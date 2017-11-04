from typing import TypeVar, List, Callable
from functools import reduce
from operator import add

T = TypeVar('T')
S = TypeVar('S')


def flatten(l):
    # type: (List[List[T]]) -> List[T]
    return reduce(add, l, [])


def flat_map(f, l):
    # type: (Callable[[S], List[T]], List[S]) -> List[T]
    return flatten([f(x) for x in l])