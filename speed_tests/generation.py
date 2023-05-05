# Python Imports
from typing import Tuple
from time import time

# Modules
from matplotlib import pyplot as plt

# Module imports
from gentasks.task_generator import *


def _complexity_under(gen: AbstractExerciseGenerator, amount: int, complexity: int) -> float:
    start = time()
    for _ in range(amount):
        gen.get_tasks_under_complexity(complexity)
    end = time()-start
    return end


def _complexity_in(gen: AbstractExerciseGenerator, amount: int, _range: Tuple[int, int]) -> float:
    start = time()
    for _ in range(amount):
        gen.get_tasks_in_complexity_range(_range[0], _range[1])
    end = time()-start
    return end


def exercise_generating() -> None:
    start = time()
    gen = PrecheckExerciseGenerator()
    print(f"Loading: {time()-start}s")
    print('Notes: for [1, 10) range used method "get_tasks_under_complexity",'
          ' for others "get_tasks_in_complexity_range"')

    x = [i for i in range(100_000, 5_000_001, 200_000)]
    y = []

    for i in x:
        y.append(_complexity_under(gen, i, 10))
    plt.plot(x, y, label='[1, 10)')

    y = []
    for i in x:
        y.append(_complexity_in(gen, i, (7, 13)))
    plt.plot(x, y, label='[7, 13)')

    y = []
    for i in x:
        y.append(_complexity_in(gen, i, (2, 14)))
    plt.plot(x, y, label='[2, 14)')

    plt.xlabel('Amount of exercises generated')
    plt.ylabel('Amount of time required to generate')
    plt.title('Generating exercises')
    plt.grid(True)
    plt.legend()
    plt.show()
