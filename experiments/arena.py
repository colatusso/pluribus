"""
Pluribus Live Arena — visualizacao em tempo real e log narrativo.

Recebe um SimulationRunner e produz:
- Figura Plotly da "arena" (agentes como nodes, conexoes como arestas).
- Eventos narrativos derivados de diffs entre snapshots de estado.
"""
import math
from typing import Dict, List, Optional, Tuple

import plotly.graph_objects as go


def _circle_layout(num_agents: int, radius: float = 1.5) -> List[Tuple[float, float]]:
    if num_agents <= 0:
        return []
    return [
        (radius * math.cos(2 * math.pi * i / num_agents),
         radius * math.sin(2 * math.pi * i / num_agents))
        for i in range(num_agents)
    ]


def build_arena_figure(runner, last_winner_id: Optional[int] = None) -> go.Figure:
    agents = runner.agents
    seq_len = max(1, runner.config.sequence_length)
    fig = go.Figure()

    if not agents:
        fig.add_annotation(
            text="💀 todos os agentes morreram",
            showarrow=False,
            font=dict(size=20, color="#ff5566"),
        )
        fig.update_layout(
            template="plotly_dark", height=500, showlegend=False,
            plot_bgcolor="#0a0a18", paper_bgcolor="#0a0a18",
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        return fig

    coords = _circle_layout(len(agents))
    pos: Dict[int, Tuple[float, float]] = {
        agent.node_id: coords[i] for i, agent in enumerate(agents)
    }

    if runner.config.mode == "hive":
        edge_x, edge_y = [], []
        for agent in agents:
            x, y = pos[agent.node_id]
            edge_x += [0, x, None]
            edge_y += [0, y, None]
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(color="rgba(150,120,255,0.18)", width=1),
            hoverinfo="skip", showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=[0], y=[0], mode="markers+text",
            marker=dict(size=34, color="#7a4dff", symbol="hexagon",
                        line=dict(color="white", width=2)),
            text=["HIVE"], textposition="middle center",
            textfont=dict(color="white", size=10),
            hoverinfo="skip", showlegend=False,
        ))
    else:
        edge_x, edge_y = [], []
        seen = set()
        for agent in agents:
            x1, y1 = pos[agent.node_id]
            for nb_id in agent.neighbors:
                if nb_id not in pos:
                    continue
                key = tuple(sorted((agent.node_id, nb_id)))
                if key in seen:
                    continue
                seen.add(key)
                x2, y2 = pos[nb_id]
                edge_x += [x1, x2, None]
                edge_y += [y1, y2, None]
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(color="rgba(150,200,255,0.25)", width=1),
            hoverinfo="skip", showlegend=False,
        ))

    xs, ys, colors, sizes, texts, hover = [], [], [], [], [], []
    for agent in agents:
        x, y = pos[agent.node_id]
        xs.append(x)
        ys.append(y)
        # reward parcial vem em matches absolutos (0..L); vitoria = 100 → satura em L
        c = seq_len if agent.best_reward >= 100.0 else min(agent.best_reward, seq_len)
        colors.append(c)
        ratio = max(0.15, min(1.0, agent.balance / max(1.0, agent.initial_balance)))
        sizes.append(14 + 22 * ratio)
        texts.append(str(agent.node_id))
        display_best = seq_len if agent.best_reward >= 100.0 else int(agent.best_reward)
        hover.append(
            f"Agent #{agent.node_id}<br>"
            f"Best: {display_best}/{seq_len}<br>"
            f"Balance: {agent.balance:.0f}/{agent.initial_balance:.0f}<br>"
            f"Tentativas: {agent.num_attempts}"
        )

    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text",
        marker=dict(
            size=sizes, color=colors, colorscale="Viridis",
            cmin=0, cmax=seq_len,
            line=dict(color="rgba(255,255,255,0.45)", width=1),
            colorbar=dict(title="Match", thickness=10, x=1.02),
        ),
        text=texts, textposition="middle center",
        textfont=dict(color="white", size=9),
        hovertext=hover, hoverinfo="text", showlegend=False,
    ))

    if last_winner_id is not None and last_winner_id in pos:
        wx, wy = pos[last_winner_id]
        fig.add_trace(go.Scatter(
            x=[wx], y=[wy], mode="markers",
            marker=dict(size=52, symbol="star",
                        color="rgba(255,215,0,0)",
                        line=dict(color="#ffd700", width=3)),
            hoverinfo="skip", showlegend=False,
        ))

    fig.update_layout(
        template="plotly_dark", height=520, showlegend=False,
        xaxis=dict(visible=False, range=[-2.1, 2.1]),
        yaxis=dict(visible=False, range=[-2.1, 2.1],
                   scaleanchor="x", scaleratio=1),
        margin=dict(l=10, r=60, t=10, b=10),
        plot_bgcolor="#0a0a18", paper_bgcolor="#0a0a18",
    )
    return fig


