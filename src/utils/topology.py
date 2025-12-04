from typing import Dict, List
import random


def create_topology(topology_type: str, num_agents: int, **kwargs) -> Dict[int, List[int]]:
    """
    Cria grafo de vizinhança para modo LOCAL.

    Args:
        topology_type: Tipo de topologia ("ring", "random", "complete")
        num_agents: Número de agentes
        **kwargs: Parâmetros adicionais por tipo

    Returns:
        Dict mapeando agent_id -> lista de vizinhos
    """
    if topology_type == "ring":
        return _create_ring(num_agents)
    elif topology_type == "random":
        k = kwargs.get("k", 3)  # número de vizinhos por nó
        return _create_random(num_agents, k)
    elif topology_type == "complete":
        return _create_complete(num_agents)
    else:
        raise ValueError(f"Topology type '{topology_type}' não suportado")


def _create_ring(num_agents: int) -> Dict[int, List[int]]:
    """Topologia em anel: cada agente tem 2 vizinhos (anterior e próximo)"""
    adjacency = {}
    for i in range(num_agents):
        prev_node = (i - 1) % num_agents
        next_node = (i + 1) % num_agents
        adjacency[i] = [prev_node, next_node]
    return adjacency


def _create_random(num_agents: int, k: int) -> Dict[int, List[int]]:
    """
    Topologia aleatória: cada agente conecta com k outros aleatórios.

    Garante grafo conexo.
    """
    adjacency = {i: [] for i in range(num_agents)}

    for i in range(num_agents):
        # Pool de possíveis vizinhos (excluindo ele mesmo)
        candidates = [j for j in range(num_agents) if j != i and j not in adjacency[i]]

        # Escolhe k vizinhos aleatórios
        num_to_pick = min(k, len(candidates))
        neighbors = random.sample(candidates, num_to_pick)

        for neighbor in neighbors:
            # Adiciona aresta bidirecional
            if neighbor not in adjacency[i]:
                adjacency[i].append(neighbor)
            if i not in adjacency[neighbor]:
                adjacency[neighbor].append(i)

    return adjacency


def _create_complete(num_agents: int) -> Dict[int, List[int]]:
    """Grafo completo: todos conectados com todos"""
    adjacency = {}
    for i in range(num_agents):
        adjacency[i] = [j for j in range(num_agents) if j != i]
    return adjacency
