#!/usr/bin/env python3
"""
Compara todas as combinacoes de modo (HIVE/LOCAL) e estrategia.

Uso:
    python experiments/compare.py -num_agents 30 -sequence_length 8 -alphabet_size 4
    python experiments/compare.py --visualize  # Com interface grafica
"""
import sys
import os
import argparse
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation.config import SimulationConfig
from src.simulation.runner import SimulationRunner


def run_sequential(args):
    """Roda comparacao sequencial (modo original)"""
    modes = ['hive', 'local']
    strategies = ['bandit', 'single_var', 'explorer']

    total_runs = len(modes) * len(strategies)
    print(f"\nRodando {total_runs} combinacoes...\n")

    results = []
    run_num = 0

    for mode in modes:
        gamma = args.gamma_hive if mode == 'hive' else args.gamma_local

        for strategy in strategies:
            run_num += 1
            print(f"  [{run_num}/{total_runs}] {mode.upper()} + {strategy}")

            config = SimulationConfig(
                num_agents=args.num_agents,
                num_ticks=args.num_ticks,
                sequence_length=args.sequence_length,
                alphabet_size=args.alphabet_size,
                num_recipes=args.num_recipes,
                mode=mode,
                learning_rate=args.learning_rate,
                gamma=gamma,
                strategy=strategy,
                initial_balance=args.initial_balance,
                cost_per_attempt=args.cost_per_attempt,
                topology_type=args.topology,
                log_interval=args.log_interval,
                output_file=f'compare_{mode}_{strategy}.csv'
            )

            runner = SimulationRunner(config)

            # Roda silencioso se --quiet
            if args.quiet:
                import io
                import contextlib
                f = io.StringIO()
                with contextlib.redirect_stdout(f):
                    start = time.time()
                    runner.run(use_multiprocessing=True)
                    elapsed = time.time() - start
            else:
                start = time.time()
                runner.run(use_multiprocessing=True)
                elapsed = time.time() - start

            # Coleta resultados
            spent = sum(a.total_spent for a in runner.agents)
            attempts = sum(a.num_attempts for a in runner.agents)

            results.append({
                'mode': mode.upper(),
                'strategy': strategy,
                'tick': runner.winner_tick,
                'attempts': attempts,
                'spent': spent,
                'time': elapsed,
                'winner': runner.winner_agent.node_id if runner.winner_agent else None
            })

    return results


