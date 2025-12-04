"""
Plugin de morte de agentes.

Agentes que ficam sem creditos sao removidos da simulacao.
"""
from typing import Dict, Any, List
from .base import Plugin


class DeathPlugin(Plugin):
    """
    Remove agentes que ficam com balance <= 0.

    Coleta estatisticas de mortalidade.
    """

    def __init__(self):
        self.initial_count = 0
        self.deaths = 0
        self.death_ticks: List[int] = []  # Tick de cada morte

    def get_name(self) -> str:
        return "Death"

    def on_simulation_start(self, runner) -> None:
        self.initial_count = len(runner.agents)
        self.deaths = 0
        self.death_ticks = []

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        # Encontra agentes que morreram
        dead_agents = [a for a in runner.agents if a.balance <= 0]

        for agent in dead_agents:
            runner.agents.remove(agent)
            self.deaths += 1
            self.death_ticks.append(tick)

        # Atualiza comunicacao se necessario (vizinhos mudaram)
        if dead_agents and hasattr(runner.comm_mode, 'update_agents'):
            runner.comm_mode.update_agents(runner.agents)

    def get_stats(self) -> Dict[str, Any]:
        final_count = self.initial_count - self.deaths
        survival_rate = (final_count / self.initial_count * 100) if self.initial_count > 0 else 0

        stats = {
            "Agentes iniciais": self.initial_count,
            "Agentes finais": final_count,
            "Mortes": self.deaths,
            "Taxa sobrevivencia": f"{survival_rate:.0f}%"
        }

        if self.death_ticks:
            stats["Primeira morte"] = f"tick {min(self.death_ticks)}"
            stats["Ultima morte"] = f"tick {max(self.death_ticks)}"

        return stats
