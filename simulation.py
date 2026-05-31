import networkx as nx
import matplotlib.pyplot as plt
import random

# Импортируем всё, что написали вчера
from graph_setup import create_graph, initialize_states, simulation_step, count_states

def run_simulation(num_nodes=30, k=4, p=0.3,
                   spread_prob=0.3, stifle_prob=0.1,
                   num_steps=30, num_infected=1, seed=42):
    """
    Запускает полную симуляцию на num_steps шагов.
    Возвращает историю: сколько S, I, R было на каждом шаге.
    """
    random.seed(seed)

    # 1. Создаём граф и расставляем начальные статусы
    G = create_graph(num_nodes, k, p)
    G = initialize_states(G, num_infected)

    # 2. Списки для хранения истории
    #    После каждого шага будем добавлять сюда текущие числа
    history_S = []
    history_I = []
    history_R = []

    # 3. Основной цикл симуляции
    for step in range(num_steps):
        counts = count_states(G)

        history_S.append(counts['S'])
        history_I.append(counts['I'])
        history_R.append(counts['R'])

        # Выводим прогресс каждые 5 шагов
        if step % 5 == 0:
            print(f"Шаг {step:3d} | S={counts['S']:3d}  I={counts['I']:3d}  R={counts['R']:3d}")

        # Если распространителей не осталось — симуляция закончена
        if counts['I'] == 0:
            print(f"\nСлух угас на шаге {step}!")
            break

        G, _ = simulation_step(G, spread_prob, stifle_prob)

    return history_S, history_I, history_R


def plot_sir_curve(history_S, history_I, history_R):
    """
    Рисует классический SIR-график:
    ось X — время (шаги), ось Y — количество людей в каждом статусе.
    """
    steps = range(len(history_S))   # [0, 1, 2, ..., N]

    plt.figure(figsize=(10, 5))

    plt.plot(steps, history_S, color='steelblue', linewidth=2, label='S — не знают слух')
    plt.plot(steps, history_I, color='red',       linewidth=2, label='I — распространяют')
    plt.plot(steps, history_R, color='gray',      linewidth=2, label='R — замолчали')

    plt.xlabel("Шаг симуляции")
    plt.ylabel("Количество людей")
    plt.title("Динамика распространения слуха (SIR-модель)")
    plt.legend()
    plt.grid(True, alpha=0.3)    # alpha=0.3 — сетка полупрозрачная
    plt.tight_layout()
    plt.savefig("sir_curve.png")
    plt.show()
    print("График сохранён: sir_curve.png")

def compare_parameters():
    """
    Запускает несколько симуляций с разными параметрами
    и рисует их I-кривые (распространители) на одном графике.
    Так видно: кто распространяется быстрее, кто дальше.
    """

    # Список экспериментов: (название, spread_prob, stifle_prob)
    experiments = [
        ("Медленный слух   (spread=0.1, stifle=0.05)", 0.1, 0.05),
        ("Обычный слух     (spread=0.3, stifle=0.1)",  0.3, 0.10),
        ("Вирусный слух    (spread=0.6, stifle=0.1)",  0.6, 0.10),
        ("Быстро глохнет   (spread=0.5, stifle=0.5)",  0.5, 0.50),
    ]

    colors = ['steelblue', 'orange', 'red', 'purple']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    # axes[0] — график количества I (пик распространения)
    # axes[1] — график количества R (сколько всего узнали)

    for (label, spread, stifle), color in zip(experiments, colors):
        S, I, R = run_simulation(
            num_nodes=30,
            spread_prob=spread,
            stifle_prob=stifle,
            num_steps=60,
            seed=42          # один и тот же seed = честное сравнение
        )
        steps = range(len(I))
        axes[0].plot(steps, I, color=color, linewidth=2, label=label)
        axes[1].plot(steps, R, color=color, linewidth=2, label=label)

    axes[0].set_title("Активные распространители (I) со временем")
    axes[0].set_xlabel("Шаг")
    axes[0].set_ylabel("Количество людей")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    axes[1].set_title("Всего узнали слух (R) со временем")
    axes[1].set_xlabel("Шаг")
    axes[1].set_ylabel("Количество людей")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("sir_comparison.png")
    plt.show()
    print("Сохранено: sir_comparison.png")

if __name__ == "__main__":
    print("=== Базовая симуляция ===")
    history_S, history_I, history_R = run_simulation(
        num_nodes=30, spread_prob=0.3, stifle_prob=0.1, num_steps=50
    )
    print(f"Итог: узнали слух {history_R[-1] + history_I[-1]} из 30 человек")
    plot_sir_curve(history_S, history_I, history_R)

    print("\n=== Сравнение параметров ===")
    compare_parameters()