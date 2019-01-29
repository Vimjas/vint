import unittest
from io import BytesIO
from pathlib import Path
import enum


from vint.linting.lint_target import (
    AbstractLintTarget,
    LintTargetFile,
    LintTargetBufferedStream,
    CachedLintTarget,
)


class Fixture(enum.Enum):
    FILE = Path('test', 'fixture', 'lint_target.vim')



class TestLintTarget(unittest.TestCase):
    def test_file(self):
        lint_target = LintTargetFile(Fixture.FILE.value)

        bytes_seq = lint_target.read()
        self.assertIsNotNone(bytes_seq)
        self.assertEqual(Fixture.FILE.value, lint_target.path)


    def test_buffered_stream(self):
        alternate_path = Path('dummy'),
        lint_target = LintTargetBufferedStream(
            alternate_path=alternate_path,
            buffered_io=BytesIO()
        )

        bytes_seq = lint_target.read()
        self.assertIsNotNone(bytes_seq)
        self.assertEqual(alternate_path, lint_target.path)


    def test_cached(self):
        path_stub = Path('stub')
        lint_target = CachedLintTarget(LintTargetStub(path_stub, bytes()))

        bytes_seq = lint_target.read()
        self.assertIsNotNone(bytes_seq)
        self.assertEqual(path_stub, lint_target.path)



class LintTargetStub(AbstractLintTarget):
    def __init__(self, path, bytes_seq):  # type: (Path, bytes) -> None
        super(LintTargetStub, self).__init__(path)
        self.bytes_seq = bytes_seq


    def read(self):  # type: () -> bytes
        return self.bytes_seq


if __name__ == '__main__':
    unittest.main()