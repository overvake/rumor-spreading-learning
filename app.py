import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random

from graph_setup import create_graph, initialize_states, simulation_step, count_states

st.set_page_config(page_title="Симулятор слухов", layout="wide")
st.title("🗣️ Симулятор распространения слухов")
st.markdown("Модель **SIR** на случайном графе социальной сети")

# --- Боковая панель ---
st.sidebar.header("⚙️ Параметры симуляции")
num_nodes   = st.sidebar.slider("Количество людей в сети", 10, 100, 30, 5)
spread_prob = st.sidebar.slider("Вероятность передать слух (spread)", 0.0, 1.0, 0.3, 0.05)
stifle_prob = st.sidebar.slider("Вероятность замолчать (stifle)", 0.0, 1.0, 0.1, 0.05)
num_steps   = st.sidebar.slider("Количество шагов", 10, 100, 40, 5)
seed        = st.sidebar.number_input("Seed", value=42)

run_button   = st.sidebar.button("▶️ Запустить симуляцию")
reset_button = st.sidebar.button("🔄 Сброс")

st.sidebar.markdown("---")
st.sidebar.markdown("**Цвета на графе:**")
st.sidebar.markdown("🟢 S — не знают слух")
st.sidebar.markdown("🔴 I — распространяют")
st.sidebar.markdown("🔵 R — замолчали")
st.sidebar.markdown("🟡 O — только что узнали")

if reset_button:
    for key in ['history_S', 'history_I', 'history_R', 'all_states', 'all_new', 'pos', 'G']:
        st.session_state.pop(key, None)
    st.rerun()

# --- Запуск симуляции ---
if run_button:
    random.seed(int(seed))

    G = create_graph(num_nodes=num_nodes, k=4, p=0.3)
    G = initialize_states(G, num_infected=1)
    pos = nx.spring_layout(G, seed=int(seed))

    history_S, history_I, history_R = [], [], []
    all_states = []
    all_new    = []

    for step in range(num_steps):
        counts = count_states(G)
        history_S.append(counts['S'])
        history_I.append(counts['I'])
        history_R.append(counts['R'])
        all_states.append({n: G.nodes[n]['state'] for n in G.nodes()})
        all_new.append(set())

        if counts['I'] == 0:
            break

        G, newly = simulation_step(G, spread_prob, stifle_prob)
        all_new[-1] = newly

    st.session_state['history_S']  = history_S
    st.session_state['history_I']  = history_I
    st.session_state['history_R']  = history_R
    st.session_state['all_states'] = all_states
    st.session_state['all_new']    = all_new
    st.session_state['pos']        = pos
    st.session_state['G']          = G

# --- Отображение ---
if 'history_S' in st.session_state:
    history_S  = st.session_state['history_S']
    history_I  = st.session_state['history_I']
    history_R  = st.session_state['history_R']
    all_states = st.session_state['all_states']
    all_new    = st.session_state['all_new']
    pos        = st.session_state['pos']
    G          = st.session_state['G']
    total_steps = len(history_S)

    color_map = {'S': '#44bb44', 'I': '#ee2222', 'R': '#4488ee'}

    # --- SIR-кривая и метрики ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 SIR-кривая")
        fig_sir, ax = plt.subplots(figsize=(6, 4))
        fig_sir.patch.set_facecolor('#111111')
        ax.set_facecolor("#FFFFFF0C")
        steps_range = range(total_steps)
        ax.plot(steps_range, history_S, color='#44bb44', lw=2, label='S — не знают')
        ax.plot(steps_range, history_I, color='#ee2222', lw=2, label='I — распространяют')
        ax.plot(steps_range, history_R, color='#4488ee', lw=2, label='R — замолчали')
        ax.set_xlabel("Шаг", color='white')
        ax.set_ylabel("Людей", color='white')
        ax.set_title("Динамика S / I / R", color='white')
        ax.tick_params(colors='white')
        ax.legend(facecolor='#222222', labelcolor='white')
        ax.grid(True, alpha=0.2, color='white')
        st.pyplot(fig_sir)
        plt.close()

    with col2:
        st.subheader("🔢 Итоги симуляции")
        total_heard = history_R[-1] + history_I[-1]
        st.metric("Всего шагов", total_steps)
        st.metric("Узнали слух", f"{total_heard} из {num_nodes}")
        st.metric("Так и не узнали", history_S[-1])
        peak_I    = max(history_I)
        peak_step = history_I.index(peak_I)
        st.metric("Пик распространения", f"{peak_I} чел. (шаг {peak_step})")

    # --- Граф по шагам ---
    st.subheader("🕸️ Состояние графа по шагам")
    step_to_show   = st.slider("Выбери шаг для просмотра", 0, total_steps - 1, 0)
    states_at_step = all_states[step_to_show]
    newly_at_step  = all_new[step_to_show]

    # Размер узла зависит от числа связей
    degrees    = dict(G.degree())
    max_degree = max(degrees.values()) if degrees else 1
    node_sizes = [80 + 400 * (degrees[n] / max_degree) for n in G.nodes()]
    node_colors = [color_map[states_at_step[n]] for n in G.nodes()]
    nodes_list  = list(G.nodes())

    col_graph, col_empty = st.columns([1, 1])
    with col_graph:
        fig_graph, ax2 = plt.subplots(figsize=(5, 5))
        fig_graph.patch.set_facecolor('#111111')
        ax2.set_facecolor('#111111')

        # Очень тонкие полупрозрачные рёбра
        nx.draw_networkx_edges(
            G, pos, ax=ax2,
            edge_color='white', alpha=0.08, width=0.8
        )

        # Жёлтый ореол для только что заражённых
        halo_nodes = [n for n in nodes_list if n in newly_at_step]
        if halo_nodes:
            halo_sizes = [node_sizes[nodes_list.index(n)] * 3 for n in halo_nodes]
            nx.draw_networkx_nodes(
                G, pos, ax=ax2,
                nodelist=halo_nodes,
                node_color='#ffcc00',
                node_size=halo_sizes,
                alpha=0.35
            )

        # Основные узлы
        nx.draw_networkx_nodes(
            G, pos, ax=ax2,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.95
        )

        # Подписи
        nx.draw_networkx_labels(
            G, pos, ax=ax2,
            font_size=6, font_color='white'
        )

        counts_at = {s: list(states_at_step.values()).count(s) for s in 'SIR'}
        ax2.set_title(
            f"Шаг {step_to_show}  |  "
            f"S={counts_at['S']}  I={counts_at['I']}  R={counts_at['R']}",
            color='white', fontsize=10
        )
        ax2.axis('off')

        patches = [
            mpatches.Patch(color='#44bb44', label='S — не знают'),
            mpatches.Patch(color='#ee2222', label='I — распространяют'),
            mpatches.Patch(color='#4488ee', label='R — замолчали'),
            mpatches.Patch(color='#ffcc00', label='O — только что узнали'),
        ]
        ax2.legend(handles=patches, loc='upper left',
                   fontsize=6, facecolor='#222222', labelcolor='white')

        st.pyplot(fig_graph)
        plt.close()

else:
    st.info("👈 Настрой параметры слева и нажми **▶️ Запустить симуляцию**")