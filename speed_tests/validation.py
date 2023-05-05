# Python Imports
from timeit import timeit

# Modules
from matplotlib import pyplot as plt

# Module imports
from gentasks.task_generator import *
from gentasks.exercise import Exercise


def _check_exercise(exercise: Exercise) -> None:
    exercise.check_generator(exercise.generator)


def _generator_test(amount: int) -> None:
    assert isinstance(amount, int)
    assert amount >= 1
    gen = PrecheckExerciseGenerator()

    values1 = []
    values2 = []
    for index, exercise in enumerate(gen.get_tasks_amount(amount, False)):
        names = '+'.join(exercise.names())
        values1.append(names)
        values2.append(timeit(lambda: _check_exercise(exercise), number=100))

    plt.barh(values1, values2)
    plt.xlabel('Amount of time required to check (seconds)')
    plt.title('Validating exercises')
    # plt.grid(True)
    plt.tight_layout()
    plt.grid(axis='x')
    plt.show()


def generator_test() -> None:
    _generator_test(1)
    _generator_test(2)
    _generator_test(3)
