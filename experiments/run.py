#!/usr/bin/env python3
"""
CLI para rodar simulações Pluribus com parâmetros customizados.

Uso:
    python experiments/run.py -mode hive -num_agents 20 -sequence_length 10
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation.config import SimulationConfig
from src.simulation.runner import SimulationRunner


def main():
    parser = argparse.ArgumentParser(
        description='Pluribus - Simulação de Mente Coletiva',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Parâmetros principais
    parser.add_argument('-mode', type=str, default='hive',
                       choices=['hive', 'local'],
                       help='Modo de comunicação: hive (global) ou local (vizinhos)')

    parser.add_argument('-num_agents', type=int, default=20,
                       help='Número de agentes')

    parser.add_argument('-sequence_length', type=int, default=10,
                       help='Tamanho das sequências')

    parser.add_argument('-alphabet_size', type=int, default=5,
                       help='Tamanho do alfabeto (0 até N-1). Ex: 5 = [0,1,2,3,4]')

    parser.add_argument('-num_recipes', type=int, default=1,
                       help='Número de receitas secretas')

    parser.add_argument('-num_ticks', type=int, default=1000,
                       help='Máximo de ticks (para se encontrar solução antes)')

    # Parâmetros de aprendizado
    parser.add_argument('-learning_rate', type=float, default=0.2,
                       help='Taxa de aprendizado (0.0-1.0)')

    parser.add_argument('-gamma', type=float, default=0.5,
                       help='Intensidade de sincronização (0.0-1.0, alto=mais convergência)')

    parser.add_argument('-strategy', type=str, default='bandit',
                       choices=['bandit', 'single_var', 'explorer'],
                       help='Estrategia de update: bandit, single_var, explorer')

    # Economia
    parser.add_argument('-initial_balance', type=float, default=1000.0,
                       help='Saldo inicial de cada agente')

    parser.add_argument('-cost_per_attempt', type=float, default=1.0,
                       help='Custo por tentativa')

    # Parâmetros LOCAL
    parser.add_argument('-topology', type=str, default='ring',
                       choices=['ring', 'random', 'complete'],
                       help='Topologia para modo LOCAL')

    parser.add_argument('-topology_k', type=int, default=3,
                       help='Número de vizinhos (para topologia random)')

    # Output
    parser.add_argument('-log_interval', type=int, default=5,
                       help='Intervalo de logging (printa a cada N ticks)')

    parser.add_argument('-output', type=str, default='results.csv',
                       help='Arquivo de saída para métricas')

    parser.add_argument('--no-multiprocessing', action='store_true',
                       help='Desabilita multiprocessing (roda sequencial)')

    args = parser.parse_args()

    # Valida parâmetros
    if args.alphabet_size < 2:
        print("Erro: alphabet_size deve ser >= 2")
        return

    if args.sequence_length < 1:
        print("Erro: sequence_length deve ser >= 1")
        return

    if args.num_agents < 1:
        print("Erro: num_agents deve ser >= 1")
        return

    # Cria configuração
    config = SimulationConfig(
        num_agents=args.num_agents,
        num_ticks=args.num_ticks,
        sequence_length=args.sequence_length,
        alphabet_size=args.alphabet_size,
        num_recipes=args.num_recipes,
        mode=args.mode,
        learning_rate=args.learning_rate,
        gamma=args.gamma,
        strategy=args.strategy,
        initial_balance=args.initial_balance,
        cost_per_attempt=args.cost_per_attempt,
        topology_type=args.topology,
        topology_k=args.topology_k,
        log_interval=args.log_interval,
        output_file=args.output
    )

    # Mostra configuração
    print("\n" + "="*70)
    print("PLURIBUS - Configuracao")
    print("="*70)
    print(f"Modo:              {args.mode.upper()}")
    print(f"Agentes:           {args.num_agents}")
    print(f"Sequence length:   {args.sequence_length}")
    print(f"Alfabeto:          0 ate {args.alphabet_size - 1} (tamanho {args.alphabet_size})")
    print(f"Receitas:          {args.num_recipes}")
    print(f"Max ticks:         {args.num_ticks}")
    print(f"Strategy:          {args.strategy}")
    print(f"Learning rate:     {args.learning_rate}")
    print(f"Gamma:             {args.gamma}")
    print(f"Saldo inicial:     {args.initial_balance}")
    print(f"Custo/tentativa:   {args.cost_per_attempt}")
    if args.mode == 'local':
        print(f"Topologia:         {args.topology}")
        if args.topology == 'random':
            print(f"Vizinhos (k):      {args.topology_k}")
    print(f"Output:            {args.output}")
    print("="*70 + "\n")

    # Roda simulação
    runner = SimulationRunner(config)
    use_mp = not args.no_multiprocessing
    runner.run(use_multiprocessing=use_mp)


if __name__ == "__main__":
    main()
