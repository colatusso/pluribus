import numpy as np
from typing import List
from ..agents.agent import Agent


class HiveMode:
    """
    Modo HIVE: mente coletiva com conhecimento quase global.

    O melhor agente do tick propaga seu conhecimento para todos.
    """

    def __init__(self, gamma: float = 0.5):
        """
        Args:
            gamma: Intensidade da sincronização (0 = nada, 1 = cópia total)
        """
        self.gamma = gamma

    def communicate(self, agents: List[Agent], tick_rewards: List[float]):
        """
        Sincroniza conhecimento: todos aprendem com o melhor.

        Args:
            agents: Lista de agentes
            tick_rewards: Rewards do tick atual (mesmo índice que agents)
        """
        if not agents:
            return

        # Encontra melhor agente deste tick
        best_idx = np.argmax(tick_rewards)
        best_agent = agents[best_idx]
        best_P = best_agent.P.copy()

        # Propaga para todos (exceto ele mesmo)
        for i, agent in enumerate(agents):
            if i != best_idx:
                agent.merge_with(best_P, gamma=self.gamma)
