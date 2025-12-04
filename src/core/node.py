from abc import ABC, abstractmethod
from typing import List


class Node(ABC):
    """
    Classe base abstrata para todos os nós do sistema.

    Define interface comum que tanto World quanto Agent devem respeitar.
    """

    def __init__(self, node_id: int):
        self.node_id = node_id

    @abstractmethod
    def get_id(self) -> int:
        """Retorna ID único do nó"""
        pass
