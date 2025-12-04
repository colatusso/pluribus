"""
Plugins de evolucao para Pluribus.

Implementam heranca genetica, especiacao e adaptacao.
"""
import random
import numpy as np
from typing import Dict, Any, List, Set, Tuple
from .base import Plugin


class GeneticPlugin(Plugin):
    """
    Heranca genetica com mutacao.

    Quando agentes morrem, podem deixar "filhos" que herdam
    parte da policy. Mutacoes aleatorias criam variacao.

    Implementa selecao natural.
    """

    priority = 85
    dependencies: Set[str] = {"Death"}
    conflicts: Set[str] = set()

    def __init__(
        self,
        reproduction_threshold: float = 0.7,
        inheritance_factor: float = 0.8,
        mutation_rate: float = 0.1,
        mutation_strength: float = 0.2
    ):
        """
        Args:
            reproduction_threshold: Reward minimo para reproduzir (fração do max)
            inheritance_factor: Quanto do pai o filho herda
            mutation_rate: Chance de mutacao por posicao
            mutation_strength: Intensidade da mutacao
        """
        self.reproduction_threshold = reproduction_threshold
        self.inheritance_factor = inheritance_factor
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength

        self.births = 0
        self.mutations = 0
        self.generations: Dict[int, int] = {}  # agent_id -> generation

    def get_name(self) -> str:
        return "Genetic"

    def get_description(self) -> str:
        return "Heranca genetica com mutacao e selecao natural"

    def get_params(self) -> Dict[str, Any]:
        return {
            "reproduction_threshold": self.reproduction_threshold,
            "inheritance_factor": self.inheritance_factor,
            "mutation_rate": self.mutation_rate,
            "mutation_strength": self.mutation_strength
        }

    def on_simulation_start(self, runner) -> None:
        self.births = 0
        self.mutations = 0
        self.generations = {a.node_id: 0 for a in runner.agents}

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not runner.agents or not tick_rewards:
            return

        max_reward = max(tick_rewards)
        threshold = max_reward * self.reproduction_threshold

        # Identifica pais potenciais
        parents = [
            (i, a) for i, a in enumerate(runner.agents)
            if i < len(tick_rewards) and tick_rewards[i] >= threshold
        ]

        if not parents:
            return

        # Cada pai pode ter um filho (se houver espaco)
        initial_count = runner.config.num_agents
        current_count = len(runner.agents)

        for parent_idx, parent in parents:
            if current_count >= initial_count:
                break

            # Cria filho
            child = self._create_child(parent, runner)
            if child:
                runner.agents.append(child)
                current_count += 1
                self.births += 1

                # Registra geracao
                parent_gen = self.generations.get(parent.node_id, 0)
                self.generations[child.node_id] = parent_gen + 1

    def _create_child(self, parent, runner):
        """Cria filho a partir do pai"""
        from src.agents.agent import Agent
        from src.agents.strategies import get_strategy

        # Novo ID unico (usa contador global do runner)
        child_id = runner.get_next_agent_id()

        # Cria agente
        strategy = get_strategy(
            runner.config.strategy,
            runner.config.learning_rate
        )

        child = Agent(
            node_id=child_id,
            sequence_length=runner.config.sequence_length,
            alphabet_size=runner.config.alphabet_size,
            strategy=strategy,
            initial_balance=runner.config.initial_balance * 0.5,  # Comeca com menos
            cost_per_attempt=runner.config.cost_per_attempt
        )

        # Herda policy do pai
        child.P = parent.P.copy() * self.inheritance_factor
        child.P += (1 - self.inheritance_factor) * np.ones_like(child.P) / child.P.shape[1]

        # Mutacao
        for pos in range(child.P.shape[0]):
            if random.random() < self.mutation_rate:
                # Adiciona ruido
                noise = np.random.normal(0, self.mutation_strength, child.P.shape[1])
                child.P[pos] += noise
                child.P[pos] = np.maximum(child.P[pos], 0.01)
                self.mutations += 1

        # Renormaliza
        row_sums = child.P.sum(axis=1, keepdims=True)
        child.P = child.P / row_sums

        # Herda vizinhos do pai
        child.neighbors = parent.neighbors.copy()

        return child

    def get_stats(self) -> Dict[str, Any]:
        max_gen = max(self.generations.values()) if self.generations else 0
        return {
            "Nascimentos": self.births,
            "Mutacoes": self.mutations,
            "Max geracao": max_gen
        }


