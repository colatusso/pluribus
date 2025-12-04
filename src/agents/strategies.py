from abc import ABC, abstractmethod
import numpy as np
from typing import List, Optional
import random


class UpdateStrategy(ABC):
    """Abstract interface for policy matrix update strategies."""

    @abstractmethod
    def update(
        self,
        P: np.ndarray,
        sequence: List[int],
        reward: float,
        **kwargs
    ) -> np.ndarray:
        """
        Updates the policy matrix based on sequence and reward.

        Args:
            P: Current policy matrix [L x M]
            sequence: Generated sequence
            reward: Received reward
            **kwargs: Additional strategy-specific parameters

        Returns:
            Updated P matrix
        """
        pass


class BanditStrategy(UpdateStrategy):
    """
    Simple position-based multi-armed bandit strategy.

    Reinforces each used token proportionally to the received reward.
    """

    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate

    def update(
        self,
        P: np.ndarray,
        sequence: List[int],
        reward: float,
        **kwargs
    ) -> np.ndarray:
        """
        Update rule: P[pos][used_token] += α * reward

        Then normalizes each row to maintain probability distribution.
        """
        P_new = P.copy()

        for pos, token in enumerate(sequence):
            P_new[pos, token] += self.learning_rate * reward

        # FIX: Clamp negative values to zero (negative reward can generate values < 0)
        P_new = np.maximum(P_new, 0.0)

        # Normalize each row (position) to sum to 1
        for pos in range(P_new.shape[0]):
            row_sum = P_new[pos].sum()
            if row_sum > 0:
                P_new[pos] /= row_sum
            else:
                # Edge case: all values are zero, revert to uniform distribution
                P_new[pos] = np.ones(P_new.shape[1]) / P_new.shape[1]

        return P_new


class SingleVarStrategy(UpdateStrategy):
    """
    Methodical strategy: analyzes history and focuses on uncertain positions.

    Uses comparative feedback to identify which positions to change.
    """

    def __init__(self, learning_rate: float = 0.15):
        self.learning_rate = learning_rate
        self.position_confidence = None  # Confidence per position

    def update(
        self,
        P: np.ndarray,
        sequence: List[int],
        reward: float,
        **kwargs
    ) -> np.ndarray:
        """
        Analyzes history to infer which positions are correct.
        Reinforces positions that seem correct more strongly.
        """
        P_new = P.copy()
        history = kwargs.get('history', [])

        # Initialize confidence if needed
        if self.position_confidence is None:
            self.position_confidence = np.ones(P.shape[0]) * 0.5

        # Analyze history to infer correct positions
        if len(history) >= 2:
            prev_seq, prev_reward = history[-2]
            curr_seq, curr_reward = history[-1]

            # Find positions that changed
            for pos in range(len(sequence)):
                if prev_seq[pos] != curr_seq[pos]:
                    # Position changed
                    if curr_reward > prev_reward:
                        # Change improved - previous position was wrong
                        self.position_confidence[pos] = min(0.9, self.position_confidence[pos] + 0.1)
                    elif curr_reward < prev_reward:
                        # Change worsened - previous position was correct
                        self.position_confidence[pos] = max(0.1, self.position_confidence[pos] - 0.1)
                    # If equal, we don't know

        # Update with confidence-based weight
        for pos, token in enumerate(sequence):
            confidence_weight = self.position_confidence[pos]
            P_new[pos, token] += self.learning_rate * reward * confidence_weight

        # FIX: Clamp negative values to zero
        P_new = np.maximum(P_new, 0.0)

        # Normalize
        for pos in range(P_new.shape[0]):
            row_sum = P_new[pos].sum()
            if row_sum > 0:
                P_new[pos] /= row_sum
            else:
                # Edge case: all values are zero, revert to uniform distribution
                P_new[pos] = np.ones(P_new.shape[1]) / P_new.shape[1]

        return P_new


class ExplorerStrategy(UpdateStrategy):
    """
    Exploratory strategy: high variation initially, focuses later.

    Uses epsilon-greedy with decay.
    """

    def __init__(self, learning_rate: float = 0.1, initial_epsilon: float = 0.3, decay: float = 0.995):
        self.learning_rate = learning_rate
        self.epsilon = initial_epsilon
        self.decay = decay
        self.num_updates = 0

    def update(
        self,
        P: np.ndarray,
        sequence: List[int],
        reward: float,
        **kwargs
    ) -> np.ndarray:
        """
        Update with decreasing exploration.
        """
        P_new = P.copy()
        self.num_updates += 1

        # Normal update (bandit)
        for pos, token in enumerate(sequence):
            P_new[pos, token] += self.learning_rate * reward

        # Add exploration noise (decays over time)
        noise = np.random.uniform(0, self.epsilon, P_new.shape)
        P_new += noise

        # Decay epsilon
        self.epsilon *= self.decay

        # FIX: Clamp negative values to zero
        P_new = np.maximum(P_new, 0.0)

        # Normalize
        for pos in range(P_new.shape[0]):
            row_sum = P_new[pos].sum()
            if row_sum > 0:
                P_new[pos] /= row_sum
            else:
                # Edge case: all values are zero, revert to uniform distribution
                P_new[pos] = np.ones(P_new.shape[1]) / P_new.shape[1]

        return P_new


def get_strategy(name: str, learning_rate: float = 0.1) -> UpdateStrategy:
    """Factory function to create strategies by name."""
    strategies = {
        'bandit': BanditStrategy(learning_rate),
        'single_var': SingleVarStrategy(learning_rate),
        'explorer': ExplorerStrategy(learning_rate)
    }
    if name not in strategies:
        raise ValueError(f"Strategy '{name}' not found. Options: {list(strategies.keys())}")
    return strategies[name]
