# archivo connect_four.py

import numpy as np
import sys
import time
import logging
from datetime import datetime
import sqlite3
import uuid
from typing import Tuple, List, Optional, Dict, Any
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache

# Configurar logging específico para la lógica del juego
logging.basicConfig(
    filename='connect_four_logic.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass
class GameStats:
    """Clase para almacenar estadísticas del juego"""
    winner_player: str
    tiempo_juego: float
    jugadas_humano: int
    jugadas_ia: int
    sugerencias_usadas: int
    tiempo_total_ia: float
    nodos_explorados: int
    promedio_tiempo_jugada_ia: float
    nivel_dificultad: int

class DatabaseError(Exception):
    """Excepción personalizada para errores de base de datos"""
    pass

class ConnectFour:
    """Implementación del juego Connect Four con IA"""

    # Constantes del juego
    MIN_BOARD_SIZE = 4
    MAX_BOARD_SIZE = 8
    VALID_DIFFICULTIES = {1, 2, 3}
    MAX_GAME_HISTORY = 100
    DB_TIMEOUT = 5.0

    def __init__(self, rows: int = 6, columns: int = 7, difficulty: int = 2,
                 initial_player: str = "HUMAN", db_path: str = 'connect_four.db'):
        """
        Inicializa el juego Connect Four

        Args:
            rows: Número de filas del tablero
            columns: Número de columnas del tablero
            difficulty: Nivel de dificultad (1-3)
            initial_player: Jugador inicial ("HUMAN" o "AI")
            db_path: Ruta a la base de datos SQLite

        Raises:
            ValueError: Si los parámetros son inválidos
            DatabaseError: Si hay problemas con la base de datos
        """
        # Validar parámetros
        self._validate_parameters(rows, columns, difficulty, initial_player)

        # Configuración del juego
        self.ROWS = rows
        self.COLUMNS = columns
        self.DIFFICULTY = difficulty
        self.PLAYER = 0
        self.AI = 1
        self.EMPTY = None
        self.WINDOW_LENGTH = 4
        self.initial_player = initial_player
        self.db_path = db_path

        # Variables para estadísticas
        self.nodes_explored = 0
        self.thinking_time = 0

        # Profundidad de búsqueda según dificultad
        self.depth_map = {1: 2, 2: 4, 3: 6}
        self.search_depth = self.depth_map[difficulty]

        # Inicialización del tablero
        self.board = [[self.EMPTY] * columns for _ in range(rows)]

        # ID único para esta partida
        self.game_id = str(uuid.uuid4())

        try:
            # Inicialización de la base de datos
            self.initialize_database()
            # Registrar inicio de partida
            self.register_new_game()
            logging.info(f"Juego iniciado: ID={self.game_id}, Configuración={rows}x{columns}, Dificultad={difficulty}")
        except Exception as e:
            logging.error(f"Error al inicializar el juego: {e}")
            raise DatabaseError(f"Error al inicializar la base de datos: {e}")

    def _validate_parameters(self, rows: int, columns: int, difficulty: int,
                           initial_player: str) -> None:
        """Valida los parámetros de inicialización"""
        if not (self.MIN_BOARD_SIZE <= rows <= self.MAX_BOARD_SIZE):
            raise ValueError(f"Número de filas debe estar entre {self.MIN_BOARD_SIZE} y {self.MAX_BOARD_SIZE}")

        if not (self.MIN_BOARD_SIZE <= columns <= self.MAX_BOARD_SIZE):
            raise ValueError(f"Número de columnas debe estar entre {self.MIN_BOARD_SIZE} y {self.MAX_BOARD_SIZE}")

        if difficulty not in self.VALID_DIFFICULTIES:
            raise ValueError("Nivel de dificultad debe ser 1, 2 o 3")

        if initial_player not in {"HUMAN", "AI"}:
            raise ValueError("Jugador inicial debe ser 'HUMAN' o 'AI'")

    @contextmanager
    def get_db_connection(self):
        """Context manager para manejar la conexión a la base de datos de forma segura"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=self.DB_TIMEOUT)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            logging.error(f"Error en la base de datos: {e}")
            raise DatabaseError(f"Error al conectar con la base de datos: {e}")
        finally:
            if conn:
                conn.close()

    def initialize_database(self) -> None:
        """Inicializa la base de datos SQLite con las tablas necesarias"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                # Crear tabla games con los nuevos campos
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    game_id TEXT PRIMARY KEY,
                    initial_player TEXT NOT NULL CHECK (initial_player IN ('HUMAN', 'AI')),
                    winner_player TEXT CHECK (winner_player IN ('HUMAN', 'AI', 'EMPATE')),
                    timestamp DATETIME NOT NULL,
                    dificultad INTEGER NOT NULL CHECK (dificultad IN (1, 2, 3)),
                    filas INTEGER NOT NULL CHECK (filas BETWEEN 4 AND 8),
                    columnas INTEGER NOT NULL CHECK (columnas BETWEEN 4 AND 8),
                    tiempo_juego FLOAT,
                    jugadas_humano INTEGER DEFAULT 0,
                    jugadas_ia INTEGER DEFAULT 0,
                    sugerencias_usadas INTEGER DEFAULT 0,
                    tiempo_total_ia FLOAT DEFAULT 0,
                    nodos_explorados INTEGER DEFAULT 0,
                    promedio_tiempo_jugada_ia FLOAT DEFAULT 0,
                    nivel_dificultad INTEGER NOT NULL CHECK (nivel_dificultad IN (1, 2, 3))
                )
                ''')

                # Crear tabla moves con restricciones
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS moves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player TEXT NOT NULL CHECK (player IN ('HUMAN', 'AI')),
                    timestamp DATETIME NOT NULL,
                    game_id TEXT NOT NULL,
                    column INTEGER NOT NULL CHECK (column >= 0),
                    help BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (game_id) REFERENCES games(game_id)
                )
                ''')

                # Crear índices para optimizar consultas
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_moves_game_id ON moves(game_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_timestamp ON games(timestamp)')

                conn.commit()

        except sqlite3.Error as e:
            logging.error(f"Error al inicializar la base de datos: {e}")
            raise DatabaseError(f"Error al crear las tablas: {e}")

    def register_new_game(self) -> None:
        """Registra una nueva partida en la base de datos"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO games (
                    game_id, initial_player, timestamp, dificultad,
                    filas, columnas, nivel_dificultad
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.game_id,
                    self.initial_player,
                    datetime.now(),
                    self.DIFFICULTY,
                    self.ROWS,
                    self.COLUMNS,
                    self.DIFFICULTY
                ))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error al registrar nuevo juego: {e}")
            raise DatabaseError(f"Error al registrar el juego: {e}")

    def register_move(self, player: str, column: int, help_used: bool = False) -> None:
        """
        Registra un movimiento en la base de datos

        Args:
            player: Jugador que realiza el movimiento ("HUMAN" o "AI")
            column: Columna donde se colocó la ficha
            help_used: Si se usó la ayuda para este movimiento
        """
        if player not in {"HUMAN", "AI"}:
            raise ValueError("Jugador inválido")

        if not (0 <= column < self.COLUMNS):
            raise ValueError("Columna inválida")

        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO moves (player, timestamp, game_id, column, help)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    player,
                    datetime.now(),
                    self.game_id,
                    column,
                    help_used
                ))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error al registrar movimiento: {e}")
            raise DatabaseError(f"Error al registrar el movimiento: {e}")

    def register_game_stats(self, stats_data: Dict[str, Any]) -> None:
        """
        Registra las estadísticas finales del juego

        Args:
            stats_data: Diccionario con las estadísticas del juego
        """
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                UPDATE games
                SET winner_player = ?,
                    tiempo_juego = ?,
                    jugadas_humano = ?,
                    jugadas_ia = ?,
                    sugerencias_usadas = ?,
                    tiempo_total_ia = ?,
                    nodos_explorados = ?,
                    promedio_tiempo_jugada_ia = ?,
                    nivel_dificultad = ?
                WHERE game_id = ?
                ''', (
                    stats_data['winner'],
                    stats_data['tiempo_juego'],
                    stats_data['jugadas_humano'],
                    stats_data['jugadas_ia'],
                    stats_data['sugerencias_usadas'],
                    stats_data['tiempo_total_ia'],
                    stats_data['nodos_explorados'],
                    stats_data['promedio_tiempo_jugada_ia'],
                    stats_data['nivel_dificultad'],
                    self.game_id
                ))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error al registrar estadísticas: {e}")
            raise DatabaseError(f"Error al actualizar las estadísticas: {e}")

    @lru_cache(maxsize=1024)
    def get_valid_moves(self) -> List[int]:
        """Retorna una lista de columnas disponibles para jugar"""
        return [col for col in range(self.COLUMNS) if self.is_valid_move(col)]

    def is_valid_move(self, col: int) -> bool:
        """Verifica si una columna está disponible para colocar una ficha"""
        if not (0 <= col < self.COLUMNS):
            return False
        return self.board[0][col] == self.EMPTY

    def drop_piece(self, col: int, piece: int, help_used: bool = False) -> Tuple[int, int]:
        """
        Coloca una ficha en la columna especificada

        Args:
            col: Columna donde colocar la ficha
            piece: Jugador que coloca la ficha (PLAYER o AI)
            help_used: Si se usó la ayuda para este movimiento

        Returns:
            Tuple[int, int]: Posición (fila, columna) donde se colocó la ficha

        Raises:
            ValueError: Si la columna es inválida o está llena
        """
        if not self.is_valid_move(col):
            raise ValueError("Movimiento inválido")

        for row in range(self.ROWS-1, -1, -1):
            if self.board[row][col] == self.EMPTY:
                self.board[row][col] = piece
                # Registrar movimiento
                player = "HUMAN" if piece == self.PLAYER else "AI"
                self.register_move(player, col, help_used)
                return row, col

        raise ValueError("Columna llena")

    def check_winner(self, piece: int) -> bool:
        """
        Verifica si hay un ganador

        Args:
            piece: Jugador a verificar (PLAYER o AI)

        Returns:
            bool: True si el jugador ha ganado
        """
        # Verificar horizontal
        for row in range(self.ROWS):
            for col in range(self.COLUMNS - 3):
                window = [self.board[row][col+i] for i in range(4)]
                if len([x for x in window if x == piece]) == 4:
                    return True

        # Verificar vertical
        for row in range(self.ROWS - 3):
            for col in range(self.COLUMNS):
                window = [self.board[row+i][col] for i in range(4)]
                if len([x for x in window if x == piece]) == 4:
                    return True

        # Verificar diagonal positiva
        for row in range(self.ROWS - 3):
            for col in range(self.COLUMNS - 3):
                window = [self.board[row+i][col+i] for i in range(4)]
                if len([x for x in window if x == piece]) == 4:
                    return True

        # Verificar diagonal negativa
        for row in range(3, self.ROWS):
            for col in range(self.COLUMNS - 3):
                window = [self.board[row-i][col+i] for i in range(4)]
                if len([x for x in window if x == piece]) == 4:
                    return True

        return False

    @lru_cache(maxsize=1024)
    def evaluate_window(self, window: Tuple[Optional[int], ...], piece: int) -> int:
        """Evalúa una ventana de 4 posiciones"""
        score = 0
        opp_piece = self.PLAYER if piece == self.AI else self.AI

        piece_count = window.count(piece)
        empty_count = window.count(self.EMPTY)
        opp_count = window.count(opp_piece)

        if piece_count == 4:
            score += 100
        elif piece_count == 3 and empty_count == 1:
            score += 5
        elif piece_count == 2 and empty_count == 2:
            score += 2

        if opp_count == 3 and empty_count == 1:
            score -= 4

        return score

    def evaluate_position(self) -> int:
            """
            Evalúa el estado actual del tablero para la IA

            Returns:
                int: Puntuación del estado actual del tablero
            """
            score = 0

            # Evaluar centro (preferencia por el control del centro)
            center_array = tuple(self.board[row][self.COLUMNS//2] for row in range(self.ROWS))
            center_count = len([x for x in center_array if x == self.AI])
            score += center_count * 3

            # Evaluar horizontal
            for row in range(self.ROWS):
                row_array = self.board[row]
                for col in range(self.COLUMNS - 3):
                    window = tuple(row_array[col:col + self.WINDOW_LENGTH])
                    score += self.evaluate_window(window, self.AI)

            # Evaluar vertical
            for col in range(self.COLUMNS):
                col_array = [self.board[row][col] for row in range(self.ROWS)]
                for row in range(self.ROWS - 3):
                    window = tuple(col_array[row:row + self.WINDOW_LENGTH])
                    score += self.evaluate_window(window, self.AI)

            # Evaluar diagonal positiva
            for row in range(self.ROWS - 3):
                for col in range(self.COLUMNS - 3):
                    window = tuple(self.board[row+i][col+i] for i in range(self.WINDOW_LENGTH))
                    score += self.evaluate_window(window, self.AI)

            # Evaluar diagonal negativa
            for row in range(3, self.ROWS):
                for col in range(self.COLUMNS - 3):
                    window = tuple(self.board[row-i][col+i] for i in range(self.WINDOW_LENGTH))
                    score += self.evaluate_window(window, self.AI)

            return score

    def minimax(self, depth: int, alpha: float, beta: float, maximizing_player: bool) -> Tuple[float, Optional[int]]:
        """
        Implementa el algoritmo Minimax con poda Alfa-Beta

        Args:
            depth: Profundidad actual de búsqueda
            alpha: Valor alpha para la poda
            beta: Valor beta para la poda
            maximizing_player: True si es turno del maximizador (IA)

        Returns:
            Tuple[float, Optional[int]]: (valor de la posición, mejor columna)
        """
        self.nodes_explored += 1
        valid_moves = self.get_valid_moves()

        # Verificar estados terminales
        if self.check_winner(self.AI):
            return (float('inf'), None)
        if self.check_winner(self.PLAYER):
            return (float('-inf'), None)
        if not valid_moves:
            return (0, None)
        if depth == 0:
            return (self.evaluate_position(), None)

        if maximizing_player:
            value = float('-inf')
            column = valid_moves[0]
            for col in valid_moves:
                try:
                    row, _ = self.drop_piece(col, self.AI)
                    new_score, _ = self.minimax(depth-1, alpha, beta, False)
                    self.board[row][col] = self.EMPTY  # Deshacer movimiento

                    if new_score > value:
                        value = new_score
                        column = col
                    alpha = max(alpha, value)

                    if alpha >= beta:
                        break

                except ValueError:
                    continue

            return value, column
        else:
            value = float('inf')
            column = valid_moves[0]
            for col in valid_moves:
                try:
                    row, _ = self.drop_piece(col, self.PLAYER)
                    new_score, _ = self.minimax(depth-1, alpha, beta, True)
                    self.board[row][col] = self.EMPTY  # Deshacer movimiento

                    if new_score < value:
                        value = new_score
                        column = col
                    beta = min(beta, value)

                    if alpha >= beta:
                        break

                except ValueError:
                    continue

            return value, column

    def get_ai_move(self) -> Tuple[int, float, int]:
        """
        Obtiene la mejor jugada para la IA

        Returns:
            Tuple[int, float, int]: (columna elegida, tiempo de pensamiento, nodos explorados)

        Raises:
            RuntimeError: Si no se puede encontrar un movimiento válido
        """
        self.nodes_explored = 0
        start_time = time.time()

        try:
            _, column = self.minimax(
                self.search_depth,
                float('-inf'),
                float('inf'),
                True
            )

            if column is None:
                raise RuntimeError("No se encontró un movimiento válido")

            end_time = time.time()
            thinking_time = end_time - start_time

            return column, thinking_time, self.nodes_explored

        except Exception as e:
            logging.error(f"Error en get_ai_move: {e}")
            # Fallback: retornar el primer movimiento válido
            valid_moves = self.get_valid_moves()
            if not valid_moves:
                raise RuntimeError("No hay movimientos válidos disponibles")
            return valid_moves[0], 0.0, 0

    def suggest_move(self) -> int:
        """
        Sugiere una jugada al jugador humano

        Returns:
            int: Columna sugerida para el siguiente movimiento

        Raises:
            RuntimeError: Si no se puede generar una sugerencia
        """
        try:
            self.nodes_explored = 0
            # Usar una profundidad menor para la sugerencia
            _, column = self.minimax(2, float('-inf'), float('inf'), False)

            if column is None or not self.is_valid_move(column):
                raise RuntimeError("No se pudo generar una sugerencia válida")

            return column

        except Exception as e:
            logging.error(f"Error al generar sugerencia: {e}")
            # Fallback: sugerir el primer movimiento válido
            valid_moves = self.get_valid_moves()
            if not valid_moves:
                raise RuntimeError("No hay movimientos válidos disponibles")
            return valid_moves[0]

    def adjust_difficulty(self, player_won: bool) -> None:
        """
        Ajusta la dificultad basándose en el resultado del juego

        Args:
            player_won: True si ganó el jugador humano
        """
        try:
            # Registrar resultado en la base de datos
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                # Obtener últimas 5 partidas
                cursor.execute('''
                    SELECT winner_player
                    FROM games
                    ORDER BY timestamp DESC
                    LIMIT 5
                ''')
                recent_games = cursor.fetchall()

                # Contar victorias del jugador
                wins = sum(1 for game in recent_games if game['winner_player'] == 'HUMAN')

                # Ajustar dificultad
                if wins >= 4 and self.DIFFICULTY < 3:
                    self.DIFFICULTY += 1
                    logging.info(f"Dificultad aumentada a {self.DIFFICULTY}")
                elif wins <= 1 and self.DIFFICULTY > 1:
                    self.DIFFICULTY -= 1
                    logging.info(f"Dificultad reducida a {self.DIFFICULTY}")

                self.search_depth = self.depth_map[self.DIFFICULTY]

        except Exception as e:
            logging.error(f"Error al ajustar dificultad: {e}")
            # En caso de error, mantener la dificultad actual
            pass

    def __del__(self):
        """Destructor para asegurar la limpieza de recursos"""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
                logging.info("Conexión a la base de datos cerrada correctamente")
        except Exception as e:
            logging.error(f"Error al cerrar la conexión: {e}")
