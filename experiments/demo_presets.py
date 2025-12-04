"""
Demo: Novos Presets Simplificados

Mostra a diferença entre sintaxe antiga (confusa) e nova (intuitiva).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation.config import SimulationConfig
from src.simulation.runner import SimulationRunner

print("=" * 70)
print("  PLURIBUS - DEMO DOS NOVOS PRESETS")
print("=" * 70)
print()

# ANTES: Sintaxe confusa
print("❌ ANTES (Sintaxe antiga - confusa):")
print("-" * 70)
print("""
config = SimulationConfig(
    num_agents=20,
    sequence_length=8,
    alphabet_size=4,
    num_recipes=1,
    mode='hive',
    gamma=0.9,              # WTF é 0.9?
    learning_rate=0.2,      # 0.2 de quê?
    initial_balance=500.0,  # Dinheiro?
    cost_per_attempt=1.0    # Custo de quê?
)
""")

print()
print("=" * 70)
print()

# DEPOIS: Sintaxe clara
print("✅ AGORA (Sintaxe nova - intuitiva):")
print("-" * 70)
print("""
config = SimulationConfig(
    num_agents=20,
    sequence_length=8,
    alphabet_size=4,
    num_recipes=1,
    mode='hive',
    collective_sync=90,     # 90% de sincronização coletiva!
    learning_strength=20,   # 20% de ajuste por tentativa!
    energy=500,             # 500 de energia inicial
    energy_per_try=1        # Gasta 1 energia por try
)
""")

print()
print("=" * 70)
print()

# MELHOR AINDA: Factory Presets
print("🚀 AINDA MELHOR (Factory Presets):")
print("-" * 70)
print("""
# Convergência rápida
config = SimulationConfig.fast_hive()

# Exploração local
config = SimulationConfig.slow_local()

# Equilibrado (recomendado)
config = SimulationConfig.balanced()

# Caos experimental
config = SimulationConfig.chaos()
""")

print()
print("=" * 70)
print()

# DEMO REAL
print("🎮 RODANDO DEMO COM PRESET 'FAST_HIVE'...")
print()

config = SimulationConfig.fast_hive(num_agents=10, sequence_length=6)
runner = SimulationRunner(config)

print(f"Configuração:")
print(f"  Collective Sync: {config.collective_sync}%")
print(f"  Learning Strength: {config.learning_strength}%")
print(f"  Energy: {config.energy}")
print(f"  Agents: {config.num_agents}")
print()

# Roda apenas 20 ticks pra demo
config.num_ticks = 20
runner.run(use_multiprocessing=False)

print()
print("=" * 70)
print("✨ Demo concluída! Viu como ficou mais simples?")
print("=" * 70)
