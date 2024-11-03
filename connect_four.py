import numpy as np
import sys
import time
from typing import Tuple, List, Optional
import json
from datetime import datetime
import sqlite3
import uuid

class ConnectFour:
    def __init__(self, rows: int = 6, columns: int = 7, difficulty: int = 2, initial_player: str = "HUMAN"):
        # Configuración inicial del juego
        self.ROWS = rows
        self.COLUMNS = columns
        self.DIFFICULTY = difficulty  # 1: Fácil, 2: Medio, 3: Difícil
        self.PLAYER = 0
        self.AI = 1
        self.EMPTY = None
        self.WINDOW_LENGTH = 4
        self.initial_player = initial_player

        # Variables para estadísticas
        self.nodes_explored = 0
        self.thinking_time = 0

        # Profundidad de búsqueda según dificultad
        self.depth_map = {1: 2, 2: 4, 3: 6}
        self.search_depth = self.depth_map[difficulty]

        # Historial de partidas para ajuste de dificultad
        self.game_history = self.load_game_history()

        # Inicialización del tablero
        self.board = [[self.EMPTY] * columns for _ in range(rows)]

        # Inicialización de la base de datos
        self.initialize_database()

        # ID único para esta partida
        self.game_id = str(uuid.uuid4())

        # Registrar inicio de partida en la base de datos
        self.register_new_game()

    def initialize_database(self):
        """Inicializa la base de datos SQLite con las tablas necesarias"""
        self.conn = sqlite3.connect('connect_four.db')
        cursor = self.conn.cursor()

        # Crear tabla games con los nuevos campos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            game_id TEXT PRIMARY KEY,
            initial_player TEXT,
            winner_player TEXT,
            timestamp DATETIME,
            dificultad INTEGER,
            filas INTEGER,
            columnas INTEGER,
            tiempo_juego FLOAT,
            jugadas_humano INTEGER,
            jugadas_ia INTEGER,
            sugerencias_usadas INTEGER,
            tiempo_total_ia FLOAT,
            nodos_explorados INTEGER,
            promedio_tiempo_jugada_ia FLOAT,
            nivel_dificultad INTEGER
        )
        ''')

        # Crear tabla moves
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS moves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT,
            timestamp DATETIME,
            game_id TEXT,
            column INTEGER,
            help BOOLEAN,
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        )
        ''')

        self.conn.commit()

    def register_new_game(self):
        """Registra una nueva partida en la base de datos"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO games (game_id, initial_player, timestamp, dificultad, filas, columnas)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            self.game_id,
            self.initial_player,
            datetime.now(),
            self.DIFFICULTY,
            self.ROWS,
            self.COLUMNS
        ))
        self.conn.commit()

    def register_move(self, player: str, column: int, help_used: bool = False):
        """Registra un movimiento en la base de datos"""
        cursor = self.conn.cursor()
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
        self.conn.commit()

    def register_game_stats(self, stats_data: dict):
        """Registra las estadísticas finales del juego en la base de datos"""
        cursor = self.conn.cursor()
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
        self.conn.commit()

    def load_game_history(self) -> List[dict]:
        """Carga el historial de partidas desde un archivo JSON"""
        try:
            with open('game_history.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_game_history(self):
        """Guarda el historial de partidas en un archivo JSON"""
        with open('game_history.json', 'w') as f:
            json.dump(self.game_history, f)

    def is_valid_move(self, col: int) -> bool:
        """Verifica si una columna está disponible para colocar una ficha"""
        return self.board[0][col] == self.EMPTY

    def get_valid_moves(self) -> List[int]:
        """Retorna una lista de columnas disponibles"""
        return [col for col in range(self.COLUMNS) if self.is_valid_move(col)]

    def drop_piece(self, col: int, piece: int, help_used: bool = False) -> Tuple[int, int]:
        """
        Coloca una ficha en la columna especificada
        Retorna la posición (fila, columna) donde se colocó la ficha
        """
        for row in range(self.ROWS-1, -1, -1):
            if self.board[row][col] == self.EMPTY:
                self.board[row][col] = piece
                # Registrar movimiento en la base de datos
                player = "HUMAN" if piece == self.PLAYER else "AI"
                self.register_move(player, col, help_used)
                return row, col
        return -1, -1

    def check_winner(self, piece: int) -> bool:
        """Verifica si hay un ganador en el tablero actual"""
        # Verificar horizontal
        for row in range(self.ROWS):
            for col in range(self.COLUMNS - 3):
                if all(self.board[row][col+i] == piece for i in range(4)):
                    return True

        # Verificar vertical
        for row in range(self.ROWS - 3):
            for col in range(self.COLUMNS):
                if all(self.board[row+i][col] == piece for i in range(4)):
                    return True

        # Verificar diagonal positiva
        for row in range(self.ROWS - 3):
            for col in range(self.COLUMNS - 3):
                if all(self.board[row+i][col+i] == piece for i in range(4)):
                    return True

        # Verificar diagonal negativa
        for row in range(3, self.ROWS):
            for col in range(self.COLUMNS - 3):
                if all(self.board[row-i][col+i] == piece for i in range(4)):
                    return True

        return False

    def evaluate_window(self, window: List[int], piece: int) -> int:
        """Evalúa una ventana de 4 posiciones para la función de evaluación"""
        score = 0
        opp_piece = self.PLAYER if piece == self.AI else self.AI

        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(self.EMPTY) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(self.EMPTY) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(self.EMPTY) == 1:
            score -= 4

        return score

    def evaluate_position(self) -> int:
        """Evalúa el estado actual del tablero"""
        score = 0

        # Evaluar centro
        center_array = [self.board[row][self.COLUMNS//2] for row in range(self.ROWS)]
        center_count = center_array.count(self.AI)
        score += center_count * 3

        # Evaluar horizontal
        for row in range(self.ROWS):
            row_array = self.board[row]
            for col in range(self.COLUMNS - 3):
                window = row_array[col:col + self.WINDOW_LENGTH]
                score += self.evaluate_window(window, self.AI)

        # Evaluar vertical
        for col in range(self.COLUMNS):
            col_array = [self.board[row][col] for row in range(self.ROWS)]
            for row in range(self.ROWS - 3):
                window = col_array[row:row + self.WINDOW_LENGTH]
                score += self.evaluate_window(window, self.AI)

        # Evaluar diagonal positiva
        for row in range(self.ROWS - 3):
            for col in range(self.COLUMNS - 3):
                window = [self.board[row+i][col+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, self.AI)

        # Evaluar diagonal negativa
        for row in range(self.ROWS - 3):
            for col in range(self.COLUMNS - 3):
                window = [self.board[row+3-i][col+i] for i in range(self.WINDOW_LENGTH)]
                score += self.evaluate_window(window, self.AI)

        return score

    def minimax(self, depth: int, alpha: float, beta: float, maximizing_player: bool) -> Tuple[int, Optional[int]]:
        """
        Implementa el algoritmo Minimax con poda Alfa-Beta
        Retorna una tupla (valor, columna)
        """
        self.nodes_explored += 1
        valid_moves = self.get_valid_moves()

        # Verificar estados terminales
        if self.check_winner(self.AI):
            return (float('inf'), None)
        if self.check_winner(self.PLAYER):
            return (float('-inf'), None)
        if len(valid_moves) == 0:
            return (0, None)
        if depth == 0:
            return (self.evaluate_position(), None)

        if maximizing_player:
            value = float('-inf')
            column = valid_moves[0]
            for col in valid_moves:
                row, _ = self.drop_piece(col, self.AI)
                new_score = self.minimax(depth-1, alpha, beta, False)[0]
                self.board[row][col] = self.EMPTY
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value, column
        else:
            value = float('inf')
            column = valid_moves[0]
            for col in valid_moves:
                row, _ = self.drop_piece(col, self.PLAYER)
                new_score = self.minimax(depth-1, alpha, beta, True)[0]
                self.board[row][col] = self.EMPTY
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value, column

    def get_ai_move(self) -> Tuple[int, float, int]:
        """
        Obtiene la mejor jugada para la IA
        Retorna (columna, tiempo_pensado, nodos_explorados)
        """
        self.nodes_explored = 0
        start_time = time.time()

        _, column = self.minimax(
            self.search_depth,
            float('-inf'),
            float('inf'),
            True
        )

        end_time = time.time()
        thinking_time = end_time - start_time

        return column, thinking_time, self.nodes_explored

    def suggest_move(self) -> int:
        """Sugiere una jugada al jugador humano"""
        # Usa una profundidad menor para la sugerencia
        self.nodes_explored = 0
        _, column = self.minimax(2, float('-inf'), float('inf'), False)
        return column

    def adjust_difficulty(self, player_won: bool):
        """Ajusta la dificultad basándose en el resultado del juego"""
        self.game_history.append({
            'date': datetime.now().isoformat(),
            'player_won': player_won,
            'difficulty': self.DIFFICULTY
        })

        # Analizar últimas 5 partidas
        recent_games = self.game_history[-5:]
        wins = sum(1 for game in recent_games if game['player_won'])

        # Ajustar dificultad
        if wins >= 4 and self.DIFFICULTY < 3:  # Si el jugador gana mucho, aumentar dificultad
            self.DIFFICULTY += 1
        elif wins <= 1 and self.DIFFICULTY > 1:  # Si el jugador pierde mucho, reducir dificultad
            self.DIFFICULTY -= 1

        self.search_depth = self.depth_map[self.DIFFICULTY]
        self.save_game_history()

    def __del__(self):
        """Destructor para cerrar la conexión a la base de datos"""
        if hasattr(self, 'conn'):
            self.conn.close()
