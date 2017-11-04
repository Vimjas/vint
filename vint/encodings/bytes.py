from typing import Optional
from pathlib import Path




try:
    # unicode exists only Python 2.
    unicode

    class Py2And3CompatibleBytes(object):  # python2
        def __init__(self, string):
            # type: (str) -> None
            self.string = string


        def __getitem__(self, sliced):
            return self.string[sliced]


        def __len__(self):
            return len(self.string)


        def decode(self, encoding):
            # type: () -> str
            return self.string.decode(encoding=encoding)


        def index(self, sub, start=None, end=None):
            # type: (Py2And3CompatibleBytes, Optional[int], Optional[int]) -> int
            return self.string.index(sub.string, start, end)


        def strip(self):
            # type: () -> Py2And3CompatibleBytes
            return Py2And3CompatibleBytes(self.string.strip())


        def bytearray(self):
            # type: () -> bytearray
            return bytearray(self.string)


        @classmethod
        def from_str_literal(cls, string):
            # type: (str) -> Py2And3CompatibleBytes
            return Py2And3CompatibleBytes(string)


        @classmethod
        def read(cls, file_path):
            # type: (Path) -> Py2And3CompatibleBytes
            with file_path.open(mode='rb') as f:
                return Py2And3CompatibleBytes(f.read())


except NameError:
    class Py2And3CompatibleBytes(object):  # python3
        def __init__(self, bytes):
            # type: (bytes) -> None
            self.bytes = bytes


        def __getitem__(self, sliced):
            return self.bytes[sliced]


        def __len__(self):
            return len(self.bytes)


        def decode(self, encoding):
            # type: () -> str
            return self.bytes.decode(encoding=encoding)


        def index(self, sub, start=None, end=None):
            # type: (Py2And3CompatibleBytes, Optional[int], Optional[int]) -> int
            return self.bytes.index(sub.bytes, start, end)


        def strip(self):
            # type: () -> Py2And3CompatibleBytes
            return Py2And3CompatibleBytes(self.bytes.strip())


        def bytearray(self):
            # type: () -> bytearray
            return bytearray(self.bytes)


        @classmethod
        def from_str_literal(cls, string):
            # type: (str) -> Py2And3CompatibleBytes
            return Py2And3CompatibleBytes(bytes(string, encoding="utf8"))


        @classmethod
        def read(cls, file_path):
            # type: (Path) -> Py2And3CompatibleBytes
            with file_path.open(mode='rb') as f:
                return Py2And3CompatibleBytes(f.read())

