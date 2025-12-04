from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class SimulationConfig:
    """
    Configuração da simulação Pluribus.

    Nomes intuitivos para facilitar entendimento:
    - collective_sync: % de sincronização coletiva (0-100)
    - learning_strength: % de ajuste por tentativa (0-100)
    - energy: energia inicial por agente
    - energy_per_try: energia gasta por tentativa
    """

    # Parâmetros do mundo
    num_agents: int = 20
    sequence_length: int = 50
    alphabet_size: int = 10
    num_recipes: int = 3

    # Parâmetros da simulação
    num_ticks: int = 1000
    mode: Literal["hive", "local"] = "hive"

    # Parâmetros de comunicação (NOVOS NOMES)
    collective_sync: int = 50  # 0-100: % de sincronização coletiva (era gamma)
    topology_type: str = "ring"  # Para modo LOCAL
    network_density: int = 30  # 0-100: % de agentes conectados (substitui topology_k)

    # Parâmetros de aprendizado (NOVOS NOMES)
    learning_strength: int = 10  # 0-100: % de ajuste por tentativa (era learning_rate)
    strategy: str = "bandit"  # bandit, single_var, explorer

    # Energia (NOVOS NOMES - substitui economia)
    energy: int = 1000  # Energia inicial por agente (era initial_balance)
    energy_per_try: int = 1  # Energia gasta por tentativa (era cost_per_attempt)

    # Output
    log_interval: int = 10  # Loga métricas a cada N ticks
    output_file: str = "simulation_results.csv"

    # Aliases antigos para retrocompatibilidade (deprecated)
    gamma: Optional[float] = None
    learning_rate: Optional[float] = None
    topology_k: Optional[int] = None
    initial_balance: Optional[float] = None
    cost_per_attempt: Optional[float] = None

    def __post_init__(self):
        if self.mode not in ["hive", "local"]:
            raise ValueError(f"Mode deve ser 'hive' ou 'local', recebeu: {self.mode}")

        # RETROCOMPATIBILIDADE: Se usou nomes antigos, converte pra novos
        if self.gamma is not None:
            self.collective_sync = int(self.gamma * 100)
        if self.learning_rate is not None:
            self.learning_strength = int(self.learning_rate * 100)
        if self.topology_k is not None:
            # Estima network_density baseado em topology_k
            self.network_density = int((self.topology_k / self.num_agents) * 100)
        if self.initial_balance is not None:
            self.energy = int(self.initial_balance)
        if self.cost_per_attempt is not None:
            self.energy_per_try = int(self.cost_per_attempt)

        # Converte valores intuitivos para formato interno
        # gamma (0.0-1.0) = collective_sync / 100
        self.gamma = self.collective_sync / 100.0

        # learning_rate (0.0-1.0) = learning_strength / 100
        self.learning_rate = self.learning_strength / 100.0

        # topology_k calculado baseado em network_density
        self.topology_k = max(2, int(self.num_agents * self.network_density / 100))

        # Aliases para compatibilidade com código interno
        self.initial_balance = float(self.energy)
        self.cost_per_attempt = float(self.energy_per_try)

    # Factory Methods - Presets prontos para usar

    @classmethod
    def fast_hive(cls, num_agents: int = 20, sequence_length: int = 8):
        """
        Preset: Convergência rápida via mente coletiva.

        - Alta sincronização coletiva (90%)
        - Aprendizado forte (20%)
        - Energia abundante para exploração rápida
        """
        return cls(
            num_agents=num_agents,
            sequence_length=sequence_length,
            alphabet_size=4,
            num_recipes=1,
            num_ticks=500,
            mode="hive",
            collective_sync=90,  # Alta sincronização
            learning_strength=20,  # Aprendizado forte
            strategy="bandit",
            energy=500,
            energy_per_try=1,
            log_interval=10
        )

    @classmethod
    def slow_local(cls, num_agents: int = 20, sequence_length: int = 8):
        """
        Preset: Exploração local gradual.

        - Baixa sincronização (30%)
        - Aprendizado moderado (10%)
        - Rede esparsa para emergência local
        """
        return cls(
            num_agents=num_agents,
            sequence_length=sequence_length,
            alphabet_size=4,
            num_recipes=1,
            num_ticks=1000,
            mode="local",
            collective_sync=30,  # Baixa sincronização
            learning_strength=10,  # Aprendizado moderado
            network_density=20,  # Rede esparsa
            strategy="single_var",
            energy=1000,
            energy_per_try=2,
            log_interval=10
        )

    @classmethod
    def balanced(cls, num_agents: int = 20, sequence_length: int = 8):
        """
        Preset: Configuração equilibrada (DEFAULT RECOMENDADO).

        - Sincronização média (50%)
        - Aprendizado moderado (15%)
        - Funciona bem em most casos
        """
        return cls(
            num_agents=num_agents,
            sequence_length=sequence_length,
            alphabet_size=4,
            num_recipes=1,
            num_ticks=500,
            mode="hive",
            collective_sync=50,  # Meio termo
            learning_strength=15,  # Moderado
            strategy="bandit",
            energy=800,
            energy_per_try=1,
            log_interval=5
        )

    @classmethod
    def chaos(cls, num_agents: int = 30, sequence_length: int = 10):
        """
        Preset: Caos experimental (pode não convergir).

        - Baixíssima sincronização (10%)
        - Aprendizado errático
        - Para testar emergência em condições extremas
        """
        return cls(
            num_agents=num_agents,
            sequence_length=sequence_length,
            alphabet_size=6,
            num_recipes=2,
            num_ticks=2000,
            mode="local",
            collective_sync=10,  # Quase zero
            learning_strength=5,  # Muito fraco
            network_density=15,  # Rede muito esparsa
            strategy="explorer",
            energy=2000,
            energy_per_try=1,
            log_interval=20
        )
