from typing import Dict, List, Optional
import random


def create_topology(
    topology_type: str,
    num_agents: int,
    agent_ids: Optional[List[int]] = None,
    **kwargs,
) -> Dict[int, List[int]]:
    """
    Cria grafo de vizinhanca.

    Args:
        topology_type: "ring", "random" ou "complete"
        num_agents: Numero de agentes
        agent_ids: IDs reais dos agentes. Se None, usa 0..N-1 (legado).
        **kwargs: parametros por tipo (ex: k para "random")

    Returns:
        Dict mapeando agent_id -> lista de vizinhos
    """
    ids = agent_ids if agent_ids is not None else list(range(num_agents))
    if len(ids) != num_agents:
        raise ValueError(
            f"agent_ids tem {len(ids)} elementos mas num_agents={num_agents}"
        )

    if topology_type == "ring":
        return _create_ring(ids)
    elif topology_type == "random":
        k = kwargs.get("k", 3)
        return _create_random(ids, k)
    elif topology_type == "complete":
        return _create_complete(ids)
    else:
        raise ValueError(f"Topology type '{topology_type}' nao suportado")


def _create_ring(ids: List[int]) -> Dict[int, List[int]]:
    n = len(ids)
    adjacency: Dict[int, List[int]] = {}
    for i, node in enumerate(ids):
        adjacency[node] = [ids[(i - 1) % n], ids[(i + 1) % n]]
    return adjacency


def _create_random(ids: List[int], k: int) -> Dict[int, List[int]]:
    """Topologia aleatoria: cada agente conecta com k outros."""
    adjacency: Dict[int, List[int]] = {node: [] for node in ids}

    for node in ids:
        candidates = [other for other in ids if other != node and other not in adjacency[node]]
        num_to_pick = min(k, len(candidates))
        neighbors = random.sample(candidates, num_to_pick)

        for nb in neighbors:
            if nb not in adjacency[node]:
                adjacency[node].append(nb)
            if node not in adjacency[nb]:
                adjacency[nb].append(node)

    return adjacency


def _create_complete(ids: List[int]) -> Dict[int, List[int]]:
    return {node: [other for other in ids if other != node] for node in ids}
