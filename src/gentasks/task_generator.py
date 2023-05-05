# Python Imports
from itertools import combinations
from random import shuffle
from typing import List, Tuple, Generator, Type

# Module Imports
from .exercise import Exercise
from .tasktypes import TASKS, GeneratorDefaultTask
from .composition_classes import Singleton


__all__ = (
    'AbstractExerciseGenerator',
    'PrecheckExerciseGenerator'
)


class AbstractExerciseGenerator(Singleton):
    __slots__ = ()

    @staticmethod
    def _create_exercise(tasks: Tuple[Type[GeneratorDefaultTask]]) -> Exercise:
        return Exercise(tasks=tasks)

    @staticmethod
    def _create_exercise_shuffle(tasks: Tuple[Type[GeneratorDefaultTask]]) -> Exercise:
        tasks = list(tasks)
        shuffle(tasks)
        return Exercise(tasks=tasks)

    def get_tasks_under_complexity(self, _complexity: int,
                                   shuffle_tasks: bool = True) -> Generator[Exercise, None, None]:
        """Returns all _combinations of tasks under given _complexity"""
        raise NotImplementedError()

    def get_tasks_in_complexity_range(self, _start: int, _end: int, /,
                                      shuffle_tasks: bool = True) -> Generator[Exercise, None, None]:
        """Returns all _combinations of tasks in given range of _complexity (_end not included)
        Note: if _start or _end out of bounds, instead of rising exception, method sets invalid value to closest
        """
        raise NotImplementedError()

    def get_tasks_amount(self, _amount: int, shuffle_tasks: bool = True) -> Generator[Exercise, None, None]:
        """Returns all combinations with defined amount of tasks"""
        raise NotImplementedError()


class PrecheckExerciseGenerator(AbstractExerciseGenerator):
    """On creating new instace, calculating all possible _combinations.
    + Fast response to method calls
    - With big amount of task types memory usage is immense
    """
    __slots__ = ('_complexity', '_combinations',)

    def new(self) -> None:
        """Creates all possible combinations"""

        self._combinations: List[Tuple[Type['GeneratorDefaultTask']]] = []
        """List of all possible _combinations"""

        self._complexity: List[int] = []
        """Summary _complexity of classes contained on same index in self._combinations"""

        # Creating all possible _combinations
        tasks: List[Type[GeneratorDefaultTask]] = TASKS.copy()

        for combinations_amount in range(1, len(tasks)):
            for combination in combinations(tasks, combinations_amount):
                self._combinations.append(combination)
                self._complexity.append(sum(cl.complexity for cl in combination))

        # Sorting by _complexity
        self._combinations, self._complexity = zip(*sorted(zip(self._combinations,
                                                               self._complexity), key=lambda x: x[1]))
        self._combinations: Tuple[Tuple[Type[GeneratorDefaultTask]]]
        self._complexity: Tuple[int]

    def get_tasks_under_complexity(self, _complexity: int,
                                   shuffle_tasks: bool = True) -> Generator[Exercise, None, None]:
        assert isinstance(_complexity, int), f"Complexity should be integer, got {type(_complexity)}"

        if shuffle_tasks:
            create_exercise = self._create_exercise_shuffle
        else:
            create_exercise = self._create_exercise

        for combination, complexity in zip(self._combinations, self._complexity):
            if complexity > _complexity:
                break
            yield create_exercise(combination)

    def get_tasks_in_complexity_range(self, _start: int, _end: int, /,
                                      shuffle_tasks: bool = True) -> Generator[Exercise, None, None]:
        assert isinstance(_start, int), f"Complexity should be integer, got {type(_start)}"
        assert isinstance(_end, int), f"Complexity should be integer, got {type(_end)}"

        if shuffle_tasks:
            create_exercise = self._create_exercise_shuffle
        else:
            create_exercise = self._create_exercise

        # Out of bounds check
        if _end > self._complexity[-1]:
            _end = self._complexity[-1]
        if _start < self._complexity[0]:
            _start = self._complexity[0]

        start: int = -1
        while start == -1:
            try:
                start = self._complexity.index(_start)
            except ValueError:
                _start += 1
                if _start == _end:
                    raise ValueError("There's no tasks in that range")
            else:
                break

        for combination, complexity in zip(self._combinations[start:], self._complexity[start:]):
            if complexity >= _end:
                break
            yield create_exercise(combination)

    def get_tasks_amount(self, _amount: int, shuffle_tasks: bool = True) -> Generator[Exercise, None, None]:
        """Returns all combinations with defined amount of tasks"""
        assert isinstance(_amount, int)
        assert isinstance(shuffle_tasks, bool)

        if shuffle_tasks:
            create_exercise = self._create_exercise_shuffle
        else:
            create_exercise = self._create_exercise

        for combination in self._combinations:
            if len(combination) != _amount:
                continue
            yield create_exercise(combination)


# class SimpleExerciseGenerator(AbstractExerciseGenerator):
#     __slots__ = ()
# 
#     def new(self) -> None:
#         pass
# 
#     def get_tasks_under_complexity(self, _complexity: int,
#                                    shuffle_tasks: bool = True) -> Generator[Exercise, None, None]:
#         pass
# 
#     def get_tasks_in_complexity_range(self, _start: int, _end: int, /,
#                                       shuffle_tasks: bool = True) -> Generator[Exercise, None, None]:
#         pass