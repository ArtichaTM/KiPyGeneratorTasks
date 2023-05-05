# Python imports
import unittest
from types import GeneratorType
from string import ascii_letters
from random import randint, choice
from typing import Optional, Generator, Iterable
from unittest import TestCase

# Module imports
import gentasks.tasktypes as tasktypes
from gentasks.exceptions import *


def randomword(length: int = 10) -> str:
    return ''.join(choice(ascii_letters) for _ in range(length))


class TestRange(TestCase):
    cl = tasktypes.Range

    def test_argument_types(self) -> None:
        arguments = self.cl.needed_arguments()
        self.assertDictEqual(arguments, {
            'start': int,
            'end': int
        })

    def test_new_type(self) -> None:
        generator = self.cl(1, 5).generator()
        self.assertIsInstance(generator, GeneratorType)

    def test_new_simple(self) -> None:
        generator = self.cl(1, 5).generator()
        simple_range = [*range(1, 5)]
        self.assertSequenceEqual(simple_range, [*generator])

    def test_new_simple2(self) -> None:
        generator = self.cl(-5, 5).generator()
        simple_range = [*range(-5, 5)]
        self.assertSequenceEqual(simple_range, [*generator])

    def test_new_negative(self) -> None:
        self.assertRaises(ValueError, lambda: self.cl(5, 1))

    def test_new_equal(self) -> None:
        self.assertRaises(ValueError, lambda: self.cl(1, 1))

    def test_new_float_numbers(self) -> None:
        self.assertRaises(TypeError, lambda: next(self.cl(1.5, 1)))
        self.assertRaises(TypeError, lambda: next(self.cl(1, 1.5)))
        self.assertRaises(TypeError, lambda: next(self.cl(0.1, 1.0)))
        self.assertRaises(TypeError, lambda: next(self.cl(2.0, 2.0)))

    def test_check_simple(self) -> None:
        cl = self.cl(1, 5)

        def new_generator(start: int, end: int):
            for i in range(start, end):
                yield i

        self.assertEqual(cl.check_generator(new_generator(1, 5)), 4)
        self.assertEqual(cl.check_generator((i for i in range(1, 5))), 4)

    def test_check_wrong_range(self) -> None:
        cl = self.cl(1, 5)

        def new_generator(start: int, end: int):
            for i in range(start, end):
                yield i

        self.assertRaises(ValueError, lambda: cl.check_generator(new_generator(0, 5)))
        self.assertRaises(ValueError, lambda: cl.check_generator(new_generator(2, 5)))
        self.assertRaises(ValueError, lambda: cl.check_generator(new_generator(-1, 5)))
        self.assertRaises(ValueError, lambda: cl.check_generator(new_generator(4, 5)))
        self.assertRaises(GeneratorUnexpectedShutdown, lambda: cl.check_generator(new_generator(5, 5)))
        self.assertRaises(GeneratorUnexpectedShutdown, lambda: cl.check_generator(new_generator(6, 5)))
        self.assertRaises(GeneratorUnexpectedShutdown, lambda: cl.check_generator(new_generator(10, 5)))

    def test_check_wrong_type(self) -> None:
        cl = self.cl(1, 5)

        def float_generator(start: int, end: int):
            for i in range(start, end):
                yield float(i)

        self.assertRaises(TypeError, lambda: cl.check_generator(float_generator(1, 5)))
        self.assertRaises(TypeError, lambda: cl.check_generator(123))
        self.assertRaises(TypeError, lambda: cl.check_generator(('hello',)))


