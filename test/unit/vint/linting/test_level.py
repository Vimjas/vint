import unittest
from vint.linting.level import Level, is_level_enabled


class TestLevel(unittest.TestCase):
    def test_is_level_enabled_with_same_level(self):
        self.assertTrue(is_level_enabled(Level.WARNING, Level.WARNING))

    def test_is_level_enabled_with_lower_level(self):
        self.assertFalse(is_level_enabled(Level.WARNING, Level.ERROR))

    def test_is_level_enabled_with_higher_level(self):
        self.assertTrue(is_level_enabled(Level.ERROR, Level.STYLE_PROBLEM))


if __name__ == '__main__':
    unittest.main()