class SpeciationPlugin(Plugin):
    """
    Especiacao - agentes divergem em especies.

    Agentes que desenvolvem strategies muito diferentes
    formam "especies" separadas que competem entre si.
    """

    priority = 88
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        num_species: int = 3,
        divergence_rate: float = 0.1,
        competition_factor: float = 0.2
    ):
        """
        Args:
            num_species: Numero de especies
            divergence_rate: Taxa de divergencia entre especies
            competition_factor: Intensidade da competicao
        """
        self.num_species = num_species
        self.divergence_rate = divergence_rate
        self.competition_factor = competition_factor

        # Especie de cada agente
        self.species: Dict[int, int] = {}
        # Performance por especie
        self.species_performance: Dict[int, List[float]] = {}

    def get_name(self) -> str:
        return "Speciation"

    def get_description(self) -> str:
        return "Agentes divergem em especies competidoras"

    def get_params(self) -> Dict[str, Any]:
        return {
            "num_species": self.num_species,
            "divergence_rate": self.divergence_rate,
            "competition_factor": self.competition_factor
        }

    def on_simulation_start(self, runner) -> None:
        # Distribui agentes em especies
        self.species = {}
        for i, agent in enumerate(runner.agents):
            self.species[agent.node_id] = i % self.num_species

        self.species_performance = {i: [] for i in range(self.num_species)}

        # Aplica divergencia inicial nas policies
        self._apply_species_divergence(runner)

    def _apply_species_divergence(self, runner) -> None:
        """Cada especie diverge em uma direcao"""
        for agent in runner.agents:
            species_id = self.species.get(agent.node_id, 0)

            # Cada especie favorece diferentes posicoes
            for pos in range(agent.P.shape[0]):
                # Especie favorece token = (pos + species_id) % alphabet
                favored = (pos + species_id) % agent.P.shape[1]
                agent.P[pos, favored] += self.divergence_rate

            # Renormaliza
            row_sums = agent.P.sum(axis=1, keepdims=True)
            agent.P = agent.P / row_sums

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not runner.agents:
            return

        # Coleta performance por especie
        species_rewards: Dict[int, List[float]] = {i: [] for i in range(self.num_species)}

        for i, agent in enumerate(runner.agents):
            if i >= len(tick_rewards):
                continue
            species_id = self.species.get(agent.node_id, 0)
            species_rewards[species_id].append(tick_rewards[i])

        # Calcula media por especie
        for species_id, rewards in species_rewards.items():
            if rewards:
                avg = np.mean(rewards)
                self.species_performance[species_id].append(avg)

        # Aplica competicao - especies melhores "roubam" recursos das piores
        if len(self.species_performance[0]) > 0:
            self._apply_competition(runner)

    def _apply_competition(self, runner) -> None:
        """Especies melhores ganham bonus"""
        # Calcula ranking de especies
        species_avg = {}
        for species_id, perfs in self.species_performance.items():
            if perfs:
                species_avg[species_id] = np.mean(perfs[-10:])  # Ultimos 10 ticks

        if not species_avg:
            return

        best_species = max(species_avg.items(), key=lambda x: x[1])[0]
        worst_species = min(species_avg.items(), key=lambda x: x[1])[0]

        # Bonus para melhor especie
        for agent in runner.agents:
            if self.species.get(agent.node_id) == best_species:
                agent.balance += self.competition_factor * 10

    def get_stats(self) -> Dict[str, Any]:
        # Conta membros por especie
        counts = {}
        for species_id in self.species.values():
            counts[species_id] = counts.get(species_id, 0) + 1

        # Melhor especie
        if self.species_performance:
            best_species = max(
                self.species_performance.items(),
                key=lambda x: np.mean(x[1][-10:]) if x[1] else 0
            )[0]
        else:
            best_species = 0

        return {
            "Especies": self.num_species,
            "Distribuicao": str(counts),
            "Melhor especie": best_species
        }


