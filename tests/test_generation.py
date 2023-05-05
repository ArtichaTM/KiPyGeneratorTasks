import unittest

from gentasks.task_generator import PrecheckExerciseGenerator
from gentasks.exercise import Exercise


class TestGeneration(unittest.TestCase):
    _class: PrecheckExerciseGenerator = PrecheckExerciseGenerator()

    def test_types(self) -> None:
        for exercise in self._class.get_tasks_in_complexity_range(0, 1000):
            self.assertIsInstance(exercise, Exercise)

    def test_complexity_range(self) -> None:
        for exercise in self._class.get_tasks_in_complexity_range(2, 10):
            self.assertGreaterEqual(exercise.complexity, 2)
            self.assertLess(exercise.complexity, 10)
        for exercise in self._class.get_tasks_in_complexity_range(5, 20):
            self.assertGreaterEqual(exercise.complexity, 5)
            self.assertLess(exercise.complexity, 20)

    def test_amount(self) -> None:
        for i in range(1, 5):
            for exercise in self._class.get_tasks_amount(i):
                self.assertEqual(len(exercise.tasks()), i)

if __name__ == '__main__':
    unittest.main()
