import pygame
import sys
import math
from typing import Optional, Tuple
import time
from connect_four import ConnectFour

class ConnectFourGUI:
    def __init__(self, game: 'ConnectFour'):
        pygame.init()
        self.game = game
        self.start_time = time.time()  # Registrar tiempo de inicio

        # Colores
        self.BLUE = (0, 0, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.GREEN = (34, 139, 34)

        # Dimensiones
        self.SQUARESIZE = 100
        self.width = self.game.COLUMNS * self.SQUARESIZE
        self.height = (self.game.ROWS + 2) * self.SQUARESIZE  # +2 para espacio extra arriba y abajo
        self.RADIUS = int(self.SQUARESIZE/2 - 5)

        # Configuración de la pantalla
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Connect Four - IA')

        # Fuentes
        self.FONT = pygame.font.SysFont("monospace", 25)
        self.FONT_SMALL = pygame.font.SysFont("monospace", 20)
        self.FONT_STATS = pygame.font.SysFont("monospace", 18)

        # Estado del juego
        self.game_over = False
        self.turn = 0 if self.game.initial_player == "HUMAN" else 1

        # Estadísticas del juego
        self.total_ai_time = 0
        self.total_ai_nodes = 0
        self.human_moves = 0
        self.ai_moves = 0
        self.suggestions_used = 0

        # Botones
        button_width = 200
        button_height = 40
        # Botón de sugerencia abajo del tablero
        self.suggest_button = pygame.Rect(
            (self.width - button_width) // 2,
            self.height - self.SQUARESIZE // 2 - button_height // 2,
            button_width,
            button_height
        )
        # Botón de cerrar (para el final del juego)
        self.close_button = pygame.Rect(
            (self.width - button_width) // 2,
            self.height - self.SQUARESIZE // 2,
            button_width,
            button_height
        )

        self.suggestion: Optional[int] = None
        self.help_used = False

    def draw_board(self):
        """Dibuja el tablero y las fichas"""
        # Limpiar pantalla
        self.screen.fill(self.WHITE)

        if not self.game_over:
            # Dibujar botón de sugerencia
            pygame.draw.rect(self.screen, self.GRAY, self.suggest_button)
            suggest_text = self.FONT_SMALL.render("Sugerir Jugada", 1, self.WHITE)
            suggest_text_rect = suggest_text.get_rect(center=self.suggest_button.center)
            self.screen.blit(suggest_text, suggest_text_rect)

        # Dibujar tablero
        for c in range(self.game.COLUMNS):
            for r in range(self.game.ROWS):
                pygame.draw.rect(self.screen, self.BLUE,
                               (c*self.SQUARESIZE,
                                (r+1)*self.SQUARESIZE,
                                self.SQUARESIZE,
                                self.SQUARESIZE))

                color = self.WHITE
                if self.game.board[r][c] == self.game.PLAYER:
                    color = self.RED
                elif self.game.board[r][c] == self.game.AI:
                    color = self.YELLOW

                pygame.draw.circle(self.screen, color,
                                 (int(c*self.SQUARESIZE + self.SQUARESIZE/2),
                                  int((r+1)*self.SQUARESIZE + self.SQUARESIZE/2)),
                                 self.RADIUS)

        # Dibujar sugerencia si existe
        if self.suggestion is not None:
            pygame.draw.circle(self.screen, self.GRAY,
                             (int(self.suggestion*self.SQUARESIZE + self.SQUARESIZE/2),
                              self.SQUARESIZE/2),
                             self.RADIUS/2)

        pygame.display.update()

    def show_stats(self, thinking_time: float, nodes: int):
        """Muestra estadísticas de la IA"""
        self.total_ai_time += thinking_time
        self.total_ai_nodes += nodes
        stats_text = f"Tiempo: {thinking_time:.2f}s | Nodos: {nodes}"
        label = self.FONT_SMALL.render(stats_text, 1, self.BLACK)
        self.screen.blit(label, (self.width - 300, 20))
        pygame.display.update()

    def show_game_over(self, winner: str):
        """Muestra mensaje de fin de juego"""
        label = self.FONT.render(f"¡{winner} ha ganado!", 1, self.BLACK)
        label_rect = label.get_rect(center=(self.width//2, 40))
        self.screen.blit(label, label_rect)
        pygame.display.update()

    def show_final_stats(self, winner: str):
        """Muestra las estadísticas finales del juego y las guarda en la base de datos"""
        # Calcular tiempo total de juego
        total_time = time.time() - self.start_time

        # Calcular promedio de tiempo por jugada IA
        avg_time_per_move = self.total_ai_time/self.ai_moves if self.ai_moves > 0 else 0

        # Preparar datos para la base de datos
        stats_data = {
            'winner': winner,
            'tiempo_juego': total_time,
            'jugadas_humano': self.human_moves,
            'jugadas_ia': self.ai_moves,
            'sugerencias_usadas': self.suggestions_used,
            'tiempo_total_ia': self.total_ai_time,
            'nodos_explorados': self.total_ai_nodes,
            'promedio_tiempo_jugada_ia': avg_time_per_move,
            'nivel_dificultad': self.game.DIFFICULTY
        }

        # Guardar estadísticas en la base de datos
        self.game.register_game_stats(stats_data)

        # Crear superficie semi-transparente para el fondo
        stats_surface = pygame.Surface((self.width, self.height))
        stats_surface.fill(self.WHITE)
        stats_surface.set_alpha(240)
        self.screen.blit(stats_surface, (0, 0))

        # Dibujar fondo del título
        title_rect = pygame.Rect(0, self.height//4 - 40, self.width, 40)
        pygame.draw.rect(self.screen, self.BLUE, title_rect)

        # Dibujar título
        title_text = self.FONT.render("Fin del Juego", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.width//2, self.height//4 - 20))
        self.screen.blit(title_text, title_rect)

        # Preparar estadísticas para mostrar
        stats = [
            f"Estadísticas del Juego:",
            f"",
            f"Ganador: {winner}",
            f"Tiempo total de juego: {total_time:.1f} segundos",
            f"Jugadas del Humano: {self.human_moves}",
            f"Jugadas de la IA: {self.ai_moves}",
            f"Sugerencias utilizadas: {self.suggestions_used}",
            f"Tiempo total de pensamiento IA: {self.total_ai_time:.1f} segundos",
            f"Nodos totales explorados: {self.total_ai_nodes}",
            f"Promedio de tiempo por jugada IA: {avg_time_per_move:.2f} segundos",
            f"Nivel de dificultad: {self.game.DIFFICULTY}",
            f""
        ]

        # Dibujar estadísticas
        y_offset = self.height//4 + 20
        for stat in stats:
            text = self.FONT_STATS.render(stat, True, self.BLACK)
            text_rect = text.get_rect(center=(self.width//2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 30

        # Dibujar botón de cerrar
        pygame.draw.rect(self.screen, self.RED, self.close_button)
        close_text = self.FONT_SMALL.render("Cerrar", True, self.WHITE)
        close_rect = close_text.get_rect(center=self.close_button.center)
        self.screen.blit(close_text, close_rect)

        pygame.display.update()

    def get_mouse_pos_column(self, pos_x: int) -> Optional[int]:
        """Convierte la posición del mouse a columna del tablero"""
        if pos_x > 0 and pos_x < self.width:
            return int(math.floor(pos_x/self.SQUARESIZE))
        return None

    def run_game(self):
        """Ejecuta el bucle principal del juego"""
        # Si la IA comienza, hacer su primera jugada
        if self.turn == 1:
            col, thinking_time, nodes = self.game.get_ai_move()
            if self.game.is_valid_move(col):
                self.game.drop_piece(col, self.game.AI, False)
                self.show_stats(thinking_time, nodes)
                self.ai_moves += 1
                self.turn = 0

        while True:
            if not self.game_over:
                self.draw_board()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.conn.close()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos_x = event.pos[0]
                    pos_y = event.pos[1]

                    if self.game_over:
                        if self.close_button.collidepoint(pos_x, pos_y):
                            self.game.conn.close()
                            sys.exit()
                    else:
                        # Verificar click en botón de sugerencia
                        if self.suggest_button.collidepoint(pos_x, pos_y):
                            self.suggestion = self.game.suggest_move()
                            self.help_used = True
                            self.suggestions_used += 1
                            continue

                        # Turno del jugador
                        if self.turn == 0:
                            col = self.get_mouse_pos_column(pos_x)
                            if col is not None and self.game.is_valid_move(col):
                                self.game.drop_piece(col, self.game.PLAYER, self.help_used)
                                self.help_used = False
                                self.suggestion = None
                                self.human_moves += 1

                                if self.game.check_winner(self.game.PLAYER):
                                    self.show_game_over("Jugador")
                                    self.game_over = True
                                    self.game.adjust_difficulty(True)
                                    self.show_final_stats("HUMAN")
                                    break

                                self.turn = 1

                elif event.type == pygame.MOUSEMOTION and not self.game_over:
                    pygame.draw.rect(self.screen, self.WHITE, (0, 0, self.width, self.SQUARESIZE))
                    pos_x = event.pos[0]
                    col = self.get_mouse_pos_column(pos_x)
                    if col is not None:
                        pygame.draw.circle(self.screen, self.RED,
                                         (int(col*self.SQUARESIZE + self.SQUARESIZE/2),
                                          int(self.SQUARESIZE/2)),
                                         self.RADIUS)
                    pygame.display.update()

            # Turno de la IA
            if not self.game_over and self.turn == 1:
                col, thinking_time, nodes = self.game.get_ai_move()

                if self.game.is_valid_move(col):
                    self.game.drop_piece(col, self.game.AI, False)
                    self.show_stats(thinking_time, nodes)
                    self.ai_moves += 1

                    if self.game.check_winner(self.game.AI):
                        self.show_game_over("IA")
                        self.game_over = True
                        self.game.adjust_difficulty(False)
                        self.show_final_stats("AI")
                        break

                    self.turn = 0

            # Verificar empate
            if not self.game_over and len(self.game.get_valid_moves()) == 0:
                self.show_game_over("Empate")
                self.game_over = True
                self.show_final_stats("EMPATE")

        # Esperar a que el jugador cierre el juego
        waiting_for_close = True
        while waiting_for_close:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.conn.close()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos_x, pos_y = event.pos
                    if self.close_button.collidepoint(pos_x, pos_y):
                        self.game.conn.close()
                        sys.exit()

def main():
    """Función principal para iniciar el juego"""
    # Solicitar configuración inicial
    print("Bienvenido a Connect Four con IA!")
    print("\nSeleccione el tamaño del tablero:")
    print("1. Normal (6x7)")
    print("2. Pequeño (5x4)")
    size_choice = input("Opción (1-2): ")

    if size_choice == "2":
        rows, columns = 5, 4
    else:
        rows, columns = 6, 7

    print("\nSeleccione el nivel de dificultad:")
    print("1. Fácil")
    print("2. Medio")
    print("3. Difícil")
    difficulty = int(input("Opción (1-3): "))

    print("\n¿Quién comienza el juego?")
    print("1. Jugador Humano")
    print("2. IA")
    initial_player = "HUMAN" if input("Opción (1-2): ") == "1" else "AI"

    # Crear instancias del juego y la interfaz
    game = ConnectFour(rows=rows, columns=columns, difficulty=difficulty, initial_player=initial_player)
    gui = ConnectFourGUI(game)

    # Iniciar el juego
    gui.run_game()

if __name__ == "__main__":
    main()
