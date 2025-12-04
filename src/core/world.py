from typing import List, Optional
from .recipe import Recipe
from .node import Node
import random


class World(Node):
    """
    Nó-mundo: validador central que guarda receitas secretas.

    Instância compartilhada entre agentes (thread-safe via multiprocessing).
    """

    def __init__(
        self,
        node_id: int,
        recipes: List[Recipe],
        sequence_length: int,
        alphabet_size: int
    ):
        super().__init__(node_id)
        self.recipes = recipes
        self.sequence_length = sequence_length
        self.alphabet_size = alphabet_size
        self.validation_count = 0

    def get_id(self) -> int:
        return self.node_id

    def validate(self, sequence: List[int]) -> float:
        """
        Valida uma sequência contra todas as receitas.

        Args:
            sequence: Sequência de tokens a validar

        Returns:
            Reward máximo entre todas as receitas
        """
        self.validation_count += 1

        if len(sequence) != self.sequence_length:
            return 0.0

        if not all(0 <= token < self.alphabet_size for token in sequence):
            return 0.0

        # Calcula reward para cada receita e retorna o máximo
        rewards = [recipe.calculate_reward(sequence) for recipe in self.recipes]
        return max(rewards) if rewards else 0.0

    def get_stats(self) -> dict:
        """Retorna estatísticas do mundo"""
        return {
            "validation_count": self.validation_count,
            "num_recipes": len(self.recipes),
            "sequence_length": self.sequence_length,
            "alphabet_size": self.alphabet_size
        }

    @staticmethod
    def create_random_recipes(
        num_recipes: int,
        sequence_length: int,
        alphabet_size: int
    ) -> List[Recipe]:
        """
        Factory method para criar receitas aleatórias.

        Args:
            num_recipes: Número de receitas a criar
            sequence_length: Tamanho de cada pattern (fixo)
            alphabet_size: Tamanho do alfabeto (0..M-1)

        Returns:
            Lista de receitas geradas
        """
        recipes = []
        for _ in range(num_recipes):
            # Pattern do tamanho da sequência (sem variação)
            pattern = [random.randint(0, alphabet_size - 1) for _ in range(sequence_length)]
            recipes.append(Recipe(pattern=pattern))

        return recipes
