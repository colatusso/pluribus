"""
Pluribus GUI - Streamlit interface for collective mind simulation.

Usage:
    streamlit run experiments/gui.py
"""
import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation.config import SimulationConfig
from src.simulation.runner import SimulationRunner
from src.utils.i18n import I18n, Language
from src.plugins.presets import PRESETS, list_presets, get_preset
from src.plugins import (
    PLUGIN_REGISTRY,
    get_plugin,
    # Environment
    DisasterPlugin,
    SeasonPlugin,
    MigrationPlugin,
    PollutionPlugin,
    # Economy
    MarketPlugin,
    TaxPlugin,
    InvestmentPlugin,
    # Social
    TrustPlugin,
    GossipPlugin,
    AlliancePlugin,
    TeachingPlugin,
    # Behavior
    MoodPlugin,
    FatiguePlugin,
    RiskPlugin,
    MemoryDecayPlugin,
    # Evolution
    GeneticPlugin,
    SpeciationPlugin,
    AdaptationPlugin,
    # Communication
    LanguagePlugin,
    CensorshipPlugin,
    # Core
    DeathPlugin,
)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_plugin_section(category: str, plugins_config: dict) -> list:
    """Cria secao de plugins por categoria"""
    active_plugins = []

    with st.expander(f"{category}", expanded=False):
        for plugin_name, plugin_info in plugins_config.items():
            col1, col2 = st.columns([1, 3])

            with col1:
                enabled = st.checkbox(
                    plugin_info["label"],
                    key=f"plugin_{plugin_name}",
                    help=plugin_info["description"]
                )

            if enabled:
                with col2:
                    params = {}
                    for param_name, param_config in plugin_info.get("params", {}).items():
                        if param_config["type"] == "float":
                            params[param_name] = st.slider(
                                param_config["label"],
                                min_value=param_config["min"],
                                max_value=param_config["max"],
                                value=param_config["default"],
                                step=param_config.get("step", 0.01),
                                key=f"{plugin_name}_{param_name}"
                            )
                        elif param_config["type"] == "int":
                            params[param_name] = st.slider(
                                param_config["label"],
                                min_value=param_config["min"],
                                max_value=param_config["max"],
                                value=param_config["default"],
                                key=f"{plugin_name}_{param_name}"
                            )
                        elif param_config["type"] == "select":
                            params[param_name] = st.selectbox(
                                param_config["label"],
                                options=param_config["options"],
                                key=f"{plugin_name}_{param_name}"
                            )
                        elif param_config["type"] == "bool":
                            params[param_name] = st.checkbox(
                                param_config["label"],
                                value=param_config["default"],
                                key=f"{plugin_name}_{param_name}"
                            )

                    active_plugins.append(get_plugin(plugin_name, **params))

    return active_plugins


