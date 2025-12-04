"""
Internationalization (i18n) system for Pluribus.

Supports English and Portuguese.
"""

from typing import Dict, Literal

Language = Literal["en", "pt"]

# Translation dictionary
TRANSLATIONS: Dict[str, Dict[Language, str]] = {
    # App title
    "app_title": {
        "en": "Pluribus - Collective Mind Simulation",
        "pt": "Pluribus - Simulação de Mente Coletiva"
    },
    "app_subtitle": {
        "en": "Emergent collective intelligence through autonomous agents",
        "pt": "Inteligência coletiva emergente através de agentes autônomos"
    },

    # Sidebar
    "language": {
        "en": "Language",
        "pt": "Idioma"
    },
    "preset_selector": {
        "en": "Preset Configuration",
        "pt": "Configuração Predefinida"
    },
    "custom": {
        "en": "Custom",
        "pt": "Customizado"
    },
    "recommended": {
        "en": "(Recommended)",
        "pt": "(Recomendado)"
    },

    # Preset names
    "fast_hive": {
        "en": "🚀 Fast Hive",
        "pt": "🚀 Fast Hive"
    },
    "balanced": {
        "en": "⚖️ Balanced",
        "pt": "⚖️ Balanced"
    },
    "slow_local": {
        "en": "🐌 Slow Local",
        "pt": "🐌 Slow Local"
    },
    "chaos": {
        "en": "🌪️ Chaos",
        "pt": "🌪️ Chaos"
    },

    # Preset descriptions
    "fast_hive_desc": {
        "en": "Ultra-fast convergence (~3 ticks). Strong hivemind, ideal for testing.",
        "pt": "Convergência ultra-rápida (~3 ticks). Hivemind forte, ideal para testar."
    },
    "balanced_desc": {
        "en": "Balance between convergence and exploration. Good starting point.",
        "pt": "Equilíbrio entre convergência e exploração. Bom ponto de partida."
    },
    "slow_local_desc": {
        "en": "Observe local emergence. Slower but more organic convergence.",
        "pt": "Observar emergência local. Convergência mais lenta mas orgânica."
    },
    "chaos_desc": {
        "en": "Extreme experiment. High diversity, very slow convergence.",
        "pt": "Experimento extremo. Alta diversidade, convergência muito lenta."
    },

    # Parameters
    "simulation_params": {
        "en": "Simulation Parameters",
        "pt": "Parâmetros da Simulação"
    },
    "num_agents": {
        "en": "Number of Agents",
        "pt": "Número de Agentes"
    },
    "sequence_length": {
        "en": "Sequence Length",
        "pt": "Tamanho da Sequência"
    },
    "alphabet_size": {
        "en": "Alphabet Size",
        "pt": "Tamanho do Alfabeto"
    },
    "num_recipes": {
        "en": "Number of Recipes",
        "pt": "Número de Receitas"
    },
    "num_ticks": {
        "en": "Max Ticks",
        "pt": "Ticks Máximos"
    },

    "behavior_params": {
        "en": "Behavior Parameters",
        "pt": "Parâmetros de Comportamento"
    },
    "mode": {
        "en": "Communication Mode",
        "pt": "Modo de Comunicação"
    },
    "collective_sync": {
        "en": "Collective Sync (%)",
        "pt": "Sincronização Coletiva (%)"
    },
    "learning_strength": {
        "en": "Learning Strength (%)",
        "pt": "Força de Aprendizado (%)"
    },
    "strategy": {
        "en": "Learning Strategy",
        "pt": "Estratégia de Aprendizado"
    },

    "economy_params": {
        "en": "Economy Parameters",
        "pt": "Parâmetros Econômicos"
    },
    "energy": {
        "en": "Initial Energy",
        "pt": "Energia Inicial"
    },
    "energy_per_try": {
        "en": "Energy per Try",
        "pt": "Energia por Tentativa"
    },

    "topology_params": {
        "en": "Network Topology",
        "pt": "Topologia de Rede"
    },
    "topology_type": {
        "en": "Topology Type",
        "pt": "Tipo de Topologia"
    },
    "network_density": {
        "en": "Network Density (%)",
        "pt": "Densidade da Rede (%)"
    },

    # Buttons
    "run_simulation": {
        "en": "▶️ Run Simulation",
        "pt": "▶️ Rodar Simulação"
    },
    "stop_simulation": {
        "en": "⏹️ Stop",
        "pt": "⏹️ Parar"
    },

    # Guide
    "guide_title": {
        "en": "📖 Quick Guide - What is this?",
        "pt": "📖 Guia Rápido - O que é isso?"
    },
    "guide_header": {
        "en": "**Pluribus** - Collective Intelligence Simulator",
        "pt": "**Pluribus** - Simulador de Inteligência Coletiva"
    },
    "guide_based_on": {
        "en": "Based on the Apple TV series where a collective mind emerges from independent agents.",
        "pt": "Baseado na série da Apple TV onde uma mente coletiva emerge de agentes independentes."
    },
    "guide_main_concepts": {
        "en": "Main Concepts",
        "pt": "Conceitos Principais"
    },
    "guide_problem": {
        "en": "The Problem:",
        "pt": "O Problema:"
    },
    "guide_problem_desc": {
        "en": "- Agents try to discover secret sequences\n- Each attempt costs energy\n- Agents learn from feedback (% accuracy)",
        "pt": "- Agentes tentam descobrir sequências secretas\n- Cada tentativa gasta energia\n- Agentes aprendem com feedback (% de acerto)"
    },
    "guide_communication_modes": {
        "en": "Communication Modes:",
        "pt": "Modos de Comunicação:"
    },
    "guide_hive_mode": {
        "en": "🐝 **HIVE**: Global collective mind - all share knowledge",
        "pt": "🐝 **HIVE**: Mente coletiva global - todos compartilham conhecimento"
    },
    "guide_local_mode": {
        "en": "🕸️ **LOCAL**: Only neighbors communicate - local emergence",
        "pt": "🕸️ **LOCAL**: Apenas vizinhos se comunicam - emergência local"
    },
    "guide_main_params": {
        "en": "Main Parameters",
        "pt": "Parâmetros Principais"
    },
    "guide_sync_title": {
        "en": "Collective Sync (0-100%)",
        "pt": "Sincronização Coletiva (0-100%)"
    },
    "guide_sync_desc": {
        "en": "- How much knowledge is shared between agents\n- 90%+ = Strong hivemind (fast convergence)\n- 30% = Individual autonomy (diverse exploration)",
        "pt": "- Quanto conhecimento é compartilhado entre agentes\n- 90%+ = Hivemind forte (convergência rápida)\n- 30% = Autonomia individual (exploração diversa)"
    },
    "guide_learning_title": {
        "en": "Learning Strength (0-100%)",
        "pt": "Força de Aprendizado (0-100%)"
    },
    "guide_learning_desc": {
        "en": "- How much the policy is adjusted each attempt\n- 20%+ = Learns fast (may oscillate)\n- 10% = Learns slowly (more stable)",
        "pt": "- Quanto a policy é ajustada a cada tentativa\n- 20%+ = Aprende rápido (pode oscilar)\n- 10% = Aprende devagar (mais estável)"
    },
    "guide_energy_title": {
        "en": "Energy",
        "pt": "Energia"
    },
    "guide_energy_desc": {
        "en": "- Limited resource per agent\n- Spends energy each attempt\n- Agents without energy die",
        "pt": "- Recurso limitado por agente\n- Gasta energia a cada tentativa\n- Agentes sem energia morrem"
    },
    "guide_recommended_presets": {
        "en": "Recommended Presets",
        "pt": "Presets Recomendados"
    },
    "guide_fast_hive_tip": {
        "en": "🚀 **Fast Hive**: Converges in ~3 ticks (good for testing)",
        "pt": "🚀 **Fast Hive**: Convergência em ~3 ticks (bom pra testar)"
    },
    "guide_balanced_tip": {
        "en": "⚖️ **Balanced**: Equilibrium (recommended for beginners)",
        "pt": "⚖️ **Balanced**: Equilíbrio (recomendado para iniciantes)"
    },
    "guide_slow_local_tip": {
        "en": "🐌 **Slow Local**: Gradual exploration (interesting to observe)",
        "pt": "🐌 **Slow Local**: Exploração gradual (interessante observar)"
    },
    "guide_chaos_tip": {
        "en": "🌪️ **Chaos**: Experiment (may not converge!)",
        "pt": "🌪️ **Chaos**: Experimento (pode não convergir!)"
    },
    "guide_tip": {
        "en": "💡 **Tip**: Start with \"Fast Hive\" to understand the basics!",
        "pt": "💡 **Dica**: Comece com \"Fast Hive\" pra entender o básico!"
    },

    # Preset selection
    "preset_title": {
        "en": "Simulation Preset",
        "pt": "Preset de Simulação"
    },
    "choose_preset": {
        "en": "Choose a preset:",
        "pt": "Escolha um preset:"
    },
    "preset_help": {
        "en": "Presets optimized by automated tests. Choose 'Custom' for full control.",
        "pt": "Presets otimizados por testes automáticos. Escolha 'Customizado' para controle total."
    },

    # Mode and strategy
    "mode_label": {
        "en": "Communication Mode",
        "pt": "Modo de Comunicação"
    },
    "mode_help": {
        "en": "HIVE: global collective mind. LOCAL: communication only with neighbors.",
        "pt": "HIVE: mente coletiva global. LOCAL: comunicação apenas com vizinhos."
    },
    "strategy_label": {
        "en": "Learning Strategy",
        "pt": "Estratégia de Aprendizado"
    },
    "strategy_help": {
        "en": "bandit: explores multiple actions. single_var: changes 1 variable at a time. explorer: epsilon-greedy.",
        "pt": "bandit: explora múltiplas ações. single_var: muda 1 variável por vez. explorer: epsilon-greedy."
    },

    # Sections
    "collective_mind": {
        "en": "🎯 Collective Mind",
        "pt": "🎯 Mente Coletiva"
    },
    "collective_sync_label": {
        "en": "Collective Sync (%)",
        "pt": "Sincronização Coletiva (%)"
    },
    "collective_sync_help": {
        "en": "How much % of knowledge is shared between agents. 100% = total hivemind.",
        "pt": "Quanto % de conhecimento é compartilhado entre agentes. 100% = hivemind total."
    },
    "learning_strength_label": {
        "en": "Learning Strength (%)",
        "pt": "Força de Aprendizado (%)"
    },
    "learning_strength_help": {
        "en": "How much % the policy is adjusted each attempt. Higher = learns faster (but may oscillate).",
        "pt": "Quanto % a policy é ajustada a cada tentativa. Maior = aprende mais rápido (mas pode oscilar)."
    },

    # Energy section
    "energy_section": {
        "en": "⚡ Energy",
        "pt": "⚡ Energia"
    },
    "initial_energy_label": {
        "en": "Initial Energy",
        "pt": "Energia Inicial"
    },
    "initial_energy_help": {
        "en": "Energy each agent starts with. Agents without energy die.",
        "pt": "Energia que cada agente começa. Agentes sem energia morrem."
    },
    "energy_per_try_label": {
        "en": "Energy per Try",
        "pt": "Energia por Tentativa"
    },
    "energy_per_try_help": {
        "en": "Energy spent on each attempt.",
        "pt": "Energia gasta a cada tentativa."
    },

    # Problem section
    "problem_section": {
        "en": "🧩 Problem",
        "pt": "🧩 Problema"
    },
    "num_agents_label": {
        "en": "Number of Agents",
        "pt": "Número de Agentes"
    },
    "sequence_length_label": {
        "en": "Sequence Length",
        "pt": "Tamanho da Sequência"
    },
    "alphabet_size_label": {
        "en": "Alphabet Size",
        "pt": "Tamanho do Alfabeto"
    },
    "num_recipes_label": {
        "en": "Number of Recipes",
        "pt": "Número de Receitas"
    },

    # Execution
    "execution_section": {
        "en": "⏱️ Execution",
        "pt": "⏱️ Execução"
    },
    "max_ticks_label": {
        "en": "Max Ticks",
        "pt": "Ticks Máximos"
    },

    # Topology
    "topology_section": {
        "en": "🕸️ Network (LOCAL mode)",
        "pt": "🕸️ Rede (modo LOCAL)"
    },
    "topology_type_label": {
        "en": "Topology",
        "pt": "Topologia"
    },
    "network_density_label": {
        "en": "Network Density (%)",
        "pt": "Densidade da Rede (%)"
    },
    "network_density_help": {
        "en": "% of possible connections. Higher = more communication.",
        "pt": "% de conexões possíveis. Maior = mais comunicação."
    },

    "guide_what_is": {
        "en": "What is Pluribus?",
        "pt": "O que é Pluribus?"
    },
    "guide_what_is_text": {
        "en": "Pluribus simulates collective intelligence emergence. Agents try to discover secret sequences (recipes) through trial and error, learning from each other.",
        "pt": "Pluribus simula emergência de inteligência coletiva. Agentes tentam descobrir sequências secretas (receitas) através de tentativa e erro, aprendendo uns com os outros."
    },
    "guide_modes": {
        "en": "Communication Modes",
        "pt": "Modos de Comunicação"
    },
    "guide_hive": {
        "en": "**HIVE** - Global collective mind. All agents share knowledge instantly. Fast convergence (~3 ticks) but low diversity.",
        "pt": "**HIVE** - Mente coletiva global. Todos agentes compartilham conhecimento instantaneamente. Convergência rápida (~3 ticks) mas baixa diversidade."
    },
    "guide_local": {
        "en": "**LOCAL** - Communication only between neighbors. Organic emergence (~10-50 ticks). High diversity but slower.",
        "pt": "**LOCAL** - Comunicação apenas entre vizinhos. Emergência orgânica (~10-50 ticks). Alta diversidade mas mais lento."
    },
    "guide_params": {
        "en": "Key Parameters",
        "pt": "Parâmetros Principais"
    },
    "guide_sync": {
        "en": "**Collective Sync**: How much agents share knowledge (0-100%). Higher = faster convergence.",
        "pt": "**Sincronização Coletiva**: Quanto os agentes compartilham conhecimento (0-100%). Maior = convergência mais rápida."
    },
    "guide_learning": {
        "en": "**Learning Strength**: How much agents learn from each attempt (0-100%). Sweet spot: 15-20%.",
        "pt": "**Força de Aprendizado**: Quanto os agentes aprendem de cada tentativa (0-100%). Sweet spot: 15-20%."
    },
    "guide_energy": {
        "en": "**Energy**: Limited resource. Each attempt costs energy. When depleted, agent stops.",
        "pt": "**Energia**: Recurso limitado. Cada tentativa custa energia. Quando esgota, agente para."
    },
    "guide_strategies": {
        "en": "Learning Strategies",
        "pt": "Estratégias de Aprendizado"
    },
    "guide_bandit": {
        "en": "**Bandit**: Reinforces what works. Fast but gets stuck in local maxima.",
        "pt": "**Bandit**: Reforça o que funciona. Rápido mas fica preso em máximos locais."
    },
    "guide_singlevar": {
        "en": "**Single Var**: Methodical - changes one variable at a time. Efficient.",
        "pt": "**Single Var**: Metódico - muda uma variável por vez. Eficiente."
    },
    "guide_explorer": {
        "en": "**Explorer**: High exploration initially, focuses later. Escapes local maxima.",
        "pt": "**Explorer**: Alta exploração inicialmente, foca depois. Escapa de máximos locais."
    },

    # Results
    "results": {
        "en": "Results",
        "pt": "Resultados"
    },
    "success": {
        "en": "✅ Success!",
        "pt": "✅ Sucesso!"
    },
    "failed": {
        "en": "❌ Failed",
        "pt": "❌ Falhou"
    },
    "winner_found": {
        "en": "Winner found at tick",
        "pt": "Vencedor encontrado no tick"
    },
    "winner_agent": {
        "en": "Winner agent",
        "pt": "Agente vencedor"
    },
    "no_solution": {
        "en": "No solution found within tick limit",
        "pt": "Nenhuma solução encontrada dentro do limite de ticks"
    },
    "discovered_sequence": {
        "en": "Discovered sequence",
        "pt": "Sequência descoberta"
    },
    "target_recipe": {
        "en": "Target recipe",
        "pt": "Receita alvo"
    },

    # Metrics
    "metrics": {
        "en": "Metrics",
        "pt": "Métricas"
    },
    "convergence_chart": {
        "en": "Convergence Evolution",
        "pt": "Evolução da Convergência"
    },
    "best_reward": {
        "en": "Best Reward",
        "pt": "Melhor Recompensa"
    },
    "avg_reward": {
        "en": "Average Reward",
        "pt": "Recompensa Média"
    },
    "tick": {
        "en": "Tick",
        "pt": "Tick"
    },
    "reward": {
        "en": "Reward",
        "pt": "Recompensa"
    },

    # Status messages
    "running": {
        "en": "Running simulation...",
        "pt": "Rodando simulação..."
    },
    "completed": {
        "en": "Simulation completed",
        "pt": "Simulação concluída"
    },
    "error": {
        "en": "Error during simulation",
        "pt": "Erro durante simulação"
    },

    # Plugins section
    "plugins": {
        "en": "Plugins",
        "pt": "Plugins"
    },
    "preset": {
        "en": "Preset",
        "pt": "Preset"
    },
    "select_preset_help": {
        "en": "Select a preset to automatically configure plugins",
        "pt": "Selecione um preset para configurar automaticamente os plugins"
    },
    "preset_plugins": {
        "en": "Plugins",
        "pt": "Plugins"
    },
    "custom_plugins": {
        "en": "Custom Plugins",
        "pt": "Plugins Customizados"
    },

    # Execution buttons
    "execute_simulation": {
        "en": "🚀 Execute Simulation",
        "pt": "🚀 Executar Simulação"
    },
    "show_detailed_progress": {
        "en": "Show detailed progress",
        "pt": "Mostrar progresso detalhado"
    },

    # Results section
    "recipes_to_discover": {
        "en": "Recipes to Discover",
        "pt": "Receitas a Descobrir"
    },
    "recipe": {
        "en": "Recipe",
        "pt": "Receita"
    },
    "active_plugins": {
        "en": "Active plugins",
        "pt": "Plugins ativos"
    },
    "solution_found": {
        "en": "🎉 SOLUTION FOUND at tick",
        "pt": "🎉 SOLUÇÃO ENCONTRADA no tick"
    },
    "winner_agent_label": {
        "en": "Winner Agent",
        "pt": "Agente Vencedor"
    },
    "total_attempts": {
        "en": "Total Attempts",
        "pt": "Tentativas Totais"
    },
    "sequence": {
        "en": "Sequence",
        "pt": "Sequência"
    },
    "all_agents_died": {
        "en": "💀 All agents died!",
        "pt": "💀 Todos os agentes morreram!"
    },
    "no_solution_found": {
        "en": "No solution found. Best",
        "pt": "Não encontrou solução. Melhor"
    },
    "plugin_statistics": {
        "en": "Plugin Statistics",
        "pt": "Estatísticas dos Plugins"
    },
    "detailed_analysis": {
        "en": "Detailed Analysis",
        "pt": "Análise Detalhada"
    },
    "progress": {
        "en": "Progress",
        "pt": "Progresso"
    },
    "agents": {
        "en": "Agents",
        "pt": "Agentes"
    },
    "evolution": {
        "en": "Evolution",
        "pt": "Evolução"
    },
    "alive_agents": {
        "en": "Alive Agents",
        "pt": "Agentes Vivos"
    },
    "best_match": {
        "en": "Best Match",
        "pt": "Best Match"
    },
    "avg_reward": {
        "en": "Avg Reward",
        "pt": "Recompensa Média"
    },
    "spent": {
        "en": "Spent",
        "pt": "Gasto"
    },
    "error_loading_plugin": {
        "en": "Error loading plugin",
        "pt": "Erro ao carregar plugin"
    },
}


class I18n:
    """Internationalization helper class."""

    def __init__(self, language: Language = "en"):
        self.language = language

    def t(self, key: str) -> str:
        """
        Translate a key to current language.

        Args:
            key: Translation key

        Returns:
            Translated string
        """
        if key not in TRANSLATIONS:
            return key  # Return key if translation not found
        return TRANSLATIONS[key].get(self.language, key)

    def set_language(self, language: Language):
        """Set the current language."""
        self.language = language