def snapshot_state(runner) -> dict:
    agents = runner.agents
    if not agents:
        return {
            "num_agents": 0,
            "global_best": runner.global_best_reward,
            "avg": 0.0,
            "best_id": None,
            "best_reward": 0.0,
        }
    best_agent = max(agents, key=lambda a: a.best_reward)
    avg = sum(a.best_reward for a in agents) / len(agents)
    return {
        "num_agents": len(agents),
        "global_best": runner.global_best_reward,
        "avg": avg,
        "best_id": best_agent.node_id,
        "best_reward": best_agent.best_reward,
    }


def extract_events(prev: Optional[dict], curr: dict, tick: int,
                   sequence_length: int) -> List[str]:
    events: List[str] = []

    if prev is None:
        events.append(f"⚡ tick {tick} — primeiros lampejos de cognicao coletiva")
        return events

    if curr["num_agents"] < prev["num_agents"]:
        diff = prev["num_agents"] - curr["num_agents"]
        events.append(
            f"💀 tick {tick} — {diff} agente(s) morreu(ram). restam {curr['num_agents']}."
        )

    if curr["num_agents"] > prev["num_agents"]:
        diff = curr["num_agents"] - prev["num_agents"]
        events.append(
            f"🐣 tick {tick} — {diff} agente(s) nasceu(ram). total: {curr['num_agents']}."
        )

    if curr["global_best"] > prev["global_best"]:
        if curr["global_best"] >= 100.0:
            positions = sequence_length
        else:
            positions = int(curr["global_best"])
        events.append(
            f"🎯 tick {tick} — agente #{curr['best_id']} chegou em "
            f"{positions}/{sequence_length} (novo recorde)."
        )

    if prev["avg"] > 0 and curr["num_agents"] > 0:
        delta = curr["avg"] - prev["avg"]
        if delta > 8:
            events.append(
                f"📈 tick {tick} — onda coletiva: media subiu {delta:.1f} pontos."
            )
        elif delta < -8:
            events.append(
                f"📉 tick {tick} — caos: media caiu {abs(delta):.1f} pontos."
            )

    return events


def build_recipe_strip(recipe_pattern: List[int], best_sequence: Optional[List[int]]) -> go.Figure:
    """Strip mostrando a receita com posicoes ja descobertas iluminadas."""
    n = len(recipe_pattern)
    matched = [False] * n
    if best_sequence and len(best_sequence) == n:
        matched = [best_sequence[i] == recipe_pattern[i] for i in range(n)]

    xs = list(range(n))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=[0] * n, mode="markers+text",
        marker=dict(
            size=46,
            color=["#0d6b3a" if m else "#1a1a28" for m in matched],
            line=dict(
                color=["#39ff88" if m else "rgba(255,255,255,0.2)" for m in matched],
                width=2,
            ),
        ),
        text=[f"<b>{t}</b>" for t in recipe_pattern],
        textfont=dict(color="white", size=16, family="Arial Black"),
        textposition="middle center",
        hoverinfo="skip", showlegend=False,
    ))
    fig.update_layout(
        template="plotly_dark", height=90,
        showlegend=False,
        xaxis=dict(visible=False, range=[-0.5, n - 0.5]),
        yaxis=dict(visible=False, range=[-0.5, 0.5]),
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="#0a0a18", paper_bgcolor="#0a0a18",
    )
    return fig