def main():
    st.set_page_config(
        page_title="Pluribus - Collective Mind Simulation",
        page_icon="🧠",
        layout="wide"
    )

    # Initialize i18n
    if 'language' not in st.session_state:
        st.session_state.language = 'en'

    i18n = I18n(st.session_state.language)

    st.title(f"🧠 {i18n.t('app_title')}")
    st.caption(i18n.t('app_subtitle'))
    st.markdown("---")

    # Sidebar with configuration
    with st.sidebar:
        # Language selector at the top
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write(i18n.t('language') + ":")
        with col2:
            language = st.selectbox(
                "",
                options=['en', 'pt'],
                index=0 if st.session_state.language == 'en' else 1,
                format_func=lambda x: "🇺🇸 English" if x == 'en' else "🇧🇷 Português",
                label_visibility="collapsed"
            )
            if language != st.session_state.language:
                st.session_state.language = language
                st.rerun()

        st.markdown("---")
        st.header(f"🎮 {i18n.t('preset_selector')}")

        # BOTÃO DE GUIA
        with st.expander(i18n.t('guide_title'), expanded=False):
            guide_text = f"""
            ### 🎯 {i18n.t('guide_header')}

            {i18n.t('guide_based_on')}

            ---

            #### 🧠 **{i18n.t('guide_main_concepts')}**

            **{i18n.t('guide_problem')}**
            {i18n.t('guide_problem_desc')}

            **{i18n.t('guide_communication_modes')}**
            - {i18n.t('guide_hive_mode')}
            - {i18n.t('guide_local_mode')}

            ---

            #### ⚙️ **{i18n.t('guide_main_params')}**

            **{i18n.t('guide_sync_title')}**
            {i18n.t('guide_sync_desc')}

            **{i18n.t('guide_learning_title')}**
            {i18n.t('guide_learning_desc')}

            **{i18n.t('guide_energy_title')}**
            {i18n.t('guide_energy_desc')}

            ---

            #### 🎮 **{i18n.t('guide_recommended_presets')}**

            - {i18n.t('guide_fast_hive_tip')}
            - {i18n.t('guide_balanced_tip')}
            - {i18n.t('guide_slow_local_tip')}
            - {i18n.t('guide_chaos_tip')}

            ---

            {i18n.t('guide_tip')}
            """
            st.markdown(guide_text)

        st.markdown("---")

        # PRESET SELECTOR
        st.subheader(i18n.t('preset_title'))

        # Build preset options dynamically
        preset_options = [
            i18n.t('custom'),
            f"{i18n.t('fast_hive')} {i18n.t('recommended')}",
            i18n.t('balanced'),
            i18n.t('slow_local'),
            i18n.t('chaos')
        ]

        config_preset = st.selectbox(
            i18n.t('choose_preset'),
            preset_options,
            help=i18n.t('preset_help')
        )

        # Mapeia presets para valores (VALORES CORRIGIDOS BASEADO NOS TESTES)
        preset_configs = {
            preset_options[1]: {  # Fast Hive (Recomendado)
                "mode": "hive",
                "collective_sync": 90,
                "learning_strength": 20,
                "energy": 500,
                "num_ticks": 100,
                "desc_key": "fast_hive_desc"
            },
            preset_options[2]: {  # Balanced
                "mode": "hive",
                "collective_sync": 70,
                "learning_strength": 18,
                "energy": 800,
                "num_ticks": 150,
                "desc_key": "balanced_desc"
            },
            preset_options[3]: {  # Slow Local
                "mode": "local",
                "collective_sync": 30,
                "learning_strength": 10,
                "energy": 1000,
                "num_ticks": 200,
                "network_density": 20,
                "desc_key": "slow_local_desc"
            },
            preset_options[4]: {  # Chaos
                "mode": "local",
                "collective_sync": 10,
                "learning_strength": 5,
                "energy": 2000,
                "num_ticks": 500,
                "network_density": 15,
                "desc_key": "chaos_desc"
            },
        }

        # Valores default ou do preset
        if config_preset != preset_options[0]:
            preset_vals = preset_configs[config_preset]
            mode_default = preset_vals.get("mode", "hive")
            sync_default = preset_vals.get("collective_sync", 50)
            learning_default = preset_vals.get("learning_strength", 15)
            energy_default = preset_vals.get("energy", 800)
            ticks_default = preset_vals.get("num_ticks", 500)
            density_default = preset_vals.get("network_density", 30)
            disabled = True  # Desabilita sliders no modo preset

            # Mostra descrição do preset
            desc_key = preset_vals.get('desc_key', '')
            if desc_key:
                st.info(f"ℹ️ {i18n.t(desc_key)}")
        else:
            mode_default = "hive"
            sync_default = 50
            learning_default = 15
            energy_default = 800
            ticks_default = 500
            density_default = 30
            disabled = False

        st.markdown("---")

        # Modo
        mode = st.selectbox(
            i18n.t('mode_label'),
            options=["hive", "local"],
            index=0 if mode_default == "hive" else 1,
            help=i18n.t('mode_help'),
            disabled=disabled
        )

        # Strategy
        strategy = st.selectbox(
            i18n.t('strategy_label'),
            options=["bandit", "single_var", "explorer"],
            index=0,
            help=i18n.t('strategy_help'),
            disabled=disabled
        )

        st.markdown("---")
        st.subheader(i18n.t('collective_mind'))

        collective_sync = st.slider(
            i18n.t('collective_sync_label'),
            0, 100, sync_default,
            help=i18n.t('collective_sync_help'),
            disabled=disabled
        )

        learning_strength = st.slider(
            i18n.t('learning_strength_label'),
            0, 100, learning_default,
            help=i18n.t('learning_strength_help'),
            disabled=disabled
        )

        st.markdown("---")
        st.subheader(i18n.t('energy_section'))

        energy = st.slider(
            i18n.t('initial_energy_label'),
            100, 2000, energy_default, 100,
            help=i18n.t('initial_energy_help'),
            disabled=disabled
        )

        energy_per_try = st.slider(
            i18n.t('energy_per_try_label'),
            1, 10, 1,
            help=i18n.t('energy_per_try_help'),
            disabled=disabled
        )

        st.markdown("---")
        st.subheader(i18n.t('problem_section'))

        num_agents = st.slider(i18n.t('num_agents_label'), 5, 100, 20, disabled=disabled)
        sequence_length = st.slider(i18n.t('sequence_length_label'), 4, 20, 8, disabled=disabled)
        alphabet_size = st.slider(i18n.t('alphabet_size_label'), 2, 10, 4, disabled=disabled)
        num_recipes = st.slider(i18n.t('num_recipes_label'), 1, 5, 1, disabled=disabled)

        st.markdown("---")
        st.subheader(i18n.t('execution_section'))

        num_ticks = st.slider(i18n.t('max_ticks_label'), 50, 2000, ticks_default, disabled=disabled)

        # Topologia (so para local)
        if mode == "local":
            st.markdown("---")
            st.subheader(i18n.t('topology_section'))
            topology_type = st.selectbox(i18n.t('topology_type_label'), ["ring", "grid", "random"], disabled=disabled)
            network_density = st.slider(
                i18n.t('network_density_label'),
                5, 100, density_default,
                help=i18n.t('network_density_help'),
                disabled=disabled
            )
        else:
            topology_type = "ring"
            network_density = 30

    # Area principal - Plugins
    st.header(i18n.t('plugins'))

    # Seletor de Presets
    preset_options = [i18n.t('custom')] + [f"{p['icon']} {p['name']}" for p in list_presets()]
    preset_keys = ["custom"] + [p['key'] for p in list_presets()]

    selected_preset_idx = st.selectbox(
        f"🎮 {i18n.t('preset')}",
        range(len(preset_options)),
        format_func=lambda x: preset_options[x],
        help=i18n.t('select_preset_help')
    )

    selected_preset_key = preset_keys[selected_preset_idx]

    # Mostra descrição do preset selecionado
    if selected_preset_key != "custom":
        preset_data = get_preset(selected_preset_key)
        st.info(f"**{preset_data['name']}**: {preset_data['description']}")

        # Mostra plugins do preset
        preset_plugins = list(preset_data['plugins'].keys())
        st.caption(f"{i18n.t('preset_plugins')}: {', '.join(preset_plugins)}")

        # Aplica overrides do preset no sidebar
        if 'config_overrides' in preset_data:
            overrides = preset_data['config_overrides']
            if 'initial_balance' in overrides:
                initial_balance = overrides['initial_balance']
            if 'cost_per_attempt' in overrides:
                cost_per_attempt = overrides['cost_per_attempt']

    st.markdown("---")

    # Definicao dos plugins por categoria
    plugins_categories = {
        "🌍 Ambiente": {
            "disaster": {
                "label": "Disaster",
                "description": "Catastrofes aleatorias resetam progresso",
                "params": {
                    "probability": {"type": "float", "label": "Probabilidade", "min": 0.0, "max": 0.2, "default": 0.02},
                    "reset_factor": {"type": "float", "label": "Reset Factor", "min": 0.0, "max": 1.0, "default": 0.3},
                    "balance_damage": {"type": "float", "label": "Dano Balance", "min": 0.0, "max": 1.0, "default": 0.2},
                }
            },
            "season": {
                "label": "Season",
                "description": "Ciclos sazonais variam custo e aprendizado",
                "params": {
                    "cycle_length": {"type": "int", "label": "Ciclo (ticks)", "min": 20, "max": 500, "default": 100},
                    "cost_amplitude": {"type": "float", "label": "Amplitude Custo", "min": 0.0, "max": 1.0, "default": 0.5},
                }
            },
            "pollution": {
                "label": "Pollution",
                "description": "Erros poluem espaco de busca",
                "params": {
                    "pollution_rate": {"type": "float", "label": "Taxa Poluicao", "min": 0.0, "max": 0.1, "default": 0.01},
                    "decay_rate": {"type": "float", "label": "Decay", "min": 0.0, "max": 0.1, "default": 0.005},
                }
            },
            "migration": {
                "label": "Migration",
                "description": "Agentes migram para novos vizinhos (APENAS modo LOCAL)",
                "params": {
                    "migration_threshold": {"type": "float", "label": "Threshold", "min": 0.0, "max": 1.0, "default": 0.3},
                },
                "requires_mode": "local"
            },
        },
        "💰 Economia": {
            "market": {
                "label": "Market",
                "description": "Compra e venda de informacao",
                "params": {
                    "base_price": {"type": "float", "label": "Preco Base", "min": 1.0, "max": 100.0, "default": 10.0},
                    "info_quality": {"type": "float", "label": "Qualidade Info", "min": 0.0, "max": 1.0, "default": 0.8},
                }
            },
            "tax": {
                "label": "Tax",
                "description": "Impostos progressivos com redistribuicao",
                "params": {
                    "tax_rate": {"type": "float", "label": "Taxa Imposto", "min": 0.0, "max": 0.5, "default": 0.1},
                    "redistribution": {"type": "select", "label": "Redistribuicao", "options": ["equal", "proportional"]},
                }
            },
            "investment": {
                "label": "Investment",
                "description": "Investimentos com juros",
                "params": {
                    "interest_rate": {"type": "float", "label": "Taxa Juros", "min": 0.0, "max": 0.1, "default": 0.02},
                    "investment_ratio": {"type": "float", "label": "Ratio Investimento", "min": 0.0, "max": 0.8, "default": 0.3},
                }
            },
        },
        "👥 Social": {
            "trust": {
                "label": "Trust",
                "description": "Reputacao baseada em ajuda",
                "params": {
                    "initial_trust": {"type": "float", "label": "Trust Inicial", "min": 0.0, "max": 1.0, "default": 0.5},
                    "trust_gain": {"type": "float", "label": "Ganho Trust", "min": 0.0, "max": 0.5, "default": 0.1},
                }
            },
            "gossip": {
                "label": "Gossip",
                "description": "Fofoca e desinformacao",
                "params": {
                    "lie_probability": {"type": "float", "label": "Prob Mentira", "min": 0.0, "max": 0.5, "default": 0.1},
                    "detection_chance": {"type": "float", "label": "Chance Deteccao", "min": 0.0, "max": 1.0, "default": 0.3},
                }
            },
            "alliance": {
                "label": "Alliance",
                "description": "Formacao de grupos/faccoes",
                "params": {
                    "num_alliances": {"type": "int", "label": "Num Aliancas", "min": 2, "max": 10, "default": 3},
                    "betrayal_chance": {"type": "float", "label": "Chance Traicao", "min": 0.0, "max": 0.2, "default": 0.05},
                }
            },
            "teaching": {
                "label": "Teaching",
                "description": "Mentoria entre agentes",
                "params": {
                    "teaching_cost": {"type": "float", "label": "Custo Ensino", "min": 0.0, "max": 50.0, "default": 5.0},
                    "learning_boost": {"type": "float", "label": "Boost Aprendizado", "min": 0.0, "max": 1.0, "default": 0.4},
                }
            },
        },
        "🧠 Comportamento": {
            "mood": {
                "label": "Mood",
                "description": "Moral afeta aprendizado",
                "params": {
                    "initial_mood": {"type": "float", "label": "Moral Inicial", "min": 0.0, "max": 1.0, "default": 0.7},
                    "chaos_threshold": {"type": "float", "label": "Threshold Caos", "min": 0.0, "max": 0.5, "default": 0.3},
                }
            },
            "fatigue": {
                "label": "Fatigue",
                "description": "Cansaco reduz performance",
                "params": {
                    "fatigue_rate": {"type": "float", "label": "Taxa Fadiga", "min": 0.0, "max": 0.2, "default": 0.05},
                    "rest_threshold": {"type": "float", "label": "Threshold Descanso", "min": 0.5, "max": 1.0, "default": 0.8},
                }
            },
            "risk": {
                "label": "Risk",
                "description": "Perfis de aversao ao risco",
                "params": {
                    "risk_variance": {"type": "float", "label": "Variancia Risco", "min": 0.0, "max": 0.5, "default": 0.3},
                    "adaptive_risk": {"type": "bool", "label": "Risco Adaptativo", "default": True},
                }
            },
            "memory_decay": {
                "label": "MemoryDecay",
                "description": "Esquecimento gradual",
                "params": {
                    "decay_rate": {"type": "float", "label": "Taxa Decay", "min": 0.0, "max": 0.1, "default": 0.02},
                }
            },
        },
        "🧬 Evolucao": {
            "genetic": {
                "label": "Genetic",
                "description": "Heranca genetica e mutacao",
                "params": {
                    "mutation_rate": {"type": "float", "label": "Taxa Mutacao", "min": 0.0, "max": 0.5, "default": 0.1},
                    "inheritance_factor": {"type": "float", "label": "Heranca", "min": 0.0, "max": 1.0, "default": 0.8},
                }
            },
            "speciation": {
                "label": "Speciation",
                "description": "Divergencia em especies",
                "params": {
                    "num_species": {"type": "int", "label": "Num Especies", "min": 2, "max": 10, "default": 3},
                    "divergence_rate": {"type": "float", "label": "Taxa Divergencia", "min": 0.0, "max": 0.5, "default": 0.1},
                }
            },
            "adaptation": {
                "label": "Adaptation",
                "description": "Parametros evoluem com sucesso",
                "params": {
                    "adaptation_rate": {"type": "float", "label": "Taxa Adaptacao", "min": 0.0, "max": 0.5, "default": 0.1},
                    "desperation_threshold": {"type": "int", "label": "Threshold Desespero", "min": 5, "max": 50, "default": 10},
                }
            },
        },
        "📡 Comunicacao": {
            "language": {
                "label": "Language",
                "description": "Evolucao de linguagem",
                "params": {
                    "compression_rate": {"type": "float", "label": "Taxa Compressao", "min": 0.0, "max": 0.1, "default": 0.01},
                    "max_compression": {"type": "float", "label": "Max Compressao", "min": 0.0, "max": 1.0, "default": 0.5},
                }
            },
            "censorship": {
                "label": "Censorship",
                "description": "Censura de informacao",
                "params": {
                    "censor_ratio": {"type": "float", "label": "Ratio Censores", "min": 0.0, "max": 0.5, "default": 0.1},
                    "accuracy": {"type": "float", "label": "Precisao", "min": 0.0, "max": 1.0, "default": 0.6},
                }
            },
        },
        "💀 Core": {
            "death": {
                "label": "Death",
                "description": "Remove agentes sem creditos",
                "params": {}
            },
        },
    }

    # Cria plugins ativos
    all_plugins = []

    # Se um preset foi selecionado, cria plugins do preset
    if selected_preset_key != "custom":
        preset_data = get_preset(selected_preset_key)
        for plugin_name, plugin_params in preset_data['plugins'].items():
            try:
                plugin = get_plugin(plugin_name, **plugin_params)
                all_plugins.append(plugin)
            except Exception as e:
                st.warning(f"{i18n.t('error_loading_plugin')} '{plugin_name}': {e}")

        # Mostra os plugins do preset (somente leitura)
        st.markdown(f"**{i18n.t('preset_plugins')}:**")
        for plugin in all_plugins:
            params = plugin.get_params()
            params_str = ", ".join(f"{k}={v}" for k, v in params.items()) if params else "default"
            st.caption(f"• {plugin.get_name()}: {params_str}")
    else:
        # Modo customizado - mostra todos os plugins para selecao
        cols = st.columns(3)
        categories = list(plugins_categories.items())

        for i, (cat_name, cat_plugins) in enumerate(categories):
            with cols[i % 3]:
                plugins = create_plugin_section(cat_name, cat_plugins)
                all_plugins.extend(plugins)

    st.markdown("---")

    # Botao executar
    col1, col2 = st.columns([2, 1])

    with col1:
        run_button = st.button(i18n.t('execute_simulation'), type="primary", use_container_width=True)

    with col2:
        show_progress = st.checkbox(i18n.t('show_detailed_progress'), value=True)

    if run_button:
        # Monta config
        config = SimulationConfig(
            num_agents=num_agents,
            num_ticks=num_ticks,
            sequence_length=sequence_length,
            alphabet_size=alphabet_size,
            num_recipes=num_recipes,
            mode=mode,
            strategy=strategy,
            collective_sync=collective_sync,
            learning_strength=learning_strength,
            energy=energy,
            energy_per_try=energy_per_try,
            topology_type=topology_type,
            network_density=network_density,
            log_interval=1,
            output_file="gui_results.csv"
        )

        # Cria runner com plugins
        runner = SimulationRunner(config, plugins=all_plugins)

        # Mostra receitas
        st.markdown(f"### {i18n.t('recipes_to_discover')}")
        for i, recipe in enumerate(runner.world.recipes):
            st.code(f"{i18n.t('recipe')} {i+1}: {recipe.pattern}")

        # Mostra plugins ativos
        if all_plugins:
            st.markdown(f"**{i18n.t('active_plugins')} ({len(all_plugins)}):** " +
                       ", ".join(p.get_name() for p in sorted(all_plugins, key=lambda x: x.priority)))

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        chart_placeholder = st.empty()

        # Historico
        history = {"tick": [], "best_match": [], "avg_reward": [], "num_agents": []}

        # Roda simulacao
        found_solution = False
        for tick in range(num_ticks):
            found_solution = runner.run_single_tick()

            history["tick"].append(tick)
            history["best_match"].append(runner.get_best_match())
            avg = sum(a.best_reward for a in runner.agents) / len(runner.agents) if runner.agents else 0
            history["avg_reward"].append(avg)
            history["num_agents"].append(len(runner.agents))

            if tick % 5 == 0 or found_solution:
                progress_bar.progress((tick + 1) / num_ticks)
                status_text.text(
                    f"{i18n.t('tick')} {tick} | {i18n.t('best_match')}: {runner.get_best_match()}/{sequence_length} | "
                    f"{i18n.t('agents')}: {len(runner.agents)} | {i18n.t('spent')}: {runner.get_total_spent():.0f}"
                )

                if show_progress and len(history["tick"]) > 1:
                    df = pd.DataFrame(history)
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df["tick"], y=df["best_match"], name=i18n.t('best_match'), line=dict(color="#00ff00", width=2)))
                    fig.add_trace(go.Scatter(x=df["tick"], y=df["avg_reward"], name=i18n.t('avg_reward'), line=dict(color="#ffaa00", width=1, dash="dot")))
                    fig.update_layout(title=i18n.t('progress'), xaxis_title=i18n.t('tick'), yaxis_title="Score", template="plotly_dark", height=300)
                    chart_placeholder.plotly_chart(fig, use_container_width=True)

            if found_solution or not runner.agents:
                break

        # Resultados finais
        st.markdown("---")

        if found_solution:
            st.success(f"{i18n.t('solution_found')} {runner.winner_tick}!")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(i18n.t('winner_agent_label'), f"#{runner.winner_agent.node_id}")
            with col2:
                st.metric(i18n.t('total_attempts'), sum(a.num_attempts for a in runner.agents))
            with col3:
                total_spent = runner.get_total_spent()
                initial_total = num_agents * energy
                roi = ((initial_total - total_spent) / initial_total * 100)
                st.metric("ROI", f"{roi:+.1f}%")

            st.code(f"{i18n.t('sequence')}: {runner.winner_sequence}")
        else:
            if not runner.agents:
                st.error(i18n.t('all_agents_died'))
            else:
                st.warning(f"{i18n.t('no_solution_found')}: {runner.get_best_match()}/{sequence_length}")

        # Stats dos plugins
        if all_plugins:
            st.markdown(f"### {i18n.t('plugin_statistics')}")
            plugin_cols = st.columns(min(3, len(all_plugins)))
            for i, plugin in enumerate(sorted(all_plugins, key=lambda x: x.priority)):
                with plugin_cols[i % len(plugin_cols)]:
                    stats = plugin.get_stats()
                    if stats:
                        with st.expander(f"📊 {plugin.get_name()}", expanded=True):
                            for key, value in stats.items():
                                st.write(f"**{key}:** {value}")

        # Graficos finais
        if len(history["tick"]) > 1:
            st.markdown(f"### {i18n.t('detailed_analysis')}")
            tab1, tab2 = st.tabs([i18n.t('progress'), i18n.t('agents')])

            with tab1:
                df = pd.DataFrame(history)
                fig = px.line(df, x="tick", y=["best_match", "avg_reward"], title=i18n.t('evolution'), template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                fig = px.area(df, x="tick", y="num_agents", title=i18n.t('alive_agents'), template="plotly_dark")
                fig.update_traces(fill='tozeroy')
                st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
