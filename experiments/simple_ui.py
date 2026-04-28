"""
Pluribus — UI Simples (modo leigo).

3 modos pictoricos + 1 slider de agentes + 5 plugins narrativos.
Retorna (config, plugins) prontos pra alimentar o SimulationRunner.
"""
from typing import List, Tuple

import streamlit as st

from src.simulation.config import SimulationConfig
from src.plugins import get_plugin
from src.plugins.base import Plugin


SIMPLE_MODES = {
    "hive": {
        "icon": "🐝",
        "title": "Mente Coletiva",
        "tagline": "Todos pensam juntos. Convergencia rapida.",
        "config": dict(
            mode="hive",
            collective_sync=85,
            learning_strength=20,
            energy=600,
            num_ticks=120,
        ),
    },
    "local": {
        "icon": "🕸️",
        "title": "Vizinhanca",
        "tagline": "So conversam com quem ta perto. Emergencia organica.",
        "config": dict(
            mode="local",
            collective_sync=40,
            learning_strength=12,
            energy=900,
            num_ticks=200,
            topology_type="random",
            network_density=25,
        ),
    },
    "chaos": {
        "icon": "🌪️",
        "title": "Caos",
        "tagline": "Pouca conversa, pouca memoria. Veja o caldeirao ferver.",
        "config": dict(
            mode="local",
            collective_sync=10,
            learning_strength=5,
            energy=1500,
            num_ticks=400,
            topology_type="random",
            network_density=15,
        ),
    },
}

NARRATIVE_PLUGINS = [
    {
        "key": "disaster",
        "icon": "☄️",
        "label": "Catastrofes",
        "help": "De vez em quando uma tragedia reseta o progresso.",
        "params": {"probability": 0.02, "reset_factor": 0.3, "balance_damage": 0.2},
    },
    {
        "key": "fatigue",
        "icon": "😴",
        "label": "Cansaco",
        "help": "Agentes cansam e aprendem menos com o tempo.",
        "params": {"fatigue_rate": 0.05, "rest_threshold": 0.8},
    },
    {
        "key": "gossip",
        "icon": "🗣️",
        "label": "Fofoca",
        "help": "Mentem entre si. As vezes a fofoca atrapalha tudo.",
        "params": {"lie_probability": 0.15, "detection_chance": 0.3},
    },
    {
        "key": "genetic",
        "icon": "🧬",
        "label": "Reproducao",
        "help": "Quando alguem se sai bem, deixa filhos com mutacao.",
        "params": {"mutation_rate": 0.1, "inheritance_factor": 0.8},
    },
    {
        "key": "death",
        "icon": "💀",
        "label": "Morte",
        "help": "Quem fica sem energia morre de verdade.",
        "params": {},
    },
]


@st.dialog("Como funciona?")
def _show_howto():
    st.markdown(
        """
**🎯 O desafio**
Descobrir uma sequencia secreta. Tipo `[0, 0, 2, 2, 0, 0, 0, 2]`.

**🎲 As regras**
Cada agente chuta uma sequencia. O mundo responde **so com o total de acertos** — nao diz quais posicoes estao certas.

**🧠 A pegadinha (credit assignment)**
Acertar 7/8 e facil. O ultimo digito doi: pra corrigir a posicao errada, o agente tem que mexer numa que ele **ja acertou**. O score cai antes de subir. Parece retrocesso, e o caminho.

**🧮 A "mente" do agente**
Cada um carrega uma matriz `P[posicao][token]` — a chance de chutar cada simbolo em cada posicao. Reward bom reforca, ruim afrouxa. Nao guarda regra, guarda **viés**.

---

**📡 O canal de comunicacao**
Nao trafegam sequencias nem rewards. Trafega **a propria matriz P** do agente que mais acertou no tick — uma especie de "telepatia" de policy. Os outros misturam essa matriz na deles (peso = `collective_sync`).

> Por isso o coletivo e poderoso mas burro: copia o **palpite do mais sortudo**, sem saber por que ele e bom.

---

**🎮 Os 3 modos**

🐝 **Mente Coletiva (HIVE)**
Todo tick, o melhor do tick irradia a P dele pra **todos**. Convergencia rapida (~3-10 ticks), pouca diversidade.

🕸️ **Vizinhanca (LOCAL)**
Cada agente so olha pros vizinhos do grafo. O melhor da bolha local e que dita. Emergencia mais lenta, mais rica.

🌪️ **Caos**
LOCAL com rede esparsa e pouca memoria. Quase ninguem se entende. Pra ver o caldeirao ferver.

---

**🌶️ Os temperos**
Adicionam stress: catastrofes resetam progresso, cansaco corroi aprendizado, fofoca contamina o canal, morte tira agentes sem energia, reproducao traz novos. Combinam de forma imprevisivel.
        """
    )
    if st.button("Entendi 🚀", type="primary", use_container_width=True):
        st.rerun()


