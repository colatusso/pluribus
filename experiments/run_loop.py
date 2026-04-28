"""
Loop de simulacao com renderizacao live (arena + cronicas + chart).
Compartilhado entre UI Simples e UI Avancada.
"""
from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from arena import (
    build_arena_figure,
    build_recipe_strip,
    extract_events,
    snapshot_state,
)


def run_and_render(runner, num_ticks: int, sequence_length: int,
                   live_arena: bool = True, show_progress: bool = True,
                   labels: dict = None) -> bool:
    """
    Executa simulacao tick a tick renderizando live na pagina.

    Args:
        runner: SimulationRunner inicializado
        num_ticks: limite de ticks
        sequence_length: tamanho da receita
        live_arena: mostrar arena visual + log narrativo
        show_progress: mostrar chart de evolucao
        labels: dict opcional pra strings (i18n). Faz fallback pra PT.

    Returns:
        True se achou solucao, False caso contrario.
    """
    L = labels or {}
    t = lambda k, default: L.get(k, default)

    # Receitas
    st.markdown(f"### {t('recipes_to_discover', '🎯 Receita(s) a descobrir')}")
    for i, recipe in enumerate(runner.world.recipes):
        st.code(f"{t('recipe', 'Receita')} {i+1}: {recipe.pattern}")

    if runner.plugins:
        st.markdown(
            f"**{t('active_plugins', '🌶️ Temperos ativos')} "
            f"({len(runner.plugins)}):** "
            + ", ".join(p.get_name() for p in sorted(runner.plugins, key=lambda x: x.priority))
        )

    progress_bar = st.progress(0)
    status_text = st.empty()

    if live_arena:
        recipe_placeholder = st.empty()
        arena_col, log_col = st.columns([3, 2])
        with arena_col:
            arena_placeholder = st.empty()
        with log_col:
            st.markdown(f"### 📜 {t('chronicles', 'Cronicas')}")
            log_placeholder = st.empty()
        chart_placeholder = st.empty()
    else:
        recipe_placeholder = None
        arena_placeholder = None
        log_placeholder = None
        chart_placeholder = st.empty()

    history = {"tick": [], "best_match": [], "avg_reward": [], "num_agents": []}
    narrative: List[str] = []
    prev_state = None
    recipe_pattern = runner.world.recipes[0].pattern if runner.world.recipes else []

    found_solution = False
    RENDER_EVERY = 3 if live_arena else 5

    for tick in range(num_ticks):
        found_solution = runner.run_single_tick()

        history["tick"].append(tick)
        history["best_match"].append(runner.get_best_match())
        avg = sum(a.best_reward for a in runner.agents) / len(runner.agents) if runner.agents else 0
        history["avg_reward"].append(avg)
        history["num_agents"].append(len(runner.agents))

        curr_state = snapshot_state(runner)
        new_events = extract_events(prev_state, curr_state, tick, sequence_length)
        if new_events:
            narrative.extend(new_events)
            narrative = narrative[-40:]
        prev_state = curr_state

        if tick % RENDER_EVERY == 0 or found_solution:
            progress_bar.progress((tick + 1) / num_ticks)
            status_text.text(
                f"{t('tick', 'Tick')} {tick} | "
                f"{t('best_match', 'Melhor match')}: {runner.get_best_match()}/{sequence_length} | "
                f"{t('agents', 'Agentes')}: {len(runner.agents)} | "
                f"{t('spent', 'Gasto')}: {runner.get_total_spent():.0f}"
            )

            if live_arena:
                best_seq = None
                if runner.agents:
                    best_seq = max(runner.agents, key=lambda a: a.best_reward).best_sequence
                recipe_placeholder.plotly_chart(
                    build_recipe_strip(recipe_pattern, best_seq),
                    use_container_width=True,
                    key=f"recipe_{tick}",
                )
                arena_placeholder.plotly_chart(
                    build_arena_figure(runner, last_winner_id=curr_state.get("best_id")),
                    use_container_width=True,
                    key=f"arena_{tick}",
                )
                if narrative:
                    log_placeholder.markdown(
                        "\n".join(f"- {line}" for line in reversed(narrative))
                    )

            if show_progress and len(history["tick"]) > 1:
                df = pd.DataFrame(history)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["tick"], y=df["best_match"],
                                         name=t('best_match', 'Melhor match'),
                                         line=dict(color="#00ff00", width=2)))
                fig.add_trace(go.Scatter(x=df["tick"], y=df["avg_reward"],
                                         name=t('avg_reward', 'Reward medio'),
                                         line=dict(color="#ffaa00", width=1, dash="dot")))
                fig.update_layout(title=t('progress', 'Progresso'),
                                  xaxis_title=t('tick', 'Tick'),
                                  yaxis_title="Score",
                                  template="plotly_dark", height=260)
                chart_placeholder.plotly_chart(fig, use_container_width=True, key=f"chart_{tick}")

        if found_solution or not runner.agents:
            break

    st.markdown("---")
    _render_results(runner, sequence_length, num_agents=runner.config.num_agents,
                    found_solution=found_solution, history=history, t=t)
    return found_solution


def _render_results(runner, sequence_length, num_agents, found_solution, history, t):
    if found_solution:
        # Frase narrativa em vez de metricas crus
        agents_alive = len(runner.agents)
        deaths = num_agents - agents_alive
        death_phrase = f" — {deaths} ficaram pelo caminho." if deaths > 0 else ""
        st.success(
            f"🎯 Agente **#{runner.winner_agent.node_id}** cracou em "
            f"**{runner.winner_tick} rodadas**{death_phrase}"
        )

        with st.expander("📊 Numeros detalhados"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Agente vencedor", f"#{runner.winner_agent.node_id}")
            with col2:
                st.metric("Tentativas totais", sum(a.num_attempts for a in runner.agents))
            with col3:
                total_spent = runner.get_total_spent()
                initial_total = num_agents * runner.config.initial_balance
                roi = ((initial_total - total_spent) / initial_total * 100) if initial_total else 0
                st.metric("Energia restante", f"{roi:+.1f}%")
            st.code(f"Sequencia: {runner.winner_sequence}")
    else:
        if not runner.agents:
            st.error("💀 Todos morreram. A simulacao nao sobreviveu.")
        else:
            best = runner.get_best_match()
            st.warning(
                f"⏳ Acabou o tempo. Chegaram em **{best}/{sequence_length}** — "
                f"perto, mas nao o suficiente."
            )

    if runner.plugins:
        with st.expander("🔌 Stats dos temperos"):
            for plugin in sorted(runner.plugins, key=lambda x: x.priority):
                stats = plugin.get_stats()
                if stats:
                    st.markdown(f"**{plugin.get_name()}**")
                    for key, value in stats.items():
                        st.write(f"  • {key}: {value}")

    if len(history["tick"]) > 1:
        with st.expander("📈 Analise detalhada"):
            tab1, tab2 = st.tabs(["Progresso", "Agentes vivos"])
            with tab1:
                df = pd.DataFrame(history)
                fig = px.line(df, x="tick", y=["best_match", "avg_reward"],
                              title="Evolucao", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            with tab2:
                fig = px.area(df, x="tick", y="num_agents",
                              title="Agentes vivos", template="plotly_dark")
                fig.update_traces(fill='tozeroy')
                st.plotly_chart(fig, use_container_width=True)
