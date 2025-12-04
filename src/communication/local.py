import numpy as np
from typing import List, Dict
from ..agents.agent import Agent


class LocalMode:
    """
    Modo LOCAL: cada agente só conversa com vizinhos.

    Troca conhecimento limitada à topologia de rede.
    """

    def __init__(self, adjacency: Dict[int, List[int]], gamma: float = 0.3):
        """
        Args:
            adjacency: Grafo de vizinhança (agent_id -> lista de vizinhos)
            gamma: Intensidade da sincronização
        """
        self.adjacency = adjacency
        self.gamma = gamma

    def communicate(self, agents: List[Agent], tick_rewards: List[float]):
        """
        Cada agente aprende com o melhor vizinho.

        Args:
            agents: Lista de agentes
            tick_rewards: Rewards do tick atual
        """
        if not agents:
            return

        # Mapeia agent_id -> (agent, reward)
        agent_map = {agent.node_id: (agent, tick_rewards[i]) for i, agent in enumerate(agents)}

        for agent in agents:
            agent_id = agent.node_id

            # Pega vizinhos (incluindo ele mesmo para comparação)
            neighbors = self.adjacency.get(agent_id, [])
            candidates = [agent_id] + neighbors

            # Filtra apenas vizinhos que existem
            valid_candidates = [
                nid for nid in candidates
                if nid in agent_map
            ]

            if not valid_candidates:
                continue

            # Encontra melhor vizinho
            best_neighbor_id = max(
                valid_candidates,
                key=lambda nid: agent_map[nid][1]  # ordena por reward
            )

            # Se o melhor é ele mesmo, não faz nada
            if best_neighbor_id == agent_id:
                continue

            # Merge com policy do melhor vizinho
            best_neighbor_agent = agent_map[best_neighbor_id][0]
            agent.merge_with(best_neighbor_agent.P.copy(), gamma=self.gamma)
