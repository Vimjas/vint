from typing import Optional
from pathlib import Path
from io import BufferedIOBase



class AbstractLintTarget(object):
    def __init__(self, path): # type: (Path) -> None
        self.path = path


    def read(self): # type: () -> bytes
        raise NotImplementedError()


class LintTargetFile(AbstractLintTarget):
    def __init__(self, path):
        # type: (Path) -> None
        super(LintTargetFile, self).__init__(path)


    def read(self): # type: () -> bytes
        with self.path.open('rb') as f:
            return f.read()


class LintTargetBufferedStream(AbstractLintTarget):
    def __init__(self, alternate_path, buffered_io):
        # type: (Path, BufferedIOBase) -> None
        super(LintTargetBufferedStream, self).__init__(alternate_path)
        self._buffered_io = buffered_io


    def read(self): # type: () -> bytes
        return self._buffered_io.read()


class CachedLintTarget(AbstractLintTarget):
    def __init__(self, lint_target):
        # type: (AbstractLintTarget) -> None
        super(CachedLintTarget, self).__init__(lint_target.path)
        self._target = lint_target
        self._cached_bytes = None  # type: Optional[bytes]


    def read(self): # type: () -> bytes
        if self._cached_bytes is not None:
            return self._cached_bytes

        result = self._target.read()
        self._cached_bytes = result
        return result