class AdaptationPlugin(Plugin):
    """
    Parametros evoluem baseado em sucesso.

    Learning rate, gamma, epsilon mudam adaptativamente.
    Agentes que nao melhoram ficam mais "desesperados".
    """

    priority = 82
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        adaptation_rate: float = 0.1,
        desperation_threshold: int = 10,
        max_adaptation: float = 2.0
    ):
        """
        Args:
            adaptation_rate: Taxa de mudanca dos parametros
            desperation_threshold: Ticks sem melhora para desespero
            max_adaptation: Multiplicador maximo dos parametros
        """
        self.adaptation_rate = adaptation_rate
        self.desperation_threshold = desperation_threshold
        self.max_adaptation = max_adaptation

        # Ticks desde ultima melhora
        self.stagnation: Dict[int, int] = {}
        # Multiplicadores atuais
        self.multipliers: Dict[int, float] = {}

    def get_name(self) -> str:
        return "Adaptation"

    def get_description(self) -> str:
        return "Parametros evoluem baseado em sucesso/fracasso"

    def get_params(self) -> Dict[str, Any]:
        return {
            "adaptation_rate": self.adaptation_rate,
            "desperation_threshold": self.desperation_threshold,
            "max_adaptation": self.max_adaptation
        }

    def on_simulation_start(self, runner) -> None:
        self.stagnation = {a.node_id: 0 for a in runner.agents}
        self.multipliers = {a.node_id: 1.0 for a in runner.agents}

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        for i, agent in enumerate(runner.agents):
            if i >= len(tick_rewards):
                continue

            reward = tick_rewards[i]
            agent_id = agent.node_id

            # Inicializa se agente novo
            if agent_id not in self.stagnation:
                self.stagnation[agent_id] = 0
                self.multipliers[agent_id] = 1.0

            # Checa se melhorou
            if reward > agent.best_reward:
                # Melhorou - reset stagnation, reduz multiplicador
                self.stagnation[agent_id] = 0
                self.multipliers[agent_id] = max(
                    1.0,
                    self.multipliers[agent_id] * (1 - self.adaptation_rate)
                )
            else:
                # Nao melhorou - aumenta stagnation
                self.stagnation[agent_id] += 1

                # Se estagnado demais, aumenta multiplicador (desespero)
                if self.stagnation[agent_id] >= self.desperation_threshold:
                    self.multipliers[agent_id] = min(
                        self.max_adaptation,
                        self.multipliers[agent_id] * (1 + self.adaptation_rate)
                    )

            # Aplica multiplicador
            self._apply_multiplier(agent)

    def _apply_multiplier(self, agent) -> None:
        """Aplica multiplicador nos parametros"""
        mult = self.multipliers.get(agent.node_id, 1.0)

        # Aumenta learning rate
        if hasattr(agent.strategy, 'learning_rate'):
            # Base * multiplicador
            base_lr = 0.1  # Assume default
            agent.strategy.learning_rate = base_lr * mult

        # Aumenta epsilon se disponivel
        if hasattr(agent.strategy, 'epsilon'):
            base_eps = 0.1
            agent.strategy.epsilon = min(0.5, base_eps * mult)

    def get_stats(self) -> Dict[str, Any]:
        if not self.multipliers:
            return {}

        mults = list(self.multipliers.values())
        desperate = sum(1 for m in mults if m > 1.5)

        return {
            "Multiplicador medio": f"{np.mean(mults):.2f}",
            "Max multiplicador": f"{max(mults):.2f}",
            "Desesperados": desperate
        }
