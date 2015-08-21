import pytest
from vint.ast.dictionary.autocmd_events import AutocmdEvents
from vint.ast.plugin.autocmd_parser import parse_autocmd


def create_echo_cmd_node():
    return ':echo'


def create_autocmd_node(autocmd_str):
    return {'str': autocmd_str}


@pytest.mark.parametrize(('autocmd_str', 'expected_result'), [
    (create_autocmd_node('autocmd'), {
        'group': None,
        'event': [],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd!'), {
        'group': None,
        'event': [],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd FileType'), {
        'group': None,
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd BufNew,BufRead'), {
        'group': None,
        'event': [AutocmdEvents.BUF_NEW, AutocmdEvents.BUF_READ],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd! FileType'), {
        'group': None,
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd FileType *'), {
        'group': None,
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': '*',
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd! FileType *'), {
        'group': None,
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': '*',
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd FileType * nested :echo'), {
        'group': None,
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': '*',
        'nested': True,
        'cmd': create_echo_cmd_node(),
    }),
    (create_autocmd_node('autocmd! FileType * nested :echo'), {
        'group': None,
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': '*',
        'nested': True,
        'cmd': create_echo_cmd_node(),
    }),
    (create_autocmd_node('autocmd Group'), {
        'group': 'Group',
        'event': [],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd! Group'), {
        'group': 'Group',
        'event': [],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd Group *'), {
        'group': 'Group',
        'event': [AutocmdEvents.ANY],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd! Group *'), {
        'group': 'Group',
        'event': [AutocmdEvents.ANY],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd Group FileType'), {
        'group': 'Group',
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd! Group FileType'), {
        'group': 'Group',
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': None,
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd Group FileType *'), {
        'group': 'Group',
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': '*',
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd! Group FileType *'), {
        'group': 'Group',
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': '*',
        'nested': False,
        'cmd': None,
    }),
    (create_autocmd_node('autocmd Group FileType * nested :echo'), {
        'group': 'Group',
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': '*',
        'nested': True,
        'cmd': create_echo_cmd_node(),
    }),
    (create_autocmd_node('autocmd! Group FileType * nested :echo'), {
        'group': 'Group',
        'event': [AutocmdEvents.FILE_TYPE],
        'pat': '*',
        'nested': True,
        'cmd': create_echo_cmd_node(),
    }),
])
def test_parse_autocmd(autocmd_str, expected_result):
    assert parse_autocmd(autocmd_str) == expected_result
