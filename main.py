# archivo main.py

import pygame
import sys
import math
import time
import logging
from typing import Optional, Tuple
from connect_four import ConnectFour

# Configurar logging
logging.basicConfig(
    filename='connect_four.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GameError(Exception):
    """Clase personalizada para errores del juego"""
    pass

class ConnectFourGUI:
    """Clase para la interfaz gráfica del juego"""

    # Constantes del juego
    COLORS = {
        'BLUE': (0, 0, 255),
        'BLACK': (0, 0, 0),
        'RED': (255, 0, 0),
        'YELLOW': (255, 255, 0),
        'WHITE': (255, 255, 255),
        'GRAY': (128, 128, 128),
        'GREEN': (34, 139, 34)
    }

    MOVE_TIMEOUT = 30  # Tiempo máximo por movimiento en segundos

    def __init__(self, game: 'ConnectFour'):
        """
        Inicializa la interfaz gráfica del juego

        Args:
            game: Instancia de ConnectFour

        Raises:
            GameError: Si hay un error al inicializar pygame
        """
        try:
            pygame.init()
        except pygame.error as e:
            logging.error(f"Error al inicializar pygame: {e}")
            raise GameError("No se pudo inicializar el juego") from e

        self.game = game
        self.start_time = time.time()

        # Dimensiones
        self.SQUARESIZE = 100
        self.width = self.game.COLUMNS * self.SQUARESIZE
        self.height = (self.game.ROWS + 2) * self.SQUARESIZE
        self.RADIUS = int(self.SQUARESIZE/2 - 5)

        # Validar dimensiones
        if not (300 <= self.width <= 1920 and 300 <= self.height <= 1080):
            raise GameError("Dimensiones de ventana inválidas")

        try:
            # Configuración de la pantalla
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption('Connect Four - IA')

            # Fuentes
            self.FONT = pygame.font.SysFont("monospace", 25)
            self.FONT_SMALL = pygame.font.SysFont("monospace", 20)
            self.FONT_STATS = pygame.font.SysFont("monospace", 18)
        except pygame.error as e:
            logging.error(f"Error al configurar la pantalla: {e}")
            raise GameError("Error al configurar la interfaz gráfica")

        # Estado del juego
        self.game_over = False
        self.turn = 0 if self.game.initial_player == "HUMAN" else 1

        # Estadísticas
        self.stats = {
            'total_ai_time': 0,
            'total_ai_nodes': 0,
            'human_moves': 0,
            'ai_moves': 0,
            'suggestions_used': 0
        }

        # Configurar botones
        self._setup_buttons()

        self.suggestion: Optional[int] = None
        self.help_used = False
        self.last_move_time = time.time()

    def _setup_buttons(self):
        """Configura los botones de la interfaz"""
        button_width = 200
        button_height = 40

        # Botón de sugerencia
        self.suggest_button = pygame.Rect(
            (self.width - button_width) // 2,
            self.height - self.SQUARESIZE // 2 - button_height // 2,
            button_width,
            button_height
        )

        # Botón de cerrar
        self.close_button = pygame.Rect(
            (self.width - button_width) // 2,
            self.height - self.SQUARESIZE // 2,
            button_width,
            button_height
        )

    def draw_board(self):
        """Dibuja el tablero y las fichas"""
        try:
            # Limpiar pantalla
            self.screen.fill(self.COLORS['WHITE'])

            if not self.game_over:
                # Dibujar botón de sugerencia
                pygame.draw.rect(self.screen, self.COLORS['GRAY'], self.suggest_button)
                suggest_text = self.FONT_SMALL.render("Sugerir Jugada", 1, self.COLORS['WHITE'])
                suggest_text_rect = suggest_text.get_rect(center=self.suggest_button.center)
                self.screen.blit(suggest_text, suggest_text_rect)

            # Dibujar tablero
            for c in range(self.game.COLUMNS):
                for r in range(self.game.ROWS):
                    pygame.draw.rect(
                        self.screen,
                        self.COLORS['BLUE'],
                        (c*self.SQUARESIZE, (r+1)*self.SQUARESIZE, self.SQUARESIZE, self.SQUARESIZE)
                    )

                    color = self.COLORS['WHITE']
                    if self.game.board[r][c] == self.game.PLAYER:
                        color = self.COLORS['RED']
                    elif self.game.board[r][c] == self.game.AI:
                        color = self.COLORS['YELLOW']

                    pygame.draw.circle(
                        self.screen,
                        color,
                        (int(c*self.SQUARESIZE + self.SQUARESIZE/2),
                         int((r+1)*self.SQUARESIZE + self.SQUARESIZE/2)),
                        self.RADIUS
                    )

            # Dibujar sugerencia
            if self.suggestion is not None:
                pygame.draw.circle(
                    self.screen,
                    self.COLORS['GRAY'],
                    (int(self.suggestion*self.SQUARESIZE + self.SQUARESIZE/2),
                     self.SQUARESIZE/2),
                    self.RADIUS/2
                )

            pygame.display.update()

        except pygame.error as e:
            logging.error(f"Error al dibujar el tablero: {e}")
            raise GameError("Error al actualizar la pantalla")

    def show_stats(self, thinking_time: float, nodes: int):
        """Muestra estadísticas de la IA"""
        try:
            self.stats['total_ai_time'] += thinking_time
            self.stats['total_ai_nodes'] += nodes
            stats_text = f"Tiempo: {thinking_time:.2f}s | Nodos: {nodes}"
            label = self.FONT_SMALL.render(stats_text, 1, self.COLORS['BLACK'])
            self.screen.blit(label, (self.width - 300, 20))
            pygame.display.update()
        except Exception as e:
            logging.error(f"Error al mostrar estadísticas: {e}")

    def show_game_over(self, winner: str):
        """Muestra mensaje de fin de juego"""
        try:
            label = self.FONT.render(f"¡{winner} ha ganado!", 1, self.COLORS['BLACK'])
            label_rect = label.get_rect(center=(self.width//2, 40))
            self.screen.blit(label, label_rect)
            pygame.display.update()
            logging.info(f"Juego terminado. Ganador: {winner}")
        except Exception as e:
            logging.error(f"Error al mostrar fin de juego: {e}")

    def check_move_timeout(self) -> bool:
        """Verifica si se ha excedido el tiempo límite para un movimiento"""
        current_time = time.time()
        if current_time - self.last_move_time > self.MOVE_TIMEOUT:
            logging.warning("Tiempo de movimiento excedido")
            return True
        return False

    def get_mouse_pos_column(self, pos_x: int) -> Optional[int]:
        """Convierte la posición del mouse a columna del tablero"""
        if 0 <= pos_x < self.width:
            return int(math.floor(pos_x/self.SQUARESIZE))
        return None

    def show_final_stats(self, winner: str):
        """
        Muestra las estadísticas finales del juego y las guarda en la base de datos

        Args:
            winner: Identificador del ganador ("HUMAN", "AI", o "EMPATE")
        """
        try:
            # Calcular tiempo total de juego
            total_time = time.time() - self.start_time

            # Calcular promedio de tiempo por jugada IA
            avg_time_per_move = self.stats['total_ai_time']/self.stats['ai_moves'] if self.stats['ai_moves'] > 0 else 0

            # Preparar datos para la base de datos
            stats_data = {
                'winner': winner,
                'tiempo_juego': total_time,
                'jugadas_humano': self.stats['human_moves'],
                'jugadas_ia': self.stats['ai_moves'],
                'sugerencias_usadas': self.stats['suggestions_used'],
                'tiempo_total_ia': self.stats['total_ai_time'],
                'nodos_explorados': self.stats['total_ai_nodes'],
                'promedio_tiempo_jugada_ia': avg_time_per_move,
                'nivel_dificultad': self.game.DIFFICULTY
            }

            # Guardar estadísticas en la base de datos
            try:
                self.game.register_game_stats(stats_data)
            except Exception as e:
                logging.error(f"Error al registrar estadísticas en BD: {e}")
                # Continuar con la visualización aunque falle el registro

            # Crear superficie semi-transparente para el fondo
            stats_surface = pygame.Surface((self.width, self.height))
            stats_surface.fill(self.COLORS['WHITE'])
            stats_surface.set_alpha(240)
            self.screen.blit(stats_surface, (0, 0))

            # Dibujar fondo del título
            title_rect = pygame.Rect(0, self.height//4 - 40, self.width, 40)
            pygame.draw.rect(self.screen, self.COLORS['BLUE'], title_rect)

            # Dibujar título
            title_text = self.FONT.render("Fin del Juego", True, self.COLORS['WHITE'])
            title_rect = title_text.get_rect(center=(self.width//2, self.height//4 - 20))
            self.screen.blit(title_text, title_rect)

            # Preparar estadísticas para mostrar
            stats = [
                f"Estadísticas del Juego:",
                f"",
                f"Ganador: {winner}",
                f"Tiempo total de juego: {total_time:.1f} segundos",
                f"Jugadas del Humano: {self.stats['human_moves']}",
                f"Jugadas de la IA: {self.stats['ai_moves']}",
                f"Sugerencias utilizadas: {self.stats['suggestions_used']}",
                f"Tiempo total de pensamiento IA: {self.stats['total_ai_time']:.1f} segundos",
                f"Nodos totales explorados: {self.stats['total_ai_nodes']}",
                f"Promedio de tiempo por jugada IA: {avg_time_per_move:.2f} segundos",
                f"Nivel de dificultad: {self.game.DIFFICULTY}",
                f""
            ]

            # Dibujar estadísticas
            y_offset = self.height//4 + 20
            for stat in stats:
                text = self.FONT_STATS.render(stat, True, self.COLORS['BLACK'])
                text_rect = text.get_rect(center=(self.width//2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 30

            # Dibujar botón de cerrar
            pygame.draw.rect(self.screen, self.COLORS['RED'], self.close_button)
            close_text = self.FONT_SMALL.render("Cerrar", True, self.COLORS['WHITE'])
            close_rect = close_text.get_rect(center=self.close_button.center)
            self.screen.blit(close_text, close_rect)

            pygame.display.update()

        except Exception as e:
            logging.error(f"Error al mostrar estadísticas finales: {e}")
            # No propagar el error para permitir que el juego termine correctamente

    def run_game(self):
        """Ejecuta el bucle principal del juego"""
        try:
            # Si la IA comienza, hacer su primera jugada
            if self.turn == 1:
                col, thinking_time, nodes = self.game.get_ai_move()
                if self.game.is_valid_move(col):
                    self.game.drop_piece(col, self.game.AI, False)
                    self.show_stats(thinking_time, nodes)
                    self.stats['ai_moves'] += 1
                    self.turn = 0
                    self.last_move_time = time.time()

            while True:
                if not self.game_over:
                    self.draw_board()

                    # Verificar timeout
                    if self.check_move_timeout():
                        self.game_over = True
                        winner = "IA" if self.turn == 0 else "Jugador"
                        self.show_game_over(f"{winner} (por tiempo)")
                        self.show_final_stats(winner.upper())
                        break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.cleanup()
                        return

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self._handle_mouse_click(event.pos)
                        if self.game_over:  # Si el juego terminó después de procesar el click
                            continue  # Mantener el bucle para mostrar estadísticas

                    elif event.type == pygame.MOUSEMOTION and not self.game_over:
                        self._handle_mouse_motion(event.pos)

                # Turno de la IA
                if not self.game_over and self.turn == 1:
                    try:
                        col, thinking_time, nodes = self.game.get_ai_move()
                        if self.game.is_valid_move(col):
                            self.game.drop_piece(col, self.game.AI, False)
                            self.show_stats(thinking_time, nodes)
                            self.stats['ai_moves'] += 1
                            self.last_move_time = time.time()

                            if self.game.check_winner(self.game.AI):
                                self.show_game_over("IA")
                                self.game_over = True
                                self.game.adjust_difficulty(False)
                                self.show_final_stats("AI")
                                continue  # Mantener el bucle para mostrar estadísticas
                            else:
                                self.turn = 0
                    except Exception as e:
                        logging.error(f"Error en turno de IA: {e}")
                        self.cleanup()
                        raise

                # Verificar empate
                if not self.game_over and len(self.game.get_valid_moves()) == 0:
                    self.show_game_over("Empate")
                    self.game_over = True
                    self.show_final_stats("EMPATE")

                # Si el juego terminó, esperar a que el jugador cierre la ventana
                if self.game_over:
                    waiting_for_close = True
                    while waiting_for_close:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                self.cleanup()
                                return
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                pos_x, pos_y = event.pos
                                if self.close_button.collidepoint(pos_x, pos_y):
                                    self.cleanup()
                                    return

        except Exception as e:
            logging.error(f"Error en el bucle principal: {str(e)}")
            self.cleanup()
            raise GameError("Error durante la ejecución del juego")

    def _handle_mouse_click(self, pos):
        """Maneja los clicks del mouse"""
        pos_x, pos_y = pos

        if self.game_over:
            if self.close_button.collidepoint(pos_x, pos_y):
                self.cleanup()
                sys.exit()
        else:
            # Verificar click en botón de sugerencia
            if self.suggest_button.collidepoint(pos_x, pos_y):
                self.suggestion = self.game.suggest_move()
                self.help_used = True
                self.stats['suggestions_used'] += 1
                return

            # Turno del jugador
            if self.turn == 0:
                col = self.get_mouse_pos_column(pos_x)
                if col is not None and self.game.is_valid_move(col):
                    self._handle_player_move(col)

    def _handle_mouse_motion(self, pos):
        """Maneja el movimiento del mouse"""
        try:
            pygame.draw.rect(self.screen, self.COLORS['WHITE'], (0, 0, self.width, self.SQUARESIZE))
            pos_x = pos[0]
            col = self.get_mouse_pos_column(pos_x)
            if col is not None:
                pygame.draw.circle(
                    self.screen,
                    self.COLORS['RED'],
                    (int(col*self.SQUARESIZE + self.SQUARESIZE/2), int(self.SQUARESIZE/2)),
                    self.RADIUS
                )
            pygame.display.update()
        except pygame.error as e:
            logging.error(f"Error al manejar movimiento del mouse: {e}")

    def _handle_player_move(self, col: int):
        """Maneja el movimiento del jugador"""
        self.game.drop_piece(col, self.game.PLAYER, self.help_used)
        self.help_used = False
        self.suggestion = None
        self.stats['human_moves'] += 1
        self.last_move_time = time.time()

        if self.game.check_winner(self.game.PLAYER):
            self.show_game_over("Jugador")
            self.game_over = True
            self.game.adjust_difficulty(True)
            self.show_final_stats("HUMAN")
        else:
            self.turn = 1

    def _handle_ai_turn(self):
        """Maneja el turno de la IA"""
        col, thinking_time, nodes = self.game.get_ai_move()

        if self.game.is_valid_move(col):
            self.game.drop_piece(col, self.game.AI, False)
            self.show_stats(thinking_time, nodes)
            self.stats['ai_moves'] += 1
            self.last_move_time = time.time()

            if self.game.check_winner(self.game.AI):
                self.show_game_over("IA")
                self.game_over = True
                self.game.adjust_difficulty(False)
                self.show_final_stats("AI")
            else:
                self.turn = 0

    def cleanup(self):
        """Limpia los recursos antes de cerrar"""
        try:
            if hasattr(self.game, 'conn'):
                self.game.conn.close()
            pygame.quit()
        except Exception as e:
            logging.error(f"Error durante la limpieza: {e}")

def validate_input(prompt: str, min_val: int, max_val: int, error_msg: str = None) -> int:
    """
    Valida la entrada del usuario asegurando que sea un número dentro del rango esperado.

    Args:
        prompt: Mensaje para mostrar al usuario
        min_val: Valor mínimo aceptable
        max_val: Valor máximo aceptable
        error_msg: Mensaje de error personalizado

    Returns:
        int: Valor numérico validado

    Raises:
        ValueError: Si la entrada no es válida después de varios intentos
    """
    MAX_ATTEMPTS = 3
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        try:
            value = input(prompt).strip()
            if not value:
                raise ValueError("La entrada no puede estar vacía")

            num = int(value)
            if min_val <= num <= max_val:
                return num
            else:
                print(error_msg or f"Por favor ingrese un número entre {min_val} y {max_val}")

        except ValueError:
            print(error_msg or f"Por favor ingrese un número válido entre {min_val} y {max_val}")

        attempts += 1

    raise ValueError("Demasiados intentos fallidos. Reinicie el juego.")

def validate_config(rows: int, columns: int, difficulty: int) -> bool:
    """
    Valida la configuración del juego

    Args:
        rows: Número de filas del tablero
        columns: Número de columnas del tablero
        difficulty: Nivel de dificultad

    Returns:
        bool: True si la configuración es válida

    Raises:
        ValueError: Si la configuración no es válida
    """
    if not (4 <= rows <= 8):
        raise ValueError("Número de filas inválido")
    if not (4 <= columns <= 8):
        raise ValueError("Número de columnas inválido")
    if difficulty not in (1, 2, 3):
        raise ValueError("Nivel de dificultad inválido")
    return True

def main():
    """Función principal para iniciar el juego con validación de entradas"""
    try:
        print("Bienvenido a Connect Four con IA!")
        logging.info("Iniciando nuevo juego")

        # Validación del tamaño del tablero
        print("\nSeleccione el tamaño del tablero:")
        print("1. Normal (6x7)")
        print("2. Pequeño (5x4)")

        size_choice = validate_input(
            "Opción (1-2): ",
            1,
            2,
            "Error: Seleccione 1 para tablero normal o 2 para tablero pequeño"
        )

        # Establecer dimensiones según la elección
        if size_choice == 2:
            rows, columns = 5, 4
        else:
            rows, columns = 6, 7

        # Validación de la dificultad
        print("\nSeleccione el nivel de dificultad:")
        print("1. Fácil")
        print("2. Medio")
        print("3. Difícil")

        difficulty = validate_input(
            "Opción (1-3): ",
            1,
            3,
            "Error: Seleccione un nivel de dificultad válido (1-3)"
        )

        # Validación del jugador inicial
        print("\n¿Quién comienza el juego?")
        print("1. Jugador Humano")
        print("2. IA")

        player_choice = validate_input(
            "Opción (1-2): ",
            1,
            2,
            "Error: Seleccione 1 para jugador humano o 2 para IA"
        )

        initial_player = "HUMAN" if player_choice == 1 else "AI"

        # Validar configuración
        if not validate_config(rows, columns, difficulty):
            raise ValueError("Configuración inválida del juego")

        # Crear instancias del juego y la interfaz con manejo de excepciones
        try:
            logging.info(f"Iniciando juego con configuración: {rows}x{columns}, dificultad={difficulty}")
            game = ConnectFour(
                rows=rows,
                columns=columns,
                difficulty=difficulty,
                initial_player=initial_player
            )
            gui = ConnectFourGUI(game)
            gui.run_game()

        except Exception as e:
            logging.error(f"Error al iniciar el juego: {str(e)}")
            print(f"Error al iniciar el juego: {str(e)}")
            sys.exit(1)

    except KeyboardInterrupt:
        logging.info("Juego interrumpido por el usuario")
        print("\nJuego interrumpido por el usuario")
        sys.exit(0)

    except ValueError as ve:
        logging.error(f"Error de validación: {str(ve)}")
        print(f"\nError: {str(ve)}")
        sys.exit(1)

    except Exception as e:
        logging.error(f"Error inesperado: {str(e)}")
        print(f"\nError inesperado: {str(e)}")
        sys.exit(1)

    finally:
        # Asegurar que la conexión a la base de datos se cierre correctamente
        try:
            if 'game' in locals() and hasattr(game, 'conn'):
                game.conn.close()
                logging.info("Conexión a la base de datos cerrada correctamente")
        except Exception as e:
            logging.error(f"Error al cerrar la conexión a la base de datos: {str(e)}")

if __name__ == "__main__":
    main()
