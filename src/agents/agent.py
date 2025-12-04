import numpy as np
from typing import List, Optional
from ..core.node import Node
from .strategies import UpdateStrategy, BanditStrategy
from ..utils.modifiers import AgentModifiers


class Agent(Node):
    """
    Agent node: explores the sequence space trying to maximize reward.

    Maintains probability matrix P[L][M] and generates sequences by sampling.
    """

    def __init__(
        self,
        node_id: int,
        sequence_length: int,
        alphabet_size: int,
        strategy: Optional[UpdateStrategy] = None,
        neighbors: Optional[List[int]] = None,
        initial_balance: float = 1000.0,
        cost_per_attempt: float = 1.0
    ):
        super().__init__(node_id)
        self.sequence_length = sequence_length
        self.alphabet_size = alphabet_size
        self.neighbors = neighbors or []

        # Probability matrix: P[pos][token]
        # Initialize as uniform
        self.P = np.ones((sequence_length, alphabet_size)) / alphabet_size

        # Update strategy
        self.strategy = strategy or BanditStrategy()

        # Economy
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.cost_per_attempt = cost_per_attempt
        self.total_spent = 0.0

        # Attempt history (for comparative analysis)
        self.history: List[tuple] = []  # [(sequence, reward), ...]
        self.max_history = 10  # Keep last N attempts

        # Stats
        self.total_reward = 0.0
        self.best_sequence: Optional[List[int]] = None
        self.best_reward = 0.0
        self.num_attempts = 0

        # Modifier system for plugins
        self.modifiers = AgentModifiers()

    def get_id(self) -> int:
        return self.node_id

    def sample_sequence(self) -> List[int]:
        """
        Generates a sequence based on distribution P.

        Returns:
            Sequence of length L
        """
        sequence = []
        for pos in range(self.sequence_length):
            # Sample token according to probability P[pos]
            token = np.random.choice(self.alphabet_size, p=self.P[pos])
            sequence.append(int(token))
        return sequence

    def update_policy(self, sequence: List[int], reward: float):
        """
        Updates policy matrix based on result.

        Args:
            sequence: Sequence that was tested
            reward: Received reward
        """
        self.num_attempts += 1
        self.total_reward += reward

        # Economy: charge for attempt (FIX: don't allow negative balance)
        cost = min(self.cost_per_attempt, self.balance)
        self.balance -= cost
        self.total_spent += cost

        # History for comparative analysis
        self.history.append((sequence.copy(), reward))
        if len(self.history) > self.max_history:
            self.history.pop(0)

        # Update best if necessary
        if reward > self.best_reward:
            self.best_reward = reward
            self.best_sequence = sequence.copy()

        # Apply update strategy (pass history for advanced strategies)
        self.P = self.strategy.update(self.P, sequence, reward, history=self.history)

    def merge_with(self, other_P: np.ndarray, gamma: float = 0.3):
        """
        Mistura a policy atual com outra policy (comunicação).

        Args:
            other_P: Policy matrix de outro agente
            gamma: Peso da mistura (0 = mantém atual, 1 = copia completo)
        """
        self.P = (1 - gamma) * self.P + gamma * other_P

        # Re-normaliza por segurança
        for pos in range(self.P.shape[0]):
            row_sum = self.P[pos].sum()
            if row_sum > 0:
                self.P[pos] /= row_sum

    def get_stats(self) -> dict:
        """Retorna estatísticas do agente"""
        roi = ((self.balance - self.initial_balance) / self.initial_balance * 100) if self.initial_balance > 0 else 0
        return {
            "agent_id": self.node_id,
            "total_reward": self.total_reward,
            "best_reward": self.best_reward,
            "num_attempts": self.num_attempts,
            "avg_reward": self.total_reward / max(1, self.num_attempts),
            "balance": self.balance,
            "total_spent": self.total_spent,
            "roi": roi
        }
