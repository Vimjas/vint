import unittest
from vint.utils.array import flatten, flat_map


class TestUtilsArray(unittest.TestCase):
    def test_flatten_empty(self):
        result = flatten([])
        self.assertEqual(result, [])

    def test_flatten_not_empty(self):
        result = flatten([[0], [1, 2]])
        self.assertEqual(result, [0, 1, 2])

    def test_flat_map(self):
        result = flat_map(lambda x: [x, x * 2], [0, 1, 2])
        self.assertEqual(result, [0, 0, 1, 2, 2, 4])
