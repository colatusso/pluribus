from typing import List, Optional
from multiprocessing import Pool, cpu_count
import numpy as np

from ..core.world import World
from ..agents.agent import Agent
from ..agents.strategies import get_strategy
from ..communication.hive import HiveMode
from ..communication.local import LocalMode
from ..utils.topology import create_topology
from ..plugins.base import Plugin
from .config import SimulationConfig
from .metrics import Metrics


def _agent_tick_worker(args):
    """
    Worker function para processar um agente em paralelo.

    Args:
        args: (agent, world)

    Returns:
        (agent, sequence, reward)
    """
    agent, world = args

    # Gera sequência
    sequence = agent.sample_sequence()

    # Valida no mundo
    reward = world.validate(sequence)

    # Atualiza policy
    agent.update_policy(sequence, reward)

    return agent, sequence, reward


class SimulationRunner:
    """
    Orquestra a simulação completa.

    Gerencia agentes, mundo, comunicação e coleta de métricas.
    """

    def __init__(self, config: SimulationConfig, plugins: Optional[List[Plugin]] = None):
        self.config = config
        self.metrics = Metrics()

        # Ordena plugins por prioridade e verifica conflitos
        self.plugins: List[Plugin] = self._setup_plugins(plugins or [])

        # Cria mundo
        recipes = World.create_random_recipes(
            num_recipes=config.num_recipes,
            sequence_length=config.sequence_length,
            alphabet_size=config.alphabet_size
        )
        self.world = World(
            node_id=0,
            recipes=recipes,
            sequence_length=config.sequence_length,
            alphabet_size=config.alphabet_size
        )

        # Cria agentes
        self.agents: List[Agent] = []
        for i in range(config.num_agents):
            # Cada agente precisa de sua própria instância de strategy
            strategy = get_strategy(config.strategy, config.learning_rate)
            agent = Agent(
                node_id=i + 1,
                sequence_length=config.sequence_length,
                alphabet_size=config.alphabet_size,
                strategy=strategy,
                initial_balance=config.initial_balance,
                cost_per_attempt=config.cost_per_attempt
            )
            self.agents.append(agent)

        # Configura modo de comunicação
        if config.mode == "hive":
            self.comm_mode = HiveMode(gamma=config.gamma)
        else:  # local
            adjacency = create_topology(
                config.topology_type,
                config.num_agents,
                k=config.topology_k
            )
            # Atualiza vizinhos dos agentes
            for agent in self.agents:
                agent.neighbors = adjacency.get(agent.node_id, [])

            self.comm_mode = LocalMode(adjacency=adjacency, gamma=config.gamma)

        self.global_best_reward = 0.0
        self.winner_agent = None
        self.winner_tick = None
        self.winner_sequence = None
        self.current_tick = 0
        self._initialized = False

        # Contador global de IDs para evitar duplicatas quando agentes morrem/nascem
        self._next_agent_id = config.num_agents + 1

    def _setup_plugins(self, plugins: List[Plugin]) -> List[Plugin]:
        """
        Configura plugins: ordena por prioridade e verifica conflitos.

        Args:
            plugins: Lista de plugins a configurar

        Returns:
            Lista ordenada de plugins

        Raises:
            ValueError: Se houver conflitos entre plugins
        """
        if not plugins:
            return []

        # Verifica conflitos
        plugin_names = {p.get_name() for p in plugins}
        for plugin in plugins:
            conflicts = plugin.conflicts & plugin_names
            if conflicts:
                raise ValueError(
                    f"Plugin '{plugin.get_name()}' conflita com: {conflicts}"
                )

        # Verifica dependencias
        for plugin in plugins:
            missing = plugin.dependencies - plugin_names
            if missing:
                print(f"Aviso: Plugin '{plugin.get_name()}' tem dependencias faltando: {missing}")

        # Verifica modo requerido
        for plugin in plugins:
            required_mode = getattr(plugin, 'requires_mode', None)
            if required_mode and required_mode != self.config.mode:
                print(f"Aviso: Plugin '{plugin.get_name()}' requer modo '{required_mode}', "
                      f"mas esta usando '{self.config.mode}'. Plugin sera ignorado.")
                plugins = [p for p in plugins if p != plugin]

        # Ordena por prioridade (menor primeiro)
        return sorted(plugins, key=lambda p: p.priority)

    def get_best_match(self) -> int:
        """Retorna o melhor match atual (numero de posicoes corretas)"""
        if self.global_best_reward >= 100.0:
            return self.config.sequence_length
        return int(self.global_best_reward)

    def get_total_spent(self) -> float:
        """Retorna gasto total de todos os agentes"""
        return sum(a.total_spent for a in self.agents)

    def run_single_tick(self) -> bool:
        """
        Executa um unico tick da simulacao.

        Returns:
            True se encontrou solucao, False caso contrario
        """
        if not self._initialized:
            self._initialized = True
            # Hook: simulation start (primeira vez)
            for plugin in self.plugins:
                plugin.on_simulation_start(self)

        tick = self.current_tick

        # Hook: tick start
        for plugin in self.plugins:
            plugin.on_tick_start(self, tick)

        tick_rewards = self._run_tick(cpu_count())

        # Hook: tick end
        for plugin in self.plugins:
            plugin.on_tick_end(self, tick, tick_rewards)

        # Checa se ainda há agentes (podem ter morrido)
        if not self.agents:
            self.current_tick += 1
            return False

        # Atualiza melhor global
        max_tick_reward = max(tick_rewards) if tick_rewards else 0.0
        if max_tick_reward > self.global_best_reward:
            self.global_best_reward = max_tick_reward

        # Encontrou solucao?
        if max_tick_reward >= 100.0:
            winner_idx = tick_rewards.index(max_tick_reward)
            winner_agent = self.agents[winner_idx]

            self.winner_agent = winner_agent
            self.winner_tick = tick
            self.winner_sequence = winner_agent.best_sequence

            self.current_tick += 1
            return True

        # Comunicacao entre agentes
        self.comm_mode.communicate(self.agents, tick_rewards)

        self.current_tick += 1
        return False

    def _print_victory_banner(self, winner_agent, tick, total_attempts):
        """Imprime banner de vitória formatado"""
        # Calcula stats de economia
        total_spent = sum(a.total_spent for a in self.agents)
        total_balance = sum(a.balance for a in self.agents)
        initial_total = sum(a.initial_balance for a in self.agents)
        roi = ((total_balance - initial_total) / initial_total * 100) if initial_total > 0 else 0

        print("\n")
        print("="*64)
        print("          SOLUCAO ENCONTRADA!")
        print("="*64)
        print(f"  Vencedor:        Agente {winner_agent.node_id}")
        print(f"  Rodada:          Tick {tick}")
        print(f"  Guess vencedor:  {winner_agent.best_sequence}")
        print(f"  Tentativas:      {total_attempts}")
        print(f"  Modo:            {self.config.mode.upper()}")
        print(f"  Strategy:        {self.config.strategy}")
        print("-"*64)
        print(f"  Gasto total:     {total_spent:.0f} creditos")
        print(f"  Saldo final:     {total_balance:.0f} creditos")
        print(f"  ROI:             {roi:+.1f}%")
        print("="*64)
        print()

    def run(self, use_multiprocessing: bool = True):
        """
        Executa a simulação.

        Args:
            use_multiprocessing: Se True, paraleliza processamento dos agentes
        """
        print(f"\nIniciando simulação - Modo: {self.config.mode.upper()}")
        print(f"Agentes: {self.config.num_agents} | Ticks: {self.config.num_ticks}")
        print(f"Sequence length: {self.config.sequence_length} | Alphabet: {self.config.alphabet_size}")
        print(f"Receitas: {self.config.num_recipes}")
        if self.plugins:
            print(f"Plugins: {', '.join(p.get_name() for p in self.plugins)}")

        # Mostra as receitas secretas (desafio)
        print("\nReceitas a descobrir:")
        for i, recipe in enumerate(self.world.recipes):
            print(f"  Receita {i+1}: {recipe.pattern}")
        print()

        # Hook: simulation start
        for plugin in self.plugins:
            plugin.on_simulation_start(self)

        num_workers = cpu_count() if use_multiprocessing else 1
        seq_len = self.config.sequence_length  # Para mostrar formato X/Y

        for tick in range(self.config.num_ticks):
            # Hook: tick start
            for plugin in self.plugins:
                plugin.on_tick_start(self, tick)
            tick_rewards = self._run_tick(num_workers)

            # Hook: tick end (antes de verificar vitória, para plugins processarem)
            for plugin in self.plugins:
                plugin.on_tick_end(self, tick, tick_rewards)

            # Checa se ainda há agentes (podem ter morrido)
            if not self.agents:
                print("\nTodos os agentes morreram!")
                break

            # Atualiza melhor global
            max_tick_reward = max(tick_rewards) if tick_rewards else 0.0
            if max_tick_reward > self.global_best_reward:
                self.global_best_reward = max_tick_reward

            # CRITÉRIO DE PARADA: Alguém acertou 100%?
            if max_tick_reward >= 100.0:
                winner_idx = tick_rewards.index(max_tick_reward)
                winner_agent = self.agents[winner_idx]

                # Salva informações do vencedor
                self.winner_agent = winner_agent
                self.winner_tick = tick
                self.winner_sequence = winner_agent.best_sequence

                # Calcula total de tentativas
                total_attempts = sum(a.num_attempts for a in self.agents)

                # Mostra banner de vitória
                self._print_victory_banner(winner_agent, tick, total_attempts)

                # Hook: simulation end
                for plugin in self.plugins:
                    plugin.on_simulation_end(self)

                # Mostra stats dos plugins
                for plugin in self.plugins:
                    stats_str = plugin.format_stats()
                    if stats_str:
                        print(stats_str)

                # Salva métricas finais
                agents_stats = [agent.get_stats() for agent in self.agents]
                self.metrics.record_tick(
                    tick=tick,
                    mode=self.config.mode,
                    tick_rewards=tick_rewards,
                    global_best_reward=self.global_best_reward,
                    agents_stats=agents_stats
                )
                self.metrics.save_csv(self.config.output_file)

                return True  # PARA A SIMULAÇÃO!

            # Comunicação entre agentes
            self.comm_mode.communicate(self.agents, tick_rewards)

            # Coleta métricas
            if tick % self.config.log_interval == 0:
                agents_stats = [agent.get_stats() for agent in self.agents]
                self.metrics.record_tick(
                    tick=tick,
                    mode=self.config.mode,
                    tick_rewards=tick_rewards,
                    global_best_reward=self.global_best_reward,
                    agents_stats=agents_stats
                )

                # Print progress (formato X/Y para ficar claro)
                avg_reward = np.mean(tick_rewards)
                max_r = int(max_tick_reward) if max_tick_reward < 100 else "WIN"
                best_r = int(self.global_best_reward) if self.global_best_reward < 100 else "WIN"
                print(f"Tick {tick:4d} | Avg: {avg_reward:5.1f}/{seq_len} | Max: {max_r}/{seq_len} | Best: {best_r}/{seq_len}")

        # Se chegou aqui, não encontrou solução
        print("\nSimulação concluída sem encontrar solução perfeita.")
        print(f"Melhor reward atingido: {self.global_best_reward:.2f}")

        # Hook: simulation end
        for plugin in self.plugins:
            plugin.on_simulation_end(self)

        # Mostra stats dos plugins
        for plugin in self.plugins:
            stats_str = plugin.format_stats()
            if stats_str:
                print(stats_str)

        agents_stats = [agent.get_stats() for agent in self.agents]
        tick_rewards = [0.0] * len(self.agents)  # dummy pra última coleta
        self.metrics.record_tick(
            tick=self.config.num_ticks,
            mode=self.config.mode,
            tick_rewards=tick_rewards,
            global_best_reward=self.global_best_reward,
            agents_stats=agents_stats
        )

        self.metrics.print_summary()
        self.metrics.save_csv(self.config.output_file)

        return False  # Não encontrou solução

    def get_next_agent_id(self) -> int:
        """
        Retorna proximo ID unico para novo agente.

        Usado por plugins que criam agentes (ex: GeneticPlugin).

        Returns:
            ID unico garantido
        """
        agent_id = self._next_agent_id
        self._next_agent_id += 1
        return agent_id

    def _apply_modifiers(self):
        """Aplica modificadores de plugins nos parametros dos agentes"""
        for agent in self.agents:
            # Aplica modificadores de learning_rate
            if hasattr(agent.strategy, 'learning_rate'):
                if 'learning_rate' in agent.modifiers._modifiers:
                    modifier = agent.modifiers._modifiers['learning_rate']
                    agent.strategy.learning_rate = modifier.get_value()

    def _run_tick(self, num_workers: int) -> List[float]:
        """
        Executa um tick: todos os agentes geram sequências e validam.

        Args:
            num_workers: Número de workers para paralelização

        Returns:
            Lista de rewards do tick
        """
        # Aplica modificadores ANTES de rodar tick
        self._apply_modifiers()

        if num_workers > 1:
            # Paralelo com multiprocessing
            with Pool(processes=num_workers) as pool:
                args_list = [(agent, self.world) for agent in self.agents]
                results = pool.map(_agent_tick_worker, args_list)

            # Atualiza agentes com resultados
            tick_rewards = []
            for i, (updated_agent, sequence, reward) in enumerate(results):
                # Copia estado atualizado de volta
                self.agents[i].P = updated_agent.P
                self.agents[i].total_reward = updated_agent.total_reward
                self.agents[i].best_reward = updated_agent.best_reward
                self.agents[i].best_sequence = updated_agent.best_sequence
                self.agents[i].num_attempts = updated_agent.num_attempts
                # Economia
                self.agents[i].balance = updated_agent.balance
                self.agents[i].total_spent = updated_agent.total_spent
                self.agents[i].history = updated_agent.history
                tick_rewards.append(reward)

            return tick_rewards
        else:
            # Sequencial
            tick_rewards = []
            for agent in self.agents:
                sequence = agent.sample_sequence()
                reward = self.world.validate(sequence)
                agent.update_policy(sequence, reward)
                tick_rewards.append(reward)

            return tick_rewards
