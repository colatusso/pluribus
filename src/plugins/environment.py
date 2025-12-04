"""
Plugins de ambiente para Pluribus.

Modificam condicoes externas que afetam todos os agentes.
"""
import random
import numpy as np
from typing import Dict, Any, List, Set
from .base import Plugin


class DisasterPlugin(Plugin):
    """
    Catastrofes aleatorias que resetam parte do progresso.

    Eventos como "terremotos", "pandemias" ou "crises" podem:
    - Resetar parte da policy dos agentes
    - Reduzir balance de todos
    - Matar agentes aleatorios

    Forca adaptacao e resiliencia - agentes precisam se recuperar.
    """

    priority = 5
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        probability: float = 0.02,
        reset_factor: float = 0.3,
        balance_damage: float = 0.2,
        kill_chance: float = 0.1
    ):
        """
        Args:
            probability: Chance de desastre por tick (0-1)
            reset_factor: Quanto da policy resetar (0-1)
            balance_damage: Fracao do balance perdida (0-1)
            kill_chance: Chance de cada agente morrer no desastre (0-1)
        """
        self.probability = probability
        self.reset_factor = reset_factor
        self.balance_damage = balance_damage
        self.kill_chance = kill_chance

        self.disasters = 0
        self.total_damage = 0.0
        self.deaths_by_disaster = 0

    def get_name(self) -> str:
        return "Disaster"

    def get_description(self) -> str:
        return "Catastrofes aleatorias que resetam progresso e causam danos"

    def get_params(self) -> Dict[str, Any]:
        return {
            "probability": self.probability,
            "reset_factor": self.reset_factor,
            "balance_damage": self.balance_damage,
            "kill_chance": self.kill_chance
        }

    def on_simulation_start(self, runner) -> None:
        self.disasters = 0
        self.total_damage = 0.0
        self.deaths_by_disaster = 0

    def on_tick_start(self, runner, tick: int) -> None:
        if random.random() < self.probability:
            self._trigger_disaster(runner, tick)

    def _trigger_disaster(self, runner, tick: int) -> None:
        """Executa um desastre"""
        self.disasters += 1

        # Dano no balance de todos
        for agent in runner.agents:
            damage = agent.balance * self.balance_damage
            agent.balance -= damage
            self.total_damage += damage

        # Reset parcial da policy
        for agent in runner.agents:
            # Mistura policy atual com uniforme
            uniform = np.ones_like(agent.P) / agent.P.shape[1]
            agent.P = (1 - self.reset_factor) * agent.P + self.reset_factor * uniform

        # Mortes aleatorias
        survivors = []
        for agent in runner.agents:
            if random.random() > self.kill_chance:
                survivors.append(agent)
            else:
                self.deaths_by_disaster += 1

        runner.agents = survivors

    def get_stats(self) -> Dict[str, Any]:
        return {
            "Desastres": self.disasters,
            "Dano total": f"{self.total_damage:.0f}",
            "Mortes por desastre": self.deaths_by_disaster
        }


class SeasonPlugin(Plugin):
    """
    Sazonalidade - dificuldade varia com o tempo.

    Simula epocas boas e ruins:
    - Verao: custos menores, aprendizado mais facil
    - Inverno: custos maiores, aprendizado mais dificil

    Agentes precisam se preparar para epocas dificeis.
    """

    priority = 3
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        cycle_length: int = 100,
        cost_amplitude: float = 0.5,
        learning_amplitude: float = 0.3
    ):
        """
        Args:
            cycle_length: Ticks para completar um ciclo sazonal
            cost_amplitude: Variacao no custo (0-1, ex: 0.5 = +/-50%)
            learning_amplitude: Variacao no learning rate (0-1)
        """
        self.cycle_length = cycle_length
        self.cost_amplitude = cost_amplitude
        self.learning_amplitude = learning_amplitude

        self.current_season = "Primavera"
        self.season_history: List[str] = []

        # Guarda valores originais
        self._original_costs: Dict[int, float] = {}
        self._original_lr: Dict[int, float] = {}

    def get_name(self) -> str:
        return "Season"

    def get_description(self) -> str:
        return "Ciclos sazonais que variam custo e aprendizado"

    def get_params(self) -> Dict[str, Any]:
        return {
            "cycle_length": self.cycle_length,
            "cost_amplitude": self.cost_amplitude,
            "learning_amplitude": self.learning_amplitude
        }

    def on_simulation_start(self, runner) -> None:
        # Guarda valores originais
        for agent in runner.agents:
            self._original_costs[agent.node_id] = agent.cost_per_attempt
            if hasattr(agent.strategy, 'learning_rate'):
                self._original_lr[agent.node_id] = agent.strategy.learning_rate

        self.season_history = []

    def on_tick_start(self, runner, tick: int) -> None:
        # Calcula fase do ciclo (0 a 2*pi)
        phase = (tick % self.cycle_length) / self.cycle_length * 2 * np.pi

        # Determina estacao
        quarter = int((tick % self.cycle_length) / (self.cycle_length / 4))
        seasons = ["Primavera", "Verao", "Outono", "Inverno"]
        self.current_season = seasons[quarter]

        # Modifica custos e learning rate
        # sin varia de -1 a 1
        modifier = np.sin(phase)

        for agent in runner.agents:
            # Custo: maior no inverno, menor no verao
            original_cost = self._original_costs.get(agent.node_id, agent.cost_per_attempt)
            agent.cost_per_attempt = original_cost * (1 + modifier * self.cost_amplitude)

            # Learning rate: maior no verao, menor no inverno usando modifier system
            if hasattr(agent.strategy, 'learning_rate'):
                original_lr = self._original_lr.get(agent.node_id, agent.strategy.learning_rate)
                season_mult = 1.0 - modifier * self.learning_amplitude
                lr_modifier = agent.modifiers.get_modifier('learning_rate', original_lr)
                lr_modifier.set_multiplier('season', season_mult)

        self.season_history.append(self.current_season)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "Estacao final": self.current_season,
            "Ciclos completos": len(self.season_history) // self.cycle_length
        }