def run_visualized(args):
    """Roda comparacao com visualizacao pygame"""
    from src.visualization.race import RaceVisualizer

    modes = ['hive', 'local']
    strategies = ['bandit', 'single_var', 'explorer']

    # Cria runners para todas as combinacoes
    runners = {}
    for mode in modes:
        gamma = args.gamma_hive if mode == 'hive' else args.gamma_local

        for strategy in strategies:
            name = f"{mode.upper()}+{strategy}"

            config = SimulationConfig(
                num_agents=args.num_agents,
                num_ticks=args.num_ticks,
                sequence_length=args.sequence_length,
                alphabet_size=args.alphabet_size,
                num_recipes=args.num_recipes,
                mode=mode,
                learning_rate=args.learning_rate,
                gamma=gamma,
                strategy=strategy,
                initial_balance=args.initial_balance,
                cost_per_attempt=args.cost_per_attempt,
                topology_type=args.topology,
                log_interval=args.log_interval,
                output_file=f'compare_{mode}_{strategy}.csv'
            )

            runners[name] = {
                'runner': SimulationRunner(config),
                'finished': False,
                'start_time': None
            }

    # Inicializa visualizador
    viz = RaceVisualizer(args.sequence_length, len(runners))
    viz.init_pygame()

    # Ordem fixa para display
    display_order = [
        'HIVE+bandit', 'HIVE+single_var', 'HIVE+explorer',
        'LOCAL+bandit', 'LOCAL+single_var', 'LOCAL+explorer'
    ]

    winner_name = None
    start_time = time.time()

    # Loop principal
    for tick in range(args.num_ticks):
        # Processa eventos pygame
        if not viz.handle_events():
            break

        # Roda um tick em cada runner
        for name in display_order:
            data = runners[name]
            if not data['finished']:
                found = data['runner'].run_single_tick()
                if found:
                    data['finished'] = True
                    if winner_name is None:
                        winner_name = name

        # Atualiza visualizador
        viz_results = []
        for name in display_order:
            runner = runners[name]['runner']
            viz_results.append({
                'name': name,
                'best_match': runner.get_best_match(),
                'spent': runner.get_total_spent()
            })

        viz.update(viz_results)
        viz.set_tick(tick, args.num_ticks)

        if winner_name:
            viz.set_winner(winner_name)

        viz.draw()

        # Todos terminaram?
        all_finished = all(d['finished'] for d in runners.values())
        if all_finished:
            break

        # Pequeno delay para nao sobrecarregar
        time.sleep(0.01)

    elapsed = time.time() - start_time

    # Aguarda usuario fechar
    if winner_name:
        while viz.handle_events():
            viz.draw()
            time.sleep(0.05)

    viz.close()

    # Monta resultados
    results = []
    for name in display_order:
        runner = runners[name]['runner']
        mode, strategy = name.split('+')
        spent = runner.get_total_spent()
        attempts = sum(a.num_attempts for a in runner.agents)

        results.append({
            'mode': mode,
            'strategy': strategy,
            'tick': runner.winner_tick,
            'attempts': attempts,
            'spent': spent,
            'time': elapsed / len(runners),  # Aproximado
            'winner': runner.winner_agent.node_id if runner.winner_agent else None
        })

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Comparar todas as combinacoes HIVE/LOCAL x estrategias',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-num_agents', type=int, default=30,
                       help='Numero de agentes')
    parser.add_argument('-sequence_length', type=int, default=8,
                       help='Tamanho das sequencias')
    parser.add_argument('-alphabet_size', type=int, default=4,
                       help='Tamanho do alfabeto')
    parser.add_argument('-num_recipes', type=int, default=1,
                       help='Numero de receitas')
    parser.add_argument('-num_ticks', type=int, default=500,
                       help='Maximo de ticks')
    parser.add_argument('-learning_rate', type=float, default=0.25,
                       help='Taxa de aprendizado')
    parser.add_argument('-gamma_hive', type=float, default=0.6,
                       help='Gamma para HIVE')
    parser.add_argument('-gamma_local', type=float, default=0.3,
                       help='Gamma para LOCAL')
    parser.add_argument('-initial_balance', type=float, default=1000.0,
                       help='Saldo inicial de cada agente')
    parser.add_argument('-cost_per_attempt', type=float, default=1.0,
                       help='Custo por tentativa')
    parser.add_argument('-topology', type=str, default='ring',
                       choices=['ring', 'random', 'complete'],
                       help='Topologia para LOCAL')
    parser.add_argument('-log_interval', type=int, default=50,
                       help='Intervalo de logging')
    parser.add_argument('--no-plot', action='store_true',
                       help='Nao mostrar graficos')
    parser.add_argument('--quiet', action='store_true',
                       help='Modo silencioso (menos output)')
    parser.add_argument('--visualize', action='store_true',
                       help='Mostrar visualizacao pygame em tempo real')

    args = parser.parse_args()

    # Banner
    print("\n" + "="*70)
    print("COMPARACAO COMPLETA")
    print("="*70)
    print(f"Agentes: {args.num_agents} | Sequencia: {args.sequence_length} | Alfabeto: {args.alphabet_size}")
    print(f"Receitas: {args.num_recipes} | Max ticks: {args.num_ticks}")
    print("="*70)

    # Roda comparacao
    if args.visualize:
        results = run_visualized(args)
    else:
        results = run_sequential(args)

    # Ordena por eficiencia (tick primeiro, depois gasto)
    def sort_key(r):
        if r['tick'] is None:
            return (float('inf'), r['spent'])
        return (r['tick'], r['spent'])

    results.sort(key=sort_key)

    # Tabela de resultados
    print("\n" + "="*70)
    print("RESULTADOS (ordenado por eficiencia)")
    print("="*70)
    print(f"\n{'#':<4} {'Modo':<8} {'Strategy':<12} {'Tick':<8} {'Tent.':<8} {'Gasto':<10} {'Tempo':<8}")
    print("-"*70)

    for i, r in enumerate(results, 1):
        tick_str = str(r['tick']) if r['tick'] else "N/A"
        print(f"{i:<4} {r['mode']:<8} {r['strategy']:<12} {tick_str:<8} {r['attempts']:<8} {r['spent']:<10.0f} {r['time']:.1f}s")

    print("-"*70)

    # Melhor resultado
    best = results[0]
    if best['tick']:
        print(f"\nMELHOR: {best['mode']} + {best['strategy']} (tick {best['tick']}, {best['spent']:.0f} creditos)")
    else:
        print(f"\nNenhuma combinacao encontrou solucao!")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
