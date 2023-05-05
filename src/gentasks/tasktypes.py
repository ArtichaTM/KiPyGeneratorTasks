# Python Imports
import random
from string import ascii_letters
from types import GeneratorType
from typing import Generator, Iterable, Generic, TypeVar, Optional, Dict, Set, List, Type
import dataclasses

# Module Imports
from .exceptions import GeneratorUnexpectedShutdown
from .constants import GENERATORS_DESCRIPTION, MAX_LOOP_TESTS

__all__ = (
    'TASKS',
    'GeneratorTaskMeta',
    'GeneratorDefaultTask'
)

T = TypeVar('T')

"""Contains Tasks classes, except GeneratorDefaultTask"""
TASKS: List[Type['GeneratorDefaultTask']] = []


class AbstractInputDataclass:
    def as_list(self) -> List:
        fields = self.__dataclass_fields__.keys()
        values = []
        for field in fields:
            values.append(getattr(self, field))
        return values


class GeneratorTaskMeta(type):
    __slots__ = ()
    all_tasks: List[Type['GeneratorDefaultTask']] = TASKS
    _avoided = False
    _complexity_set: Set[int] = set()

    def __new__(mcs: Type['GeneratorDefaultTask'], name, bases, dct):
        cl: Type['GeneratorDefaultTask'] = super().__new__(mcs, name, bases, dct)

        # This if cause ONLY to avoid GeneratorDefaultTask class
        if mcs._avoided:
            TASKS.append(cl)
            if cl.complexity in mcs._complexity_set:
                raise ValueError("Repeated _complexity in " + str(cl))
            mcs._complexity_set.add(cl.complexity)
        else:
            mcs._avoided = True

        return cl

    def __int__(self: Type['GeneratorDefaultTask']) -> int:
        assert hasattr(self, '_complexity'), "All tasks should include _complexity"
        return self.complexity

    def __repr__(self) -> str:
        return f"<TT {self.__qualname__}>"


class GeneratorDefaultTask(metaclass=GeneratorTaskMeta):
    """Generic class for all Generator Tasks"""
    __slots__ = ()

    """Complexity variable represents severity to complete this task
    Higher _complexity means:
    1. Less chance to appear in tasks
    2. Chance to not appear in tasks at all, if _complexity limit in manager
        is higher than _complexity in current task
    """
    complexity: int

    """Names of notes, that will be displayed after steps definition
    All possible notes can be seen in constants file
    """
    notes: Set[str] = {}

    def __init__(self, *args, **kwargs):
        self.variables_check(*args, **kwargs)

    def __str__(self) -> str:
        return self.description()

    def __int__(self) -> int:
        return self.complexity

    def __repr__(self) -> str:
        return f"{type(self).__qualname__} with {self.to_dataclass()}"

    @dataclasses.dataclass(slots=True)
    class InputDataclass(AbstractInputDataclass):
        """Tuple, that contains names and types, that required to built task"""
        def __iter__(self):
            return (getattr(self, field.name) for field in dataclasses.fields(self))

    def to_dataclass(self) -> InputDataclass:
        raise NotImplementedError('All generator task classes should implement .to_tuple() method')

    @classmethod
    def from_dataclass(cls, tuple: InputDataclass) -> 'GeneratorDefaultTask':
        return cls(*tuple)

    @classmethod
    def check_cases_generator(cls) -> Generator['GeneratorDefaultTask', None, None]:
        """ Generates tasks with values to check all possibilities
        :return: Generator-class generator
        :rtype: GeneratorDefaultTask
        """
        raise NotImplementedError()

    def variables_check(self, *args, **kwargs):
        """Checks object variables for correct type, conditions, e.t.c."""
        raise NotImplementedError('All generator task classes should implement .variables_check() function')

    def generator(self) -> Generator:
        """Creates valid generator corresponding to object variables
        :return: Generator, that works based on object variables and returns(/accepts) valid values
        :rtype: Generator
        """
        raise NotImplementedError('All generator task classes should implement .new() function')

    def check_generator(self, generator: Generator) -> int:
        """Checks generator for correct work.
        NOTE: generator should be started to make this method work properly
        :param generator: Initialized generator
        :type generator: Running generator
        :return: Amount of calls made to generator
        :rtype: int
        """
        raise NotImplementedError()

    @classmethod
    def needed_arguments(cls) -> Dict[str, type]:
        return cls.InputDataclass.__annotations__

    @classmethod
    def description(cls) -> str:
        """ Returns text as item in list
        :return: String with text for students
        :rtype: str
        """
        return GENERATORS_DESCRIPTION[cls.__qualname__]


