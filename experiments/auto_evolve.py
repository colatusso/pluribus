"""
Auto-Evolução do Pluribus

Script que roda simulações, analisa resultados e sugere/aplica melhorias automaticamente.
Roda em background enquanto a GUI continua funcionando.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
from datetime import datetime
from src.simulation.config import SimulationConfig
from src.simulation.runner import SimulationRunner

class AutoEvolver:
    """
    Sistema de auto-evolução que:
    1. Roda experimentos variados
    2. Analisa padrões de sucesso/falha
    3. Identifica problemas
    4. Sugere melhorias
    """

    def __init__(self):
        self.results_history = []
        self.insights = []
        self.iteration = 0

    def run_experiment(self, config_name: str, config: SimulationConfig) -> dict:
        """Roda um experimento e captura métricas"""
        print(f"\n{'='*80}")
        print(f"EXPERIMENTO #{self.iteration + 1}: {config_name}")
        print(f"{'='*80}")

        start_time = time.time()
        runner = SimulationRunner(config)

        # Roda simulação
        found = runner.run(use_multiprocessing=False)

        elapsed = time.time() - start_time

        # Captura métricas
        result = {
            'iteration': self.iteration,
            'config_name': config_name,
            'timestamp': datetime.now().isoformat(),
            'success': found,
            'winner_tick': runner.winner_tick if found else None,
            'num_agents': config.num_agents,
            'agents_alive': len(runner.agents),
            'survival_rate': len(runner.agents) / config.num_agents,
            'total_attempts': sum(a.num_attempts for a in runner.agents),
            'avg_attempts_per_agent': sum(a.num_attempts for a in runner.agents) / len(runner.agents) if runner.agents else 0,
            'total_spent': runner.get_total_spent(),
            'best_match': runner.get_best_match(),
            'sequence_length': config.sequence_length,
            'elapsed_seconds': elapsed,
            'config': {
                'mode': config.mode,
                'collective_sync': config.collective_sync,
                'learning_strength': config.learning_strength,
                'energy': config.energy,
                'energy_per_try': config.energy_per_try,
                'strategy': config.strategy
            }
        }

        self.results_history.append(result)
        self.iteration += 1

        # Print resultado
        print(f"\n📊 RESULTADO:")
        print(f"  Sucesso: {'✅ SIM' if found else '❌ NÃO'}")
        if found:
            print(f"  Resolvido em: {runner.winner_tick} ticks")
        print(f"  Best match: {runner.get_best_match()}/{config.sequence_length}")
        print(f"  Agentes vivos: {len(runner.agents)}/{config.num_agents} ({result['survival_rate']*100:.1f}%)")
        print(f"  Total tentativas: {result['total_attempts']}")
        print(f"  Tempo: {elapsed:.2f}s")

        return result

    def analyze_results(self):
        """Analisa todos os resultados e identifica padrões"""
        print(f"\n{'='*80}")
        print(f"ANÁLISE DE RESULTADOS ({len(self.results_history)} experimentos)")
        print(f"{'='*80}\n")

        if len(self.results_history) < 2:
            print("Poucos experimentos ainda. Continue rodando...\n")
            return

        # Separa sucessos e falhas
        successes = [r for r in self.results_history if r['success']]
        failures = [r for r in self.results_history if not r['success']]

        success_rate = len(successes) / len(self.results_history) * 100

        print(f"📈 TAXA DE SUCESSO: {success_rate:.1f}% ({len(successes)}/{len(self.results_history)})")
        print()

        # Análise de sucessos
        if successes:
            avg_ticks = sum(s['winner_tick'] for s in successes) / len(successes)
            avg_survival = sum(s['survival_rate'] for s in successes) / len(successes)

            print("✅ PADRÕES DE SUCESSO:")
            print(f"  Média de ticks até solução: {avg_ticks:.1f}")
            print(f"  Taxa média de sobrevivência: {avg_survival*100:.1f}%")

            # Identifica melhor configuração
            best = min(successes, key=lambda x: x['winner_tick'])
            print(f"\n  🏆 MELHOR RESULTADO:")
            print(f"    Config: {best['config_name']}")
            print(f"    Resolvido em: {best['winner_tick']} ticks")
            print(f"    Sync: {best['config']['collective_sync']}%")
            print(f"    Learning: {best['config']['learning_strength']}%")
            print()

        # Análise de falhas
        if failures:
            avg_match = sum(f['best_match'] for f in failures) / len(failures)
            avg_survival = sum(f['survival_rate'] for f in failures) / len(failures)

            print("❌ PADRÕES DE FALHA:")
            print(f"  Best match médio: {avg_match:.1f}/{failures[0]['sequence_length']}")
            print(f"  Taxa média de sobrevivência: {avg_survival*100:.1f}%")

            # Identifica problema comum
            low_energy_failures = [f for f in failures if f['survival_rate'] < 0.3]
            if low_energy_failures:
                print(f"\n  ⚠️  {len(low_energy_failures)} falhas por falta de energia (<30% sobrevivência)")
                insight = "INSIGHT: Aumentar energia inicial ou reduzir custo por tentativa"
                print(f"  💡 {insight}")
                self.insights.append(insight)

            convergence_failures = [f for f in failures if f['best_match'] < f['sequence_length'] * 0.5]
            if convergence_failures:
                print(f"  ⚠️  {len(convergence_failures)} falhas por convergência lenta (<50% match)")
                insight = "INSIGHT: Aumentar collective_sync ou learning_strength"
                print(f"  💡 {insight}")
                self.insights.append(insight)
            print()

    def suggest_next_experiment(self) -> dict:
        """Sugere próximo experimento baseado nos resultados"""
        if not self.results_history:
            return ('baseline', SimulationConfig.balanced(num_agents=15, sequence_length=6))

        last_result = self.results_history[-1]

        # Se último falhou, ajusta
        if not last_result['success']:
            if last_result['survival_rate'] < 0.5:
                # Problema de energia
                print("\n💡 SUGESTÃO: Aumentar energia (último experimento teve baixa sobrevivência)")
                config = SimulationConfig(
                    num_agents=15,
                    sequence_length=6,
                    alphabet_size=4,
                    num_recipes=1,
                    num_ticks=100,
                    mode='hive',
                    collective_sync=70,
                    learning_strength=20,
                    energy=1000,  # Aumentado!
                    energy_per_try=1,
                    strategy='bandit'
                )
                return ('high_energy', config)
            else:
                # Problema de convergência
                print("\n💡 SUGESTÃO: Aumentar collective_sync (agentes vivos mas não convergindo)")
                config = SimulationConfig(
                    num_agents=15,
                    sequence_length=6,
                    alphabet_size=4,
                    num_recipes=1,
                    num_ticks=100,
                    mode='hive',
                    collective_sync=90,  # Aumentado!
                    learning_strength=25,  # Aumentado!
                    energy=500,
                    energy_per_try=1,
                    strategy='bandit'
                )
                return ('high_sync', config)

        # Se último sucedeu, testa variação
        print("\n💡 SUGESTÃO: Testar problema mais difícil (último sucedeu)")
        config = SimulationConfig(
            num_agents=20,
            sequence_length=8,  # Mais difícil!
            alphabet_size=4,
            num_recipes=1,
            num_ticks=150,
            mode='hive',
            collective_sync=last_result['config']['collective_sync'],
            learning_strength=last_result['config']['learning_strength'],
            energy=last_result['config']['energy'],
            energy_per_try=last_result['config']['energy_per_try'],
            strategy='bandit'
        )
        return ('harder_problem', config)

    def run_evolution_cycle(self, num_experiments: int = 5):
        """Roda um ciclo completo de evolução"""
        print(f"\n{'#'*80}")
        print(f"# INICIANDO CICLO DE AUTO-EVOLUÇÃO")
        print(f"# Experimentos planejados: {num_experiments}")
        print(f"# Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*80}\n")

        for i in range(num_experiments):
            # Sugere próximo experimento
            config_name, config = self.suggest_next_experiment()

            # Roda experimento
            result = self.run_experiment(config_name, config)

            # Analisa resultados até agora
            if (i + 1) % 2 == 0:  # A cada 2 experimentos
                self.analyze_results()

            # Pequena pausa entre experimentos
            if i < num_experiments - 1:
                print("\n⏸️  Próximo experimento em 2s...\n")
                time.sleep(2)

        # Análise final
        print(f"\n{'#'*80}")
        print(f"# ANÁLISE FINAL DO CICLO")
        print(f"{'#'*80}")
        self.analyze_results()

        # Salva resultados
        self.save_results()

    def save_results(self):
        """Salva histórico de resultados"""
        filename = f"auto_evolve_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'results': self.results_history,
                'insights': self.insights,
                'total_experiments': len(self.results_history),
                'success_rate': len([r for r in self.results_history if r['success']]) / len(self.results_history) if self.results_history else 0
            }, f, indent=2)

        print(f"\n💾 Resultados salvos em: {filename}")

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║                  PLURIBUS - AUTO-EVOLUÇÃO                          ║
    ║                                                                    ║
    ║  Sistema autônomo de melhoria contínua via experimentos           ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)

    evolver = AutoEvolver()

    try:
        evolver.run_evolution_cycle(num_experiments=5)

        print(f"\n{'='*80}")
        print("✅ CICLO DE EVOLUÇÃO COMPLETO!")
        print(f"{'='*80}\n")

        # Resumo final
        successes = [r for r in evolver.results_history if r['success']]
        if successes:
            best = min(successes, key=lambda x: x['winner_tick'])
            print("🏆 MELHOR CONFIGURAÇÃO ENCONTRADA:")
            print(f"  Nome: {best['config_name']}")
            print(f"  Ticks: {best['winner_tick']}")
            print(f"  Collective Sync: {best['config']['collective_sync']}%")
            print(f"  Learning Strength: {best['config']['learning_strength']}%")
            print(f"  Energy: {best['config']['energy']}")

        if evolver.insights:
            print(f"\n💡 INSIGHTS DESCOBERTOS ({len(set(evolver.insights))}):")
            for insight in set(evolver.insights):
                print(f"  - {insight}")

    except KeyboardInterrupt:
        print("\n\n⏹️  Evolução interrompida pelo usuário")
        evolver.save_results()
