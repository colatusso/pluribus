#!/usr/bin/env python3
"""
Exemplo simples: roda uma simulação rápida pra ver o sistema funcionando.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation.config import SimulationConfig
from src.simulation.runner import SimulationRunner


def main():
    print("="*70)
    print("PLURIBUS - Exemplo Simples")
    print("="*70)
    print()

    # Configuração simples e rápida
    config = SimulationConfig(
        num_agents=15,
        num_ticks=300,
        sequence_length=20,
        alphabet_size=6,
        num_recipes=2,
        mode="hive",
        learning_rate=0.15,
        gamma=0.6,
        log_interval=20,
        output_file="example_results.csv"
    )

    # Roda simulação
    runner = SimulationRunner(config)
    runner.run(use_multiprocessing=True)

    print("\nPronto! Confira:")
    print("  - Métricas: example_results.csv")
    print("  - Para comparar HIVE vs LOCAL: python experiments/compare.py")


if __name__ == "__main__":
    main()
