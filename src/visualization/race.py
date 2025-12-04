"""
Visualizacao em tempo real da corrida de estrategias.
"""
import pygame
from typing import List, Dict, Optional


class RaceVisualizer:
    """
    Visualiza a corrida entre diferentes combinacoes de modo + estrategia.

    Mostra barras de progresso para cada combinacao, com gasto acumulado.
    """

    # Cores
    COLORS = {
        'bg': (30, 30, 40),
        'text': (220, 220, 220),
        'text_dim': (150, 150, 150),
        'bar_bg': (60, 60, 70),
        'winner': (255, 215, 0),  # Dourado
        # HIVE - tons de azul
        'HIVE+bandit': (70, 130, 180),
        'HIVE+single_var': (100, 149, 237),
        'HIVE+explorer': (65, 105, 225),
        # LOCAL - tons de laranja
        'LOCAL+bandit': (255, 140, 0),
        'LOCAL+single_var': (255, 165, 79),
        'LOCAL+explorer': (255, 127, 80),
    }

    def __init__(self, sequence_length: int, num_combinations: int = 6):
        """
        Args:
            sequence_length: Tamanho da sequencia (para calcular progresso)
            num_combinations: Numero de combinacoes a mostrar
        """
        self.sequence_length = sequence_length
        self.num_combinations = num_combinations

        # Estado
        self.results: List[Dict] = []
        self.winner_name: Optional[str] = None
        self.current_tick = 0
        self.max_ticks = 100
        self.running = False

        # Pygame
        self.width = 800
        self.height = 450
        self.screen = None
        self.font = None
        self.font_small = None
        self.font_title = None

    def init_pygame(self):
        """Inicializa pygame (chamado separadamente para permitir threading)"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Pluribus - Corrida de Estrategias")

        self.font = pygame.font.SysFont('Monaco', 16)
        self.font_small = pygame.font.SysFont('Monaco', 12)
        self.font_title = pygame.font.SysFont('Monaco', 24, bold=True)

        self.running = True

    def update(self, results: List[Dict]):
        """
        Atualiza estado com resultados atuais.

        Args:
            results: Lista de dicts com:
                - name: str (ex: 'HIVE+bandit')
                - best_match: int (melhor match atual)
                - spent: float (gasto acumulado)
        """
        self.results = results

    def set_winner(self, name: str):
        """Define o vencedor para destacar"""
        self.winner_name = name

    def set_tick(self, tick: int, max_ticks: int):
        """Atualiza contador de tick"""
        self.current_tick = tick
        self.max_ticks = max_ticks

    def draw(self):
        """Desenha frame atual"""
        if not self.screen:
            return

        # Background
        self.screen.fill(self.COLORS['bg'])

        # Titulo
        title = self.font_title.render("PLURIBUS - Corrida de Estrategias", True, self.COLORS['text'])
        title_rect = title.get_rect(centerx=self.width // 2, y=20)
        self.screen.blit(title, title_rect)

        # Barras
        bar_start_y = 70
        bar_height = 40
        bar_spacing = 55
        bar_x = 180
        bar_max_width = 400

        for i, result in enumerate(self.results):
            y = bar_start_y + i * bar_spacing
            name = result.get('name', f'Combo {i}')
            best_match = result.get('best_match', 0)
            spent = result.get('spent', 0)

            # Cor da barra
            bar_color = self.COLORS.get(name, (100, 100, 100))

            # E o vencedor?
            is_winner = name == self.winner_name

            # Label esquerda
            label_color = self.COLORS['winner'] if is_winner else self.COLORS['text']
            label = self.font.render(name, True, label_color)
            self.screen.blit(label, (10, y + 10))

            # Barra de fundo
            pygame.draw.rect(
                self.screen,
                self.COLORS['bar_bg'],
                (bar_x, y, bar_max_width, bar_height),
                border_radius=5
            )

            # Barra de progresso
            progress = best_match / self.sequence_length
            bar_width = int(bar_max_width * progress)
            if bar_width > 0:
                pygame.draw.rect(
                    self.screen,
                    bar_color,
                    (bar_x, y, bar_width, bar_height),
                    border_radius=5
                )

            # Borda dourada se vencedor
            if is_winner:
                pygame.draw.rect(
                    self.screen,
                    self.COLORS['winner'],
                    (bar_x - 2, y - 2, bar_max_width + 4, bar_height + 4),
                    width=3,
                    border_radius=7
                )

                # Tag WINNER
                winner_tag = self.font_small.render("WINNER", True, self.COLORS['winner'])
                self.screen.blit(winner_tag, (bar_x + bar_max_width + 80, y + 2))

            # Stats a direita
            stats_text = f"{best_match}/{self.sequence_length}  ${spent:.0f}"
            stats = self.font.render(stats_text, True, self.COLORS['text'])
            self.screen.blit(stats, (bar_x + bar_max_width + 10, y + 10))

        # Tick counter
        tick_text = f"Tick: {self.current_tick} / {self.max_ticks}"
        tick_surface = self.font.render(tick_text, True, self.COLORS['text_dim'])
        tick_rect = tick_surface.get_rect(centerx=self.width // 2, y=self.height - 40)
        self.screen.blit(tick_surface, tick_rect)

        # Instrucao se acabou
        if self.winner_name:
            hint = self.font_small.render("Pressione ESC ou feche a janela para sair", True, self.COLORS['text_dim'])
            hint_rect = hint.get_rect(centerx=self.width // 2, y=self.height - 20)
            self.screen.blit(hint, hint_rect)

        pygame.display.flip()

    def handle_events(self) -> bool:
        """
        Processa eventos do pygame.

        Returns:
            True se deve continuar, False se deve fechar
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def close(self):
        """Fecha pygame"""
        if self.running:
            pygame.quit()
            self.running = False
