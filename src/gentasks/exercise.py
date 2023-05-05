# Python Imports
from typing import List, Set, Generator, Callable, Sequence, Tuple, Type, Any
from types import GeneratorType
from io import StringIO
from random import shuffle
import dataclasses

# Module Imports
from .tasktypes import *
from .constants import TASK_TEXT, NOTES


GeneratorClass = Type[GeneratorDefaultTask]


class Exercise:
    __slots__ = ('_subgenerators', 'complexity')

    def __init__(self, tasks: Sequence[GeneratorClass] = None):
        self._subgenerators: List[GeneratorClass] = []
        self.complexity: int = 0

        if tasks:
            for task in tasks:
                self.append(task)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"<Exercise with {len(self._subgenerators)} tasks>"

    def append(self, generator_class: GeneratorClass) -> None:
        assert isinstance(generator_class, type(GeneratorDefaultTask)), "Can't append to list non-generator class"
        self._subgenerators.append(generator_class)
        self.complexity += generator_class.complexity

    def pop(self, index: int) -> GeneratorClass:
        generator = self._subgenerators.pop(index)
        self.complexity -= generator._complexity
        return generator

    def notes(self) -> Set[str]:
        values: Set[str] = set()

        for subgenerator in self._subgenerators:
            values.update(subgenerator.notes)

        return values

    def description(self) -> str:
        """Returns exercise text:
        1. Intro
        2. Numerated tasks
        3. Notes
        """
        assert isinstance(TASK_TEXT, str)
        string = StringIO()
        string.write('\t' + TASK_TEXT)

        # if self._subgenerators:
        #     string.write('\n')

        # Tasks text
        for index, task in enumerate(self._subgenerators, 1):
            string.write(f"\n{index}. {task.description()}")
    
        # Call examples
        string.write('\n\tПример вызова генератора:')
        all_variants = [*self.all_variants()]
        shuffle(all_variants)
        for variant in all_variants[:3]:
            arguments = (str(i) for i in variant)
            arguments = ', '.join(arguments)
            string.write(f"\nmain({arguments})")

        # Notes
        notes = self.notes()
        if notes:
            string.write("\n\tПримечания:")
            for note in notes:
                string.write('\n' + NOTES[note])

        return string.getvalue()

    def all_variants(self) -> Generator[List[tuple], None, None]:
        """Returns list of lists, containing arguments for generators to check
        :rtype: List[List[tuple]]
        """
        tasks_possibilities: List[List[tuple]] = []
        for gen in self._subgenerators:
            gen: GeneratorClass
            gen: Generator[GeneratorDefaultTask] = gen.check_cases_generator()
            task_possibilities: List[tuple] = []
            for case in gen:
                case: GeneratorDefaultTask
                case: GeneratorDefaultTask.InputDataclass = case.to_dataclass()
                assert dataclasses.is_dataclass(case)
                case: list = case.as_list()
                assert isinstance(case, list)
                case: tuple = tuple(case)
                task_possibilities.append(case)
            tasks_possibilities.append(task_possibilities)

        arguments = [i[0] for i in tasks_possibilities]
        for task_index, task in enumerate(tasks_possibilities):
            task_len = len(task)
            for pos_index, possibility in enumerate(task, 1):
                arguments[task_index] = possibility
                if pos_index == task_len:
                    continue
                yield arguments.copy()
        yield arguments.copy()

    def _check_variant(self, generator: Generator, arguments: List[tuple]):
        for argument, genclass in zip(arguments, self._subgenerators):
            genclass: GeneratorClass
            genclass: GeneratorDefaultTask = genclass(*argument)
            genclass.check_generator(generator)

    def check_generator(self, generator: Callable[[Any], Generator]) -> None:
        """Validates generator, if he's correct corresponding to tasks
        :param generator: URL to function, that returns generator
        :type generator: Callable[Generator]
        :return: None
        :raises TypeError: if passed function did not return generator
        :raises Exception: Raises any exception, corresponding to each task
        """
        to_check = self.all_variants()
        arguments = next(to_check)

        # Validator check
        gen = generator(*arguments)
        if type(gen) != GeneratorType:
            raise TypeError("Функция(/генератор) не вернула валидный генератор")
        self._check_variant(gen, arguments)

        # Normal iteration
        for arguments in to_check:
            gen = generator(*arguments)
            self._check_variant(gen, arguments)

    def names(self) -> List[str]:
        names = []
        for task in self._subgenerators:
            names.append(task.__qualname__)
        return names

    def tasks(self) -> Tuple[GeneratorClass]:
        return tuple(self._subgenerators)

    def generator(self, *args) -> Generator:
        for arguments, genclass in zip(args, self._subgenerators, strict=True):
            assert isinstance(arguments, tuple)
            assert isinstance(genclass, GeneratorTaskMeta)
            yield from genclass(*arguments).generator()
