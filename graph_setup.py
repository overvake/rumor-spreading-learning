import networkx as nx
import matplotlib.pyplot as plt
import random

def create_graph(num_nodes=30, k=4, p=0.3):
    G = nx.watts_strogatz_graph(n=num_nodes, k=k, p=p)
    return G

def print_graph_info(G):
    print(f"Узлов (людей): {G.number_of_nodes()}")
    print(f"Рёбер (знакомств): {G.number_of_edges()}")
    print(f"Среднее число друзей: {sum(dict(G.degree()).values()) / G.number_of_nodes():.1f}")

def draw_graph(G):
    plt.figure(figsize=(8, 8))

    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G,
        pos,
        node_color="skyblue",   # цвет узлов
        node_size=300,           # размер узлов
        edge_color="gray",       # цвет рёбер
        with_labels=True,        # показывать номера узлов
        font_size=8
    )

    plt.title("Граф социальной сети (до начала симуляции)")
    plt.tight_layout()
    plt.savefig("graph_initial.png")
    plt.show()
    print("График сохранён в graph_initial.png")

def initialize_states(G, num_infected=1):
    """
    Всем узлам присваиваем статус 'S'.
    Затем случайно выбираем num_infected узлов и делаем их 'I'.
    
    G            - наш граф
    num_infected - сколько человек изначально знают слух
    """
    # все - восприимчивые (S)
    for node in G.nodes():
        G.nodes[node]['state'] = 'S'
        G.nodes[node]['steps_as_I'] = 0

    # выбираем случайных "носителей слуха" и делаем их I
    spreaders = random.sample(list(G.nodes()), num_infected)
    for node in spreaders:
        G.nodes[node]['state'] = 'I'

    print(f"Начальный носитель слуха: узел(ы) {spreaders}")
    return G

def count_states(G):
    """Считаем, сколько человек в каждом состоянии."""
    counts = {'S': 0, 'I': 0, 'R': 0}
    for node in G.nodes():
        state = G.nodes[node]['state']  # читаем атрибут 'state'
        counts[state] += 1
    return counts

# --- Рисуем с цветами по статусу ---

def draw_graph_with_states(G):
    """
    S — голубой (не знают)
    I — красный (распространяют)
    R — серый  (замолчали)
    """
    # Словарь цветов
    color_map = {'S': 'skyblue', 'I': 'red', 'R': 'lightgray'}

    # Формируем список цветов в порядке узлов графа
    node_colors = [color_map[G.nodes[node]['state']] for node in G.nodes()]

    pos = nx.spring_layout(G, seed=42)  # seed=42 — позиции те же, что были

    plt.figure(figsize=(8, 8))
    nx.draw(
        G,
        pos,
        node_color=node_colors,
        node_size=300,
        edge_color="gray",
        with_labels=True,
        font_size=8
    )

    # Считаем текущие количества для заголовка
    counts = count_states(G)
    plt.title(f"Шаг 0  |  S={counts['S']}  I={counts['I']}  R={counts['R']}")
    plt.tight_layout()
    plt.savefig("graph_step0.png")
    plt.show()
    print("Сохранено: graph_step0.png")

def simulation_step(G, spread_prob=0.3, stifle_prob=0.1):
    to_infected  = []
    to_recovered = []
    newly_infected = set()

    for node in G.nodes():
        state = G.nodes[node]['state']
        if state == 'I':
            G.nodes[node]['steps_as_I'] += 1
            for neighbor in G.neighbors(node):
                if G.nodes[neighbor]['state'] == 'S':
                    if random.random() < spread_prob:
                        to_infected.append(neighbor)
            
            if G.nodes[node]['steps_as_I'] > 1:
                if random.random() < stifle_prob:
                    to_recovered.append(node)

    for node in to_infected:
        G.nodes[node]['state'] = 'I'
        G.nodes[node]['steps_as_I'] = 0
        newly_infected.add(node)

    for node in to_recovered:
        G.nodes[node]['state'] = 'R'

    return G, newly_infected

if __name__ == "__main__":
    random.seed(42)

    G = create_graph(num_nodes=30, k=4, p=0.3)
    G = initialize_states(G, num_infected=1)

    print("=== Шаг 0 (начало) ===")
    print(count_states(G))
    draw_graph_with_states(G)
    
    G, _ = simulation_step(G, spread_prob=0.3, stifle_prob=0.1)

    print("\n=== Шаг 1 (после первого шага) ===")
    print(count_states(G))

    # Рисуем состояние после шага
    pos = nx.spring_layout(G, seed=42)
    counts = count_states(G)
    node_colors = [{'S':'skyblue','I':'red','R':'lightgray'}[G.nodes[n]['state']] for n in G.nodes()]

    plt.figure(figsize=(8, 8))
    nx.draw(G, pos, node_color=node_colors, node_size=300,
            edge_color="gray", with_labels=True, font_size=8)
    plt.title(f"Шаг 1  |  S={counts['S']}  I={counts['I']}  R={counts['R']}")
    plt.tight_layout()
    plt.savefig("graph_step1.png")
    plt.show()
    print("Сохранено: graph_step1.png")