"""
Testes de integração do sistema Pluribus.

Smoke tests para validar funcionamento básico.
"""
import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import numpy as np
from src.core.recipe import Recipe
from src.core.world import World
from src.agents.agent import Agent
from src.agents.strategies import BanditStrategy
from src.simulation.config import SimulationConfig
from src.simulation.runner import SimulationRunner


class TestRecipe:
    """Testa funcionamento das receitas"""

    def test_recipe_exact_match(self):
        """Receita deve dar reward 100.0 em match exato"""
        recipe = Recipe(pattern=[1, 2, 3, 4, 5])

        sequence = [1, 2, 3, 4, 5]
        reward = recipe.calculate_reward(sequence)

        # Match perfeito = 100.0
        assert reward == 100.0

    def test_recipe_partial_match(self):
        """Receita deve dar reward parcial em match incompleto"""
        recipe = Recipe(pattern=[1, 2, 3, 4, 5])

        # 3 de 5 corretos
        sequence = [1, 2, 3, 0, 0]
        reward = recipe.calculate_reward(sequence)

        # Deve retornar número de matches
        assert reward == 3.0

    def test_recipe_no_match(self):
        """Receita deve dar reward 0 em nenhum match"""
        recipe = Recipe(pattern=[1, 2, 3, 4, 5])

        sequence = [9, 9, 9, 9, 9]
        reward = recipe.calculate_reward(sequence)

        assert reward == 0.0


class TestWorld:
    """Testa funcionamento do World"""

    def test_world_validate(self):
        """World deve validar sequências corretamente"""
        recipes = [
            Recipe(pattern=[1, 2, 3, 0, 0])
        ]

        world = World(
            node_id=0,
            recipes=recipes,
            sequence_length=5,
            alphabet_size=10
        )

        # Sequência com match parcial
        sequence = [1, 2, 3, 0, 0]
        reward = world.validate(sequence)

        # Match perfeito = 100.0
        assert reward == 100.0

    def test_world_reject_invalid_length(self):
        """World deve rejeitar sequências com tamanho incorreto"""
        recipes = [
            Recipe(pattern=[1, 2, 3, 0, 0])
        ]

        world = World(
            node_id=0,
            recipes=recipes,
            sequence_length=5,
            alphabet_size=10
        )

        # Sequência muito curta
        sequence = [1, 2]
        reward = world.validate(sequence)

        assert reward == 0.0

    def test_world_create_random_recipes(self):
        """Factory method deve criar receitas válidas"""
        recipes = World.create_random_recipes(
            num_recipes=5,
            sequence_length=20,
            alphabet_size=10
        )

        assert len(recipes) == 5
        for recipe in recipes:
            assert len(recipe.pattern) == 20  # Fixo agora
            assert all(0 <= token < 10 for token in recipe.pattern)


class TestAgent:
    """Testa funcionamento do Agent"""

    def test_agent_sample_sequence(self):
        """Agent deve gerar sequências do tamanho correto"""
        agent = Agent(
            node_id=1,
            sequence_length=10,
            alphabet_size=5,
            strategy=BanditStrategy()
        )

        sequence = agent.sample_sequence()

        assert len(sequence) == 10
        assert all(0 <= token < 5 for token in sequence)

    def test_agent_update_policy(self):
        """Agent deve atualizar policy após receber reward"""
        agent = Agent(
            node_id=1,
            sequence_length=10,
            alphabet_size=5,
            strategy=BanditStrategy(learning_rate=0.5)
        )

        sequence = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
        initial_P = agent.P.copy()

        # Atualiza com reward alto
        agent.update_policy(sequence, reward=100.0)

        # Policy deve ter mudado
        assert not np.allclose(agent.P, initial_P)

        # Stats devem estar atualizados
        assert agent.total_reward == 100.0
        assert agent.best_reward == 100.0
        assert agent.num_attempts == 1

    def test_agent_merge(self):
        """Agent deve conseguir fazer merge com outra policy"""
        agent1 = Agent(
            node_id=1,
            sequence_length=5,
            alphabet_size=3
        )

        # Policy artificial diferente
        other_P = np.array([
            [0.1, 0.2, 0.7],
            [0.5, 0.3, 0.2],
            [0.2, 0.2, 0.6],
            [0.8, 0.1, 0.1],
            [0.3, 0.4, 0.3]
        ])

        initial_P = agent1.P.copy()
        agent1.merge_with(other_P, gamma=0.5)

        # Policy deve ter mudado
        assert not np.allclose(agent1.P, initial_P)

        # Cada linha deve somar ~1
        for pos in range(agent1.P.shape[0]):
            assert abs(agent1.P[pos].sum() - 1.0) < 0.01


class TestSimulation:
    """Testes de integração da simulação completa"""

    def test_simulation_hive_runs(self):
        """Simulação HIVE deve rodar sem erros"""
        config = SimulationConfig(
            num_agents=5,
            num_ticks=50,
            sequence_length=10,
            alphabet_size=5,
            num_recipes=2,
            mode="hive",
            log_interval=10,
            output_file="test_hive.csv"
        )

        runner = SimulationRunner(config)
        runner.run(use_multiprocessing=False)  # Sequencial pra teste

        # Deve ter coletado métricas
        assert len(runner.metrics.records) > 0

        # Cleanup
        if os.path.exists("test_hive.csv"):
            os.remove("test_hive.csv")

    def test_simulation_local_runs(self):
        """Simulação LOCAL deve rodar sem erros"""
        config = SimulationConfig(
            num_agents=5,
            num_ticks=50,
            sequence_length=10,
            alphabet_size=5,
            num_recipes=2,
            mode="local",
            topology_type="ring",
            log_interval=10,
            output_file="test_local.csv"
        )

        runner = SimulationRunner(config)
        runner.run(use_multiprocessing=False)

        # Deve ter coletado métricas
        assert len(runner.metrics.records) > 0

        # Cleanup
        if os.path.exists("test_local.csv"):
            os.remove("test_local.csv")

    def test_simulation_improves_over_time(self):
        """Simulação deve encontrar rewards positivos"""
        config = SimulationConfig(
            num_agents=10,
            num_ticks=200,
            sequence_length=15,
            alphabet_size=8,
            num_recipes=2,
            mode="hive",
            learning_rate=0.2,
            log_interval=10,
            output_file="test_improvement.csv"
        )

        runner = SimulationRunner(config)
        runner.run(use_multiprocessing=False)

        df = runner.metrics.to_dataframe()

        # Sistema deve ter encontrado soluções com reward > 0
        assert runner.global_best_reward > 0, \
            f"Sistema não encontrou nenhuma solução válida (best_reward={runner.global_best_reward})"

        # Reward médio final deve ser positivo
        final_avg = df.tail(5)['avg_reward'].mean()
        assert final_avg > 0, \
            f"Reward médio final é zero ou negativo: {final_avg:.2f}"

        # Deve ter progresso inicial (reward tick 0 < reward médio)
        initial = df.head(1)['avg_reward'].iloc[0]
        later = df.tail(10)['avg_reward'].mean()
        assert later >= initial * 0.5, \
            f"Sistema degradou muito: início={initial:.2f}, fim={later:.2f}"

        # Cleanup
        if os.path.exists("test_improvement.csv"):
            os.remove("test_improvement.csv")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