class Range(GeneratorDefaultTask):
    """Generator, which return numbers within range (start -> end), without end number in ascending order"""
    __slots__ = ('start', 'end')
    complexity = 1

    @dataclasses.dataclass(slots=True)
    class InputDataclass(AbstractInputDataclass):
        start: int
        end: int

    def __init__(self, start: int, end: int, /):
        super().__init__(start, end)
        self.start = start
        self.end = end

    def to_dataclass(self) -> InputDataclass:
        return self.InputDataclass(self.start, self.end)

    @classmethod
    def check_cases_generator(cls) -> Generator['Range', None, None]:
        yield cls(-1, 0)
        yield cls(0, 1)
        yield cls(-100, 100)

    def variables_check(self, start: int, end: int):
        if not isinstance(start, int):
            raise TypeError('Start index should be integer')
        elif not isinstance(end, int):
            raise TypeError('End index should be integer')
        elif start >= end:
            raise ValueError('For positive range start should be lower than end')

    def generator(self) -> Generator[int, None, None]:
        """Returns generator, which returns values from start to end"""
        yield from range(self.start, self.end)

    def check_generator(self, generator: Generator[int, None, None]) -> int:
        if not isinstance(generator, GeneratorType):
            raise TypeError("Полученный объект не является генератором")

        calls = 0
        valid_generator = self.generator()
        valid = _empty = object()

        for valid, current in zip(valid_generator, generator):
            calls += 1
            if not type(current) == type(valid):
                raise TypeError(f"Ожидался тип {type(valid).__qualname__}, получен {type(current).__qualname__}")
            elif current != valid:
                raise ValueError(f"Ожидалось {valid}, получено {current}")
        if valid is _empty:
            raise GeneratorUnexpectedShutdown("Генератор закончил работу при старте")
        return calls


class NegativeRange(Range):
    """Generator, which return numbers within range (start -> end), without end number in descending order """
    complexity = 2

    def variables_check(self, start: int, end: int):
        if not isinstance(start, int):
            raise TypeError('Start index should be integer')
        elif not isinstance(end, int):
            raise TypeError('End index should be integer')
        elif start <= end:
            raise ValueError('For negative range start should be greater than end')

    def generator(self) -> Generator[int, None, None]:
        """Returns generator, which returns values from start to end in reverse order"""
        yield from range(self.start, self.end, -1)

    @classmethod
    def check_cases_generator(cls) -> Generator['NegativeRange', None, None]:
        yield cls(1, 0)
        yield cls(0, -1)
        yield cls(100, -100)


class AwaitKeyword(GeneratorDefaultTask):
    """Generator, which runs forever until got keyword through .send()
    .check() method validates random strings for random amount of calls.
    When generator gets desired keyword, he must yield it and break a loop

    >>> gen = AwaitKeyword('phrase').generator()
    >>> next(gen)  # Starting
    >>> gen.send('wall')  # Incorrect phrase
    >>> value = gen.send('phrase')  # yield keyword and breaks loop
    >>> assert value == 'phrase'
    """
    __slots__ = ('keyword',)
    complexity = 4
    notes = {'.send()'}
    # Quite simple, but u must check for keyword each run and break

    @dataclasses.dataclass(slots=True)
    class InputDataclass(AbstractInputDataclass):
        keyword: str

    def __init__(self, keyword: str):
        super().__init__(keyword)
        self.keyword = keyword

    def _random_keywords(self) -> Generator[str, None, None]:
        while True:
            string = ''.join(random.choice(ascii_letters) for _ in range(random.randint(0, 30)))
            if string == self.keyword:
                continue
            yield string

    def to_dataclass(self) -> InputDataclass:
        return self.InputDataclass(self.keyword)

    def variables_check(self, keyword: str) -> None:
        if not isinstance(keyword, str):
            raise TypeError('Keyword must be string')

    def generator(self) -> Generator[Optional[str], str, None]:
        while True:
            string = yield
            if string == self.keyword:
                break
        yield string

    @classmethod
    def check_cases_generator(cls) -> Generator['AwaitKeyword', None, None]:
        yield cls('keyword')
        yield cls('')
        yield cls('Валу')
        yield cls('123')

    def check_generator(self, generator: Generator[None, str, None]) -> int:
        if not isinstance(generator, GeneratorType):
            raise TypeError("Полученный объект не является генератором")

        # Check, if generator just started
        if not generator.gi_running:
            next(generator)

        calls = 0
        loops = _empty = object()
        for loops, random_keyword in enumerate(self._random_keywords()):
            calls += 1
            try:
                generator.send(random_keyword)
            except StopIteration:
                raise GeneratorUnexpectedShutdown("Генератор остановил свою работу до ключевого слова")

            if loops > 13:
                break

        if loops is _empty:
            raise GeneratorUnexpectedShutdown("Генератор закончил работу при старте")

        # Check after keyword
        try:
            value = generator.send(self.keyword)
            calls += 1
        except StopIteration:
            raise GeneratorUnexpectedShutdown(
                "После получения ключа генератор завершил свою работу, хотя ожидалось str"
            )

        if value != self.keyword:
            raise GeneratorUnexpectedShutdown("Генератору передан ключ. Полученное значение не совпадает с ключом")

        return calls


