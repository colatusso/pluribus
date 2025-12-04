# 🧠 Pluribus - Collective Mind Simulation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A collective intelligence simulator inspired by Apple TV's Pluribus series, where autonomous agents emerge a collective mind through distributed communication and learning.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Concept](#-concept)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Simulation Modes](#-simulation-modes)
- [Configuration](#-configuration)
- [Plugins](#-plugins)
- [Learning Strategies](#-learning-strategies)
- [GUI](#-gui)
- [Auto-Evolution](#-auto-evolution)
- [Examples](#-examples)
- [API Reference](#-api-reference)

---

## 🎯 Overview

Pluribus is a simulation framework to study **collective intelligence emergence** through autonomous agents. Inspired by the Apple TV series of the same name, the system models how distributed knowledge can converge to solutions through:

- 🤝 **Agent communication** (local or global)
- 📊 **Reinforcement learning** (multi-armed bandit)
- ⚡ **Resource economy** (limited energy)
- 🧩 **Modular plugin system**

### Key Features

- ✅ **Two architectures**: HIVE (collective mind) and LOCAL (decentralized emergence)
- ✅ **3 learning strategies**: Bandit, Single-Variable, Explorer
- ✅ **20+ plugins** to modify behavior
- ✅ **Interactive GUI** with optimized presets
- ✅ **Auto-evolution system** that adjusts parameters automatically
- ✅ **Multilingual interface** (English/Portuguese)
- ✅ **100% backward compatible** with legacy code

---

## 💡 Concept

### The Problem

Agents try to discover **secret sequences** (recipes) through trial and error:

```
Recipe:  [3, 1, 4, 1, 5, 9, 2, 6]
Attempt: [3, 1, 2, 1, 5, 8, 2, 6]
Reward: 75% (6/8 correct)
```

### Communication Modes

**🐝 HIVE** - Global collective mind (fast convergence ~3 ticks)
**🕸️ LOCAL** - Communication only between neighbors (local emergence ~10-50 ticks)

---

## 🚀 Installation

```bash
git clone https://github.com/your-username/pluribus.git
cd pluribus
conda create -n pluribus python=3.10
conda activate pluribus
pip install -r requirements.txt
```

---

## ⚡ Quick Start

### CLI

```python
from src.simulation.config import SimulationConfig
from src.simulation.runner import SimulationRunner

config = SimulationConfig.fast_hive()
runner = SimulationRunner(config)

if runner.run():
    print(f"✅ Solved in {runner.winner_tick} ticks!")
```

### GUI

```bash
streamlit run experiments/gui.py
```

Access: **http://localhost:8501**

---

## 🏗️ Architecture

```
src/
├── agents/           # Agents and strategies
├── communication/    # HIVE and LOCAL
├── core/             # World, Node, Recipe
├── plugins/          # 20+ modular plugins
├── simulation/       # Config, Runner, Metrics
└── utils/            # Modifiers, i18n, helpers
```

---

## 🎮 Simulation Modes

### HIVE Mode
```python
config = SimulationConfig(
    mode='hive',
    collective_sync=90,    # 90% sharing
    learning_strength=20   # Strong learning
)
```

✅ Fast convergence (~3 ticks)
❌ Low diversity

### LOCAL Mode
```python
config = SimulationConfig(
    mode='local',
    collective_sync=30,    # 30% local
    network_density=20     # 20% connections
)
```

✅ High diversity
❌ Slow convergence

---

## ⚙️ Configuration

### Presets

```python
SimulationConfig.fast_hive()    # ~3 ticks
SimulationConfig.balanced()     # ~7 ticks
SimulationConfig.slow_local()   # ~9 ticks
SimulationConfig.chaos()        # ~44 ticks
```

### Manual

```python
config = SimulationConfig(
    num_agents=20,
    sequence_length=8,
    alphabet_size=4,
    mode='hive',
    collective_sync=70,      # 0-100%
    learning_strength=18,    # 0-100%
    energy=800,
    energy_per_try=1
)
```

### Backward Compatibility

```python
# Both syntaxes work!
config1 = SimulationConfig(gamma=0.7, learning_rate=0.2)
config2 = SimulationConfig(collective_sync=70, learning_strength=20)
```

---

## 🔌 Plugins

### Behavior
- **MoodPlugin** - Mood affects synchronization
- **FatiguePlugin** - Fatigue reduces learning

### Environment
- **SeasonPlugin** - Seasonal cycles
- **DisasterPlugin** - Random catastrophes

### Evolution
- **GeneticPlugin** - Genetic reproduction
- **AdaptationPlugin** - Parameters evolve

### Communication
- **LanguagePlugin** - Language compression
- **CensorshipPlugin** - Censor agents

Example:
```python
from src.plugins.behavior import FatiguePlugin

runner = SimulationRunner(
    config,
    plugins=[FatiguePlugin(decay_rate=0.02)]
)
```

---

## 🎓 Learning Strategies

### BanditStrategy (Default)
Multi-armed bandit - reinforces what works

### SingleVarStrategy
Methodical - changes one variable at a time

### ExplorerStrategy
Epsilon-greedy with decay - balances exploration

---

## 💻 GUI

### Features
- 📊 Real-time charts
- 🎯 Optimized presets (automatically tested)
- 📖 Complete interactive guide
- 🔧 Full control (Custom mode)
- 🌍 Multilingual (EN/PT)

### GUI Presets

| Preset | Ticks | Description |
|--------|-------|-------------|
| 🚀 Fast Hive | ~3 | Ultra-fast convergence |
| ⚖️ Balanced | ~7 | Balance (recommended) |
| 🐌 Slow Local | ~9 | Observe emergence |
| 🌪️ Chaos | ~44 | Extreme experiment |

---

## 🤖 Auto-Evolution

System that runs experiments and optimizes parameters automatically:

```bash
python experiments/auto_evolve.py
```

**What it does:**
1. Runs varied experiments
2. Analyzes success/failure patterns
3. Adjusts parameters automatically
4. Generates insights and recommendations

**Output:**
```
🏆 BEST CONFIGURATION:
  Ticks: 5
  Sync: 50%
  Learning: 15%

💡 INSIGHTS:
  - Sync 70%+ converges 40% faster
  - Learning 15-20% is the sweet spot
```

---

## 📚 Examples

### Basic

```python
config = SimulationConfig(
    num_agents=15,
    sequence_length=6,
    num_ticks=100
)

runner = SimulationRunner(config)
success = runner.run()
```

### With Plugins

```python
from src.plugins.behavior import FatiguePlugin
from src.plugins.evolution import GeneticPlugin

plugins = [
    FatiguePlugin(decay_rate=0.02),
    GeneticPlugin(mutation_rate=0.1)
]

runner = SimulationRunner(config, plugins=plugins)
runner.run()
```

### HIVE vs LOCAL

```python
# HIVE
config_hive = SimulationConfig(mode='hive')
runner_hive = SimulationRunner(config_hive)
runner_hive.run()

# LOCAL
config_local = SimulationConfig(mode='local')
runner_local = SimulationRunner(config_local)
runner_local.run()

print(f"HIVE: {runner_hive.winner_tick} ticks")
print(f"LOCAL: {runner_local.winner_tick} ticks")
```

---

## 📘 API Reference

### SimulationConfig

```python
SimulationConfig(
    num_agents: int = 20,
    sequence_length: int = 50,
    alphabet_size: int = 10,
    num_recipes: int = 3,
    num_ticks: int = 1000,
    mode: Literal["hive", "local"] = "hive",

    # Intuitive names (0-100%)
    collective_sync: int = 50,
    learning_strength: int = 10,
    energy: int = 1000,
    energy_per_try: int = 1,
    network_density: int = 30,

    strategy: str = "bandit",
    topology_type: str = "ring",
    log_interval: int = 10,
    output_file: str = "results.csv"
)
```

### SimulationRunner

```python
runner = SimulationRunner(config, plugins=None)

# Methods
runner.run(use_multiprocessing=True) -> bool
runner.run_single_tick() -> bool
runner.get_best_match() -> int
runner.get_total_spent() -> float

# Attributes
runner.winner_tick: Optional[int]
runner.winner_agent: Optional[Agent]
runner.winner_sequence: Optional[List[int]]
runner.agents: List[Agent]
```

### Agent

```python
agent = Agent(node_id, sequence_length, alphabet_size)

# Methods
agent.sample_sequence() -> List[int]
agent.update_policy(sequence, reward)
agent.merge_with(other_P, gamma)
agent.get_stats() -> dict

# Attributes
agent.P: np.ndarray          # Probability matrix
agent.balance: float          # Energy
agent.best_reward: float
agent.modifiers: AgentModifiers
```

---

## 🐛 Bugs Fixed

### v2.0.0 (2025-12-01)

✅ **BUG #1**: Negative balance allowed
✅ **BUG #2**: Negative values in P matrix
✅ **BUG #3**: runner.run() didn't return True/False

---

## 📝 Changelog

### v2.0.0 - Sprint 1 Complete

**Simplicity:**
- Intuitive names (collective_sync, learning_strength, energy)
- Unified 0-100% scale
- Optimized factory presets
- 100% backward compatible

**Features:**
- GUI with interactive guide
- Automatically tested presets
- Auto-evolution system
- Multilingual support (EN/PT)
- 3 critical bugs fixed

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

Inspired by Apple TV's **Pluribus** series

---

**Made with ❤️ by the collective mind**