class TestNegativeRange(TestCase):
    cl = tasktypes.NegativeRange

    def test_argument_types(self) -> None:
        arguments = self.cl.needed_arguments()
        self.assertDictEqual(arguments, {
            'start': int,
            'end': int
        })

    def test_new_type(self) -> None:
        generator = self.cl(5, 1).generator()
        self.assertIsInstance(generator, GeneratorType)

    def test_new_simple(self) -> None:
        generator = self.cl(5, 1).generator()
        simple_range = [*range(5, 1, -1)]
        self.assertSequenceEqual(simple_range, [*generator])

    def test_new_simple2(self) -> None:
        generator = self.cl(5, -5).generator()
        simple_range = [*range(5, -5, -1)]
        self.assertSequenceEqual(simple_range, [*generator])

    def test_new_negative(self) -> None:
        self.assertRaises(ValueError, lambda: self.cl(1, 5))

    def test_new_equal(self) -> None:
        self.assertRaises(ValueError, lambda: self.cl(1, 1))

    def test_new_float_numbers(self) -> None:
        self.assertRaises(TypeError, lambda: next(self.cl(1.5, 1)))
        self.assertRaises(TypeError, lambda: next(self.cl(1.3, 1.5)))
        self.assertRaises(TypeError, lambda: next(self.cl(0.1, 1.0)))
        self.assertRaises(TypeError, lambda: next(self.cl(3.0, 2.0)))

    def test_new_negative_float_numbers(self) -> None:
        self.assertRaises(TypeError, lambda: next(self.cl(1.5, -1)))
        self.assertRaises(TypeError, lambda: next(self.cl(1, -1.5)))
        self.assertRaises(TypeError, lambda: next(self.cl(0.1, -1.0)))
        self.assertRaises(TypeError, lambda: next(self.cl(2.0, -2.0)))

    def test_check_simple(self) -> None:
        cl = self.cl(5, 1)

        def new_generator(start: int, end: int):
            for i in range(start, end, -1):
                yield i

        self.assertEqual(cl.check_generator(new_generator(5, 1)), 4)
        self.assertEqual(cl.check_generator((i for i in range(5, 1, -1))), 4)

    def test_check_wrong_range(self) -> None:
        cl = self.cl(5, 1)

        def new_generator(start: int, end: int):
            for i in range(start, end, -1):
                yield i

        self.assertRaises(GeneratorUnexpectedShutdown, lambda: cl.check_generator(new_generator(1, 5)))
        self.assertRaises(GeneratorUnexpectedShutdown, lambda: cl.check_generator(new_generator(0, 5)))
        self.assertRaises(GeneratorUnexpectedShutdown, lambda: cl.check_generator(new_generator(2, 5)))
        self.assertRaises(GeneratorUnexpectedShutdown, lambda: cl.check_generator(new_generator(-1, 5)))
        self.assertRaises(GeneratorUnexpectedShutdown, lambda: cl.check_generator(new_generator(4, 5)))
        self.assertRaises(GeneratorUnexpectedShutdown, lambda: cl.check_generator(new_generator(5, 5)))
        self.assertRaises(ValueError, lambda: cl.check_generator(new_generator(6, 5)))
        self.assertRaises(ValueError, lambda: cl.check_generator(new_generator(10, 5)))

    def test_check_wrong_type(self) -> None:
        cl = self.cl(5, 1)

        def float_generator(start: int, end: int):
            for i in range(start, end, -1):
                yield float(i)

        self.assertRaises(TypeError, lambda: cl.check_generator(float_generator(5, 1)))
        self.assertRaises(TypeError, lambda: cl.check_generator(123))
        self.assertRaises(TypeError, lambda: cl.check_generator(('hello',)))


class TestAwaitKeyword(TestCase):
    cl = tasktypes.AwaitKeyword

    def test_argument_types(self) -> None:
        arguments = self.cl.needed_arguments()
        self.assertDictEqual(arguments, {
            'keyword': str,
        })

    def test_new_type(self) -> None:
        generator = self.cl('5').generator()
        self.assertIsInstance(generator, GeneratorType)

    def _test_new_simple(self, none_range: range, string_range: range, keyword: str = 'Answer, but not right') -> None:
        assert isinstance(none_range, range)
        assert isinstance(string_range, range)
        assert len(keyword) > 15, 'Keyword should contain at least 15 characters'

        generator = self.cl(keyword).generator()
        for _ in none_range:
            self.assertIsNone(next(generator))
        for _ in string_range:
            self.assertIsNone(generator.send(randomword(randint(1, 15))))
        self.assertEqual(keyword, generator.send(keyword))

    def test_new_simple(self) -> None:
        for i in range(5, 20):
            self._test_new_simple(range(randint(i, 25)), range(randint(i, 25)))

    def test_new_wrong_type(self) -> None:
        self.assertRaises(TypeError, lambda: self.cl(5))

    def test_check_simple(self) -> None:
        cl = self.cl('value')

        def keyword_gen(keyword: str) -> Generator[Optional[str], str, None]:
            while True:
                string = yield
                if string == keyword:
                    break
            yield string

        self.assertNotEqual(cl.check_generator(keyword_gen('value')), 0)