class Iterator(GeneratorDefaultTask, Generic[T]):
    """Generator, which runs over elements of given sequence"""
    __slots__ = ('iterable', )
    complexity = 3
    # Simple:
    # yield from (i for i in iterable)
    # But not easiest so far

    @dataclasses.dataclass(slots=True)
    class InputDataclass(AbstractInputDataclass):
        iterable: Iterable[T]

    def __init__(self, iterable: Iterable[T]):
        super().__init__(iterable)
        self.iterable = iterable

    def to_dataclass(self) -> InputDataclass:
        return self.InputDataclass(self.iterable)

    def variables_check(self, iterable: Iterable[T]) -> None:
        try:
            iter(iterable)
        except TypeError:
            raise TypeError('iterable argument are not iterable')

    def generator(self) -> Generator[T, None, None]:
        for element in self.iterable:
            yield element

    @classmethod
    def check_cases_generator(cls) -> Generator['Iterator', None, None]:
        yield cls(())
        yield cls((1, 2))
        yield cls([])
        yield cls([1, 2])
        yield cls(set())

    def check_generator(self, generator: Generator[T, None, None]) -> int:
        if not isinstance(generator, GeneratorType):
            raise TypeError("Полученный объект не является генератором")

        calls = 0
        valid_generator = self.generator()
        valid = _empty = object()

        for valid, current in zip(valid_generator, generator):
            calls += 1
            if not type(current) == type(valid):
                raise TypeError(f"Ожидался тип {type(valid).__qualname__} ({valid}),"
                                f" получен {type(current).__qualname__} ({current})")
            elif current != valid:
                raise ValueError(f"Ожидалось {valid}, получено {current}")
        if valid is _empty and sum(1 for _ in self.iterable):
            raise GeneratorUnexpectedShutdown("Генератор закончил работу при старте")
        return calls


class Fibonacci(GeneratorDefaultTask):
    """Yield numbers, corresponding to fibonacci numbers. [0, 1, 1, 2, 3, ...],
    unless exception StopIteration is received

    Example:
    >>> gen = Fibonacci().generator()
    >>> next(gen)
    0
    >>> next(gen)
    1
    >>> next(gen)
    1
    >>> next(gen)
    2
    >>> gen.throw(StopIteration, StopIteration())
    Traceback (most recent call last):
    ...
    StopIteration

    Generator successfully finished
    """
    __slots__ = ()
    complexity = 7
    notes = {'.throw()'}
    # Fibonacci algorithm + generator.throw() method + try-except clauses

    @dataclasses.dataclass(slots=True)
    class InputDataclass(AbstractInputDataclass):
        pass

    def to_dataclass(self) -> InputDataclass:
        return self.InputDataclass()

    def variables_check(self) -> None:
        pass

    def generator(self) -> Generator[int, None, None]:
        first: int = -1
        second: int = -1
        try:
            first = 0
            yield first
            second = 1
            yield second
            while True:
                first, second = second, first+second
                yield second
        except StopIteration:
            if second <= 1 and first != 1:
                yield 1
            yield second+first

    @classmethod
    def check_cases_generator(cls) -> Generator['Fibonacci', None, None]:
        yield cls()

    @staticmethod
    def _check_call(valid_gen: Generator, current_gen: Generator) -> None:
        """Checks fibonacci generators equality and raises different exceptions
        It is assumed that the generators are in the same state
        :param valid_gen: Correct fibonacci generator
        :type valid_gen: Generator
        :param current_gen: Fibonacci generator that under tests
        :type current_gen: Generator
        :raise TypeError: Returned type different from correct
        :raise ValueError: Returned value different from correct
        :raise GeneratorUnexpectedShutdown: Generator unexpectedly raised StopIteration
        """
        answer_valid = next(valid_gen)
        try:
            answer_current = next(current_gen)
        except StopIteration:
            raise GeneratorUnexpectedShutdown("Генератор закончил работу до исключения StopIteration")
        if not type(answer_current) == type(answer_valid):
            raise TypeError(f"Ожидался тип {type(answer_valid).__qualname__},"
                            f" получен {type(answer_current).__qualname__}")
        elif answer_current != answer_valid:
            raise ValueError(f"Ожидалось {answer_valid}, получено {answer_current}")

    def check_generator(self, generator: Generator[T, None, None]) -> int:
        if not isinstance(generator, GeneratorType):
            raise TypeError("Полученный объект не является генератором")

        valid_generator = self.generator()
        answer_valid = _empty = object()

        calls: int = 0
        for calls in range(0, random.randint(400, 400+MAX_LOOP_TESTS)):
            self._check_call(valid_generator, generator)

        generator.throw(StopIteration, StopIteration())
        return calls