class MigrationPlugin(Plugin):
    """
    Migracao - agentes podem mudar de regiao (vizinhos).

    Agentes insatisfeitos (baixo progresso) migram buscando
    vizinhos melhores. Afeta topologia da rede.

    So funciona em modo LOCAL.
    """

    priority = 10
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()
    requires_mode: str = "local"  # Novo: modo requerido

    def __init__(
        self,
        migration_threshold: float = 0.3,
        migration_chance: float = 0.1
    ):
        """
        Args:
            migration_threshold: Agentes com reward < threshold * best migram
            migration_chance: Chance de migrar quando insatisfeito
        """
        self.migration_threshold = migration_threshold
        self.migration_chance = migration_chance

        self.migrations = 0

    def get_name(self) -> str:
        return "Migration"

    def get_description(self) -> str:
        return "Agentes insatisfeitos migram para novos vizinhos"

    def get_params(self) -> Dict[str, Any]:
        return {
            "migration_threshold": self.migration_threshold,
            "migration_chance": self.migration_chance
        }

    def on_simulation_start(self, runner) -> None:
        self.migrations = 0

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if not runner.agents or runner.config.mode != "local":
            return

        best_reward = max(tick_rewards) if tick_rewards else 0

        for i, agent in enumerate(runner.agents):
            reward = tick_rewards[i] if i < len(tick_rewards) else 0

            # Checa se insatisfeito
            if reward < best_reward * self.migration_threshold:
                if random.random() < self.migration_chance:
                    self._migrate_agent(agent, runner)

    def _migrate_agent(self, agent, runner) -> None:
        """Migra agente para novos vizinhos aleatorios"""
        all_ids = [a.node_id for a in runner.agents if a.node_id != agent.node_id]
        if len(all_ids) < 2:
            return

        # Escolhe novos vizinhos aleatorios
        num_neighbors = min(len(agent.neighbors), len(all_ids))
        if num_neighbors > 0:
            agent.neighbors = random.sample(all_ids, num_neighbors)
            self.migrations += 1

    def get_stats(self) -> Dict[str, Any]:
        return {
            "Migracoes": self.migrations
        }


class PollutionPlugin(Plugin):
    """
    Poluicao - tentativas erradas poluem o espaco de busca.

    Cada erro "polui" certas posicoes/tokens, tornando mais dificil
    para TODOS os agentes acertarem essas combinacoes.

    Simula degradacao ambiental coletiva.
    """

    priority = 8
    dependencies: Set[str] = set()
    conflicts: Set[str] = set()

    def __init__(
        self,
        pollution_rate: float = 0.01,
        decay_rate: float = 0.005,
        max_pollution: float = 0.5
    ):
        """
        Args:
            pollution_rate: Quanto cada erro polui (0-1)
            decay_rate: Quanto a poluicao diminui por tick
            max_pollution: Poluicao maxima por posicao
        """
        self.pollution_rate = pollution_rate
        self.decay_rate = decay_rate
        self.max_pollution = max_pollution

        # Matriz de poluicao [posicao][token]
        self.pollution_matrix = None
        self.total_pollution = 0.0

    def get_name(self) -> str:
        return "Pollution"

    def get_description(self) -> str:
        return "Erros poluem o espaco de busca para todos"

    def get_params(self) -> Dict[str, Any]:
        return {
            "pollution_rate": self.pollution_rate,
            "decay_rate": self.decay_rate,
            "max_pollution": self.max_pollution
        }

    def on_simulation_start(self, runner) -> None:
        seq_len = runner.config.sequence_length
        alphabet = runner.config.alphabet_size
        self.pollution_matrix = np.zeros((seq_len, alphabet))
        self.total_pollution = 0.0

    def on_tick_end(self, runner, tick: int, tick_rewards: List[float]) -> None:
        if self.pollution_matrix is None:
            return

        # Adiciona poluicao dos erros
        for i, agent in enumerate(runner.agents):
            if i >= len(tick_rewards):
                continue

            reward = tick_rewards[i]
            if reward < 100.0 and agent.history:
                # Ultima sequencia tentada
                seq, _ = agent.history[-1]

                # Polui posicoes erradas (nao sabemos quais, entao polui tudo um pouco)
                error_rate = (100.0 - reward) / 100.0
                for pos, token in enumerate(seq):
                    pollution = self.pollution_rate * error_rate
                    self.pollution_matrix[pos, token] = min(
                        self.pollution_matrix[pos, token] + pollution,
                        self.max_pollution
                    )

        # Decay natural
        self.pollution_matrix *= (1 - self.decay_rate)

        # Aplica poluicao nas policies (reduz probabilidade de areas poluidas)
        for agent in runner.agents:
            # Penaliza areas poluidas
            penalty = 1 - self.pollution_matrix
            agent.P = agent.P * penalty

            # Renormaliza
            row_sums = agent.P.sum(axis=1, keepdims=True)
            row_sums = np.where(row_sums == 0, 1, row_sums)
            agent.P = agent.P / row_sums

        self.total_pollution = self.pollution_matrix.sum()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "Poluicao total": f"{self.total_pollution:.2f}",
            "Poluicao media": f"{self.total_pollution / self.pollution_matrix.size:.4f}" if self.pollution_matrix is not None else "0"
        }