class TestIterator(TestCase):
    cl = tasktypes.Iterator

    def test_argument_types(self) -> None:
        arguments = self.cl.needed_arguments()
        self.assertDictEqual(arguments, {
            'iterable': Iterable[tasktypes.T],
        })

    def test_new_type(self) -> None:
        generator = self.cl([]).generator()
        self.assertIsInstance(generator, GeneratorType)

    def test_new_simple(self) -> None:
        values = [1, 2, 3]
        generator = self.cl(values).generator()
        self.assertSequenceEqual(values, [*generator])

    def test_new_different_types(self) -> None:
        values = [None, '', self, [1, 5, 6], {'key': 'value'}, ...]
        generator = self.cl(values).generator()
        self.assertSequenceEqual(values, [*generator])

    def test_new_dict(self) -> None:
        values = {'key1': 1, 'key2': 2}
        generator = self.cl(values).generator()
        self.assertSequenceEqual([*values.keys()], [*generator])

    def test_check_simple(self) -> None:
        cl = self.cl([1, 2, 3])

        def generator(values: Iterable):
            yield from (v for v in values)

        self.assertEqual(cl.check_generator(generator([1, 2, 3])), 3)

    def test_check_list_sizes(self) -> None:
        for length in range(0, 10):
            list = [i for i in range(0, length)]
            cl = self.cl(list)
            self.assertEqual(cl.check_generator((value for value in list)), len(list))

    def test_check_different_types(self) -> None:
        cl = self.cl((1, 2))
        self.assertEqual(2, cl.check_generator((i for i in (1, 2))))

    def test_check_custom_class(self) -> None:
        class CustomIterable:
            __slots__ = ('var',)

            def __init__(self):
                self.var = -1

            def __iter__(self):
                return self

            def __next__(self) -> int:
                self.var += 1
                if self.var == 100:
                    raise StopIteration
                return self.var

        cl = self.cl(CustomIterable())
        self.assertEqual(100, cl.check_generator((i for i in CustomIterable())))

    def test_check_generator(self) -> None:
        def gen_example() -> Generator:
            yield 1
            yield 123
            yield [213]
            yield None
            yield ...

        cl = self.cl(gen_example())
        self.assertEqual(5, cl.check_generator(gen_example()))


class TestFibonacci(TestCase):
    cl = tasktypes.Fibonacci

    def test_argument_types(self) -> None:
        arguments = self.cl.needed_arguments()
        self.assertDictEqual(arguments, dict())

    def setUp(self) -> None:
        self.cl = self.cl()

    def test_new_type(self) -> None:
        generator = self.cl.generator()
        self.assertIsInstance(generator, GeneratorType)

    def test_new_20elements(self) -> None:
        fibonacci_constant = [
            0, 1, 1, 2, 3,
            5, 8, 13, 21, 34,
            55, 89, 144, 233, 377,
            610, 987, 1597, 2584, 4181
        ]
        generator = self.cl.generator()
        for number in fibonacci_constant[:-1]:
            self.assertEqual(number, next(generator))
        self.assertEqual(fibonacci_constant[-1], generator.throw(StopIteration, StopIteration()))

    def test_new_send_random(self) -> None:
        generator = self.cl.generator()
        self.assertEqual(generator.send(None), 0)
        self.assertEqual(generator.send(123), 1)
        self.assertEqual(generator.send('values'), 1)
        self.assertIsInstance(generator.throw(StopIteration, StopIteration()), int)

    def test_new_closing(self) -> None:
        gen = self.cl.generator()
        next(gen)
        self.assertIsInstance(gen.throw(StopIteration, StopIteration()), int)

    def test_check_simple(self) -> None:
        def gen() -> Generator[int, None, None]:
            yield 0
            yield 1
            first = 0
            second = 1
            while True:
                first, second = second, first + second
                try:
                    yield second
                except StopIteration:
                    break

        self.assertRaises(StopIteration, lambda: self.cl.check_generator(gen()))

    def test_check_wrong_100(self) -> None:
        def gen() -> Generator[int, None, None]:
            yield 0
            yield 1
            first = 0
            second = 1
            while True:
                first, second = second, first + second
                if second > 100:
                    yield 1
                try:
                    yield second
                except StopIteration:
                    break
        self.assertRaises(ValueError, lambda: self.cl.check_generator(gen()))

    def test_pre_closing(self) -> None:
        def gen() -> Generator[int, None, None]:
            yield 0
            yield 1
        self.assertRaises(GeneratorUnexpectedShutdown, lambda: self.cl.check_generator(gen()))

    def test_after_raising(self) -> None:
        generator = self.cl.generator()
        self.assertEqual(generator.send(None), 0)
        self.assertEqual(generator.send(123), 1)
        self.assertEqual(generator.send('values'), 1)
        self.assertIsInstance(generator.throw(StopIteration, StopIteration()), int)
        self.assertRaises(StopIteration, lambda: next(generator))


if __name__ == '__main__':
    unittest.main()
