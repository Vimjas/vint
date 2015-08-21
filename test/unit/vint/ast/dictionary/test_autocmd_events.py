import pytest
from vint.ast.dictionary.autocmd_events import is_autocmd_event


@pytest.mark.parametrize(('event_name', 'expected_result'), [
    ('BufReadPost', True),
    ('FileType', True),
    ('FILETYPE', True),
    ('filetype', True),
    ('*', True),
    ('INVALID', False),
])
def test_is_autocmd_event(event_name, expected_result):
    assert is_autocmd_event(event_name) is expected_result
