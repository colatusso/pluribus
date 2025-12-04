"""
Plugins de comunicacao para Pluribus.

Implementam evolucao de linguagem e censura.
"""
import random
import numpy as np
from typing import Dict, Any, List, Set
from .base import Plugin


class LanguagePlugin(Plugin):
    """
    Evolucao de linguagem/codigo.

    Agentes desenvolvem formas mais eficientes de comunicar
    informacao. Compressao aumenta com o tempo.

    Simula evolucao de linguagem e jargao.
    """

    priority = 105
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        compression_rate: float = 0.01,
        max_compression: float = 0.5,
        learning_curve: float = 0.1
    ):
        """
        Args:
            compression_rate: Taxa de melhora na compressao por tick
            max_compression: Compressao maxima (1 = perda total, 0 = sem compressao)
            learning_curve: Velocidade de aprendizado da linguagem
        """
        self.compression_rate = compression_rate
        self.max_compression = max_compression
        self.learning_curve = learning_curve

        # Nivel de linguagem por par de agentes
        self.language_levels: Dict[tuple, float] = {}
        self.total_compression = 0.0

    def get_name(self) -> str:
        return "Language"

    def get_description(self) -> str:
        return "Evolucao de linguagem para comunicacao eficiente"

    def get_params(self) -> Dict[str, Any]:
        return {
            "compression_rate": self.compression_rate,
            "max_compression": self.max_compression,
            "learning_curve": self.learning_curve
        }

    def on_simulation_start(self, runner) -> None:
        self.language_levels = {}
        self.total_compression = 0.0

        # Inicializa niveis de linguagem entre vizinhos
        for agent in runner.agents:
            for neighbor_id in agent.neighbors:
                pair = tuple(sorted([agent.node_id, neighbor_id]))
                self.language_levels[pair] = 0.0

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not runner.agents:
            return

        # Evolui linguagem entre pares que se comunicam bem
        for agent in runner.agents:
            for neighbor_id in agent.neighbors:
                pair = tuple(sorted([agent.node_id, neighbor_id]))

                # Encontra vizinho
                neighbor = next(
                    (a for a in runner.agents if a.node_id == neighbor_id),
                    None
                )
                if not neighbor:
                    continue

                # Se ambos melhoraram, linguagem evolui
                agent_improved = agent.best_reward > 0
                neighbor_improved = neighbor.best_reward > 0

                if agent_improved and neighbor_improved:
                    self.language_levels[pair] = min(
                        self.max_compression,
                        self.language_levels.get(pair, 0) + self.compression_rate
                    )

        # Aplica compressao na comunicacao
        self._apply_language_compression(runner)

    def _apply_language_compression(self, runner) -> None:
        """Comunicacao mais eficiente com linguagem desenvolvida"""
        for agent in runner.agents:
            if not agent.neighbors:
                continue

            # Calcula nivel medio de linguagem com vizinhos
            levels = []
            for neighbor_id in agent.neighbors:
                pair = tuple(sorted([agent.node_id, neighbor_id]))
                levels.append(self.language_levels.get(pair, 0))

            avg_level = np.mean(levels) if levels else 0

            # Linguagem desenvolvida = comunicacao mais precisa
            # Adiciona ao agente como modificador
            agent._language_bonus = avg_level * self.learning_curve
            self.total_compression += avg_level

    def get_stats(self) -> Dict[str, Any]:
        if not self.language_levels:
            return {}

        levels = list(self.language_levels.values())
        avg_level = np.mean(levels) if levels else 0
        max_level = max(levels) if levels else 0

        return {
            "Nivel medio linguagem": f"{avg_level:.3f}",
            "Nivel max linguagem": f"{max_level:.3f}",
            "Pares comunicando": len(self.language_levels)
        }


class CensorshipPlugin(Plugin):
    """
    Censura de informacao.

    Alguns agentes (censores) podem bloquear a propagacao
    de informacao entre outros. Simula controle de informacao.

    Pode ajudar (bloqueando fake news) ou atrapalhar (bloqueando verdade).
    """

    priority = 110
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        censor_ratio: float = 0.1,
        block_probability: float = 0.3,
        accuracy: float = 0.6
    ):
        """
        Args:
            censor_ratio: Fracao de agentes que sao censores
            block_probability: Chance de bloquear uma comunicacao
            accuracy: Chance de bloquear corretamente (info ruim)
        """
        self.censor_ratio = censor_ratio
        self.block_probability = block_probability
        self.accuracy = accuracy

        # IDs dos censores
        self.censors: Set[int] = set()
        self.blocks = 0
        self.correct_blocks = 0
        self.incorrect_blocks = 0

    def get_name(self) -> str:
        return "Censorship"

    def get_description(self) -> str:
        return "Censores bloqueiam propagacao de informacao"

    def get_params(self) -> Dict[str, Any]:
        return {
            "censor_ratio": self.censor_ratio,
            "block_probability": self.block_probability,
            "accuracy": self.accuracy
        }

    def on_simulation_start(self, runner) -> None:
        # Seleciona censores
        num_censors = max(1, int(len(runner.agents) * self.censor_ratio))
        censor_agents = random.sample(runner.agents, num_censors)
        self.censors = {a.node_id for a in censor_agents}

        self.blocks = 0
        self.correct_blocks = 0
        self.incorrect_blocks = 0

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not runner.agents:
            return

        # Censores decidem o que bloquear
        for i, agent in enumerate(runner.agents):
            if agent.node_id not in self.censors:
                continue

            # Censor examina comunicacao dos vizinhos
            for neighbor_id in agent.neighbors:
                if random.random() > self.block_probability:
                    continue

                neighbor = next(
                    (a for a in runner.agents if a.node_id == neighbor_id),
                    None
                )
                if not neighbor:
                    continue

                # Decide se bloqueia
                neighbor_idx = next(
                    (j for j, a in enumerate(runner.agents) if a.node_id == neighbor_id),
                    None
                )
                if neighbor_idx is None or neighbor_idx >= len(tick_rewards):
                    continue

                neighbor_reward = tick_rewards[neighbor_idx]
                is_good_info = neighbor_reward >= 50  # Info "boa"

                # Censura
                self.blocks += 1

                if random.random() < self.accuracy:
                    # Censura correta - bloqueia info ruim OU deixa passar boa
                    if not is_good_info:
                        self._apply_censorship(neighbor, runner)
                        self.correct_blocks += 1
                    # Info boa passa
                else:
                    # Censura incorreta - bloqueia info boa OU deixa passar ruim
                    if is_good_info:
                        self._apply_censorship(neighbor, runner)
                        self.incorrect_blocks += 1

    def _apply_censorship(self, agent, runner) -> None:
        """Aplica censura - reduz influencia do agente"""
        # Remove temporariamente dos vizinhos de outros
        for other in runner.agents:
            if agent.node_id in other.neighbors:
                # Marca como censurado (sera ignorado na comunicacao)
                if not hasattr(other, '_censored_neighbors'):
                    other._censored_neighbors = set()
                other._censored_neighbors.add(agent.node_id)

    def get_stats(self) -> Dict[str, Any]:
        accuracy_rate = (
            self.correct_blocks / self.blocks * 100
            if self.blocks > 0 else 0
        )

        return {
            "Censores": len(self.censors),
            "Bloqueios": self.blocks,
            "Bloqueios corretos": self.correct_blocks,
            "Bloqueios incorretos": self.incorrect_blocks,
            "Precisao": f"{accuracy_rate:.0f}%"
        }