def render() -> Tuple[SimulationConfig, List[Plugin], dict]:
    """
    Renderiza a UI simples e retorna (config, plugins, options).

    options = {"run": bool, "live_arena": bool}
    """
    if not st.session_state.get("seen_howto"):
        st.session_state.seen_howto = True
        _show_howto()

    title_col, help_col = st.columns([4, 1])
    with title_col:
        st.markdown("### 🎮 Escolha o estilo da simulacao")
    with help_col:
        if st.button("❓ Como funciona?", use_container_width=True, key="open_howto"):
            _show_howto()

    if "simple_mode" not in st.session_state:
        st.session_state.simple_mode = "hive"

    cols = st.columns(3)
    for col, (key, mode) in zip(cols, SIMPLE_MODES.items()):
        with col:
            selected = st.session_state.simple_mode == key
            border = "3px solid #7a4dff" if selected else "1px solid #2a2a3a"
            bg = "#15152a" if selected else "#0e0e1a"
            st.markdown(
                f"""
                <div style="
                    border: {border};
                    background: {bg};
                    border-radius: 12px;
                    padding: 18px;
                    text-align: center;
                    min-height: 140px;
                ">
                    <div style="font-size: 44px;">{mode['icon']}</div>
                    <div style="font-size: 18px; color: #fff; font-weight: 600; margin-top: 4px;">
                        {mode['title']}
                    </div>
                    <div style="font-size: 12px; color: #aaa; margin-top: 6px;">
                        {mode['tagline']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                "✓ Escolhido" if selected else "Escolher",
                key=f"pick_{key}",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.simple_mode = key
                st.rerun()

    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 👥 Quantos agentes?")
        num_agents = st.slider(
            "Numero de mentes participando",
            min_value=5, max_value=60, value=20, step=1,
            label_visibility="collapsed",
        )

        st.markdown("### 🧩 Dificuldade")
        difficulty = st.select_slider(
            "Tamanho do enigma",
            options=["Facil", "Normal", "Dificil"],
            value="Normal",
            label_visibility="collapsed",
        )

    with col_right:
        st.markdown("### 🌶️ Tempero (opcional)")
        st.caption("Ative o que quiser — cada um muda a historia.")

        active_plugin_keys: List[str] = []
        for plug in NARRATIVE_PLUGINS:
            on = st.checkbox(
                f"{plug['icon']} {plug['label']}",
                value=False,
                help=plug["help"],
                key=f"simple_plug_{plug['key']}",
            )
            if on:
                active_plugin_keys.append(plug["key"])

    st.markdown("---")

    btn_col, opt_col = st.columns([3, 1])
    with btn_col:
        run = st.button(
            "▶️ Comecar simulacao",
            type="primary",
            use_container_width=True,
            key="simple_run",
        )
    with opt_col:
        live_arena = st.checkbox(
            "🎬 Live Arena",
            value=True,
            help="Mostra arena animada enquanto roda",
        )

    diff_map = {
        "Facil": dict(sequence_length=5, alphabet_size=3),
        "Normal": dict(sequence_length=8, alphabet_size=4),
        "Dificil": dict(sequence_length=12, alphabet_size=5),
    }
    mode_cfg = SIMPLE_MODES[st.session_state.simple_mode]["config"]

    config = SimulationConfig(
        num_agents=num_agents,
        num_recipes=1,
        log_interval=1,
        output_file="gui_results.csv",
        **diff_map[difficulty],
        **mode_cfg,
    )

    plugins: List[Plugin] = []
    for plug_meta in NARRATIVE_PLUGINS:
        if plug_meta["key"] in active_plugin_keys:
            try:
                plugins.append(get_plugin(plug_meta["key"], **plug_meta["params"]))
            except Exception as e:
                st.warning(f"Erro ao carregar {plug_meta['label']}: {e}")

    return config, plugins, {"run": run, "live_arena": live_arena}
