from dataclasses import dataclass
from typing import List


@dataclass
class Recipe:
    """
    Representa uma receita (padrão secreto) que o World usa para validar sequências.

    Attributes:
        pattern: Sequência de tokens que forma o padrão
    """
    pattern: List[int]

    def calculate_reward(self, sequence: List[int]) -> float:
        """
        Calcula reward baseado em match com o pattern.

        Sistema simplificado:
        - Match perfeito (100%) = 100.0 (VENCEDOR!)
        - Match parcial = número de símbolos corretos nas posições certas

        Args:
            sequence: Sequência a ser validada

        Returns:
            100.0 se match perfeito, senão número de matches
        """
        if not sequence:
            return 0.0

        # Conta matches (posições corretas)
        matches = 0
        max_len = min(len(self.pattern), len(sequence))

        for i in range(max_len):
            if sequence[i] == self.pattern[i]:
                matches += 1

        # Match perfeito? VENCEDOR!
        if matches == len(self.pattern) and len(sequence) == len(self.pattern):
            return 100.0

        # Senão retorna apenas o número de matches
        return float(matches)
