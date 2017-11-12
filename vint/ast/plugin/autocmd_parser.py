from vint.ast.node_type import NodeType, get_node_type
from vint.ast.dictionary.autocmd_events import AutocmdEvents, is_autocmd_event
from vint.ast.plugin.abstract_ast_plugin import AbstractASTPlugin
from vint.ast.traversing import traverse, register_traverser_extension
from vint.ast.helpers import get_cmd_name_from_excmd_node

AUTOCMD_CONTENT = 'VINT:autocmd_content'

_autocmd_event_map = {event.value.lower(): event for event in AutocmdEvents}


class AutocmdParser(AbstractASTPlugin):
    """ A class for :autocmd parsers.
    Syntax:
      :au[tocmd][!] [group] {event} {pat} [nested] {cmd}
      :au[tocmd][!] [group] {event} {pat}
      :au[tocmd][!] [group] *       {pat}
      :au[tocmd][!] [group] {event}
      :au[tocmd][!] [group]
    """
    def process(self, ast):
        def enter_handler(node):
            if get_node_type(node) is not NodeType.EXCMD or \
                    get_cmd_name_from_excmd_node(node) != 'autocmd':
                return

            node[AUTOCMD_CONTENT] = parse_autocmd(node)

        traverse(ast, on_enter=enter_handler)


def parse_autocmd(autocmd_node):
    autocmd_info = {
        'group': None,
        'event': [],
        'pat': None,
        'nested': False,
        'cmd': None,
        'bang': False
    }

    # type: str
    autocmd_str = autocmd_node.get('str')

    # This tokens may be broken, because the cmd part can have
    # whitespaces.
    # type: [str]
    tokens = autocmd_str.split(None, 2)

    if len(tokens) > 0:
        autocmd_info['bang'] = tokens[0].endswith('!')

    if len(tokens) == 1:
        # Examples:
        #   :au[tocmd][!]
        return autocmd_info

    # Examples:
    #   :au[tocmd][!] [group] {event} {pat} [nested] {cmd}
    #   :au[tocmd][!] [group] {event} {pat}
    #   :au[tocmd][!] [group] *       {pat}
    #   :au[tocmd][!] [group] {event}
    #   :au[tocmd][!] {group}
    #                    ^
    #                 tokens[1]
    has_group = not is_autocmd_event_like(tokens[1])

    if has_group:
        # Examples:
        #   :au[tocmd][!] {group} {event} {pat} [nested] {cmd}
        #   :au[tocmd][!] {group} {event} {pat}
        #   :au[tocmd][!] {group} *       {pat}
        #   :au[tocmd][!] {group} {event}
        #   :au[tocmd][!] {group}
        #                    ^
        #                 tokens[1]
        autocmd_info['group'] = tokens[1]

        if len(tokens) == 2:
            # Examples:
            #   :au[tocmd][!] {group}
            return autocmd_info

        # Examples:
        #   :au[tocmd][!] {group} {event} {pat} [nested] {cmd}
        #   :au[tocmd][!] {group} {event} {pat}
        #   :au[tocmd][!] {group} *       {pat}
        #   :au[tocmd][!] {group} {event}
        #                         <-------- tokens[2] ------->
        rest_str = tokens[2]

        rest_tokens = rest_str.split(None, 1)
        autocmd_info['event'] = _parse_events(rest_tokens[0])

        if len(rest_tokens) == 1:
            # Examples:
            #   :au[tocmd][!] {group} {event}
            return autocmd_info

        rest_str = rest_tokens[1]
    else:
        # Examples:
        #   :au[tocmd][!] {event} {pat} [nested] {cmd}
        #   :au[tocmd][!] {event} {pat}
        #   :au[tocmd][!] *       {pat}
        #   :au[tocmd][!] {event}
        #                    ^
        #                 tokens[1]
        autocmd_info['event'] = _parse_events(tokens[1])

        if len(tokens) == 2:
            # Examples:
            #   :au[tocmd][!] {event}
            return autocmd_info

        # Examples:
        #   :au[tocmd][!] {event} {pat} [nested] {cmd}
        #   :au[tocmd][!] {event} {pat}
        #   :au[tocmd][!] *       {pat}
        #                         <---- tokens[2] --->
        rest_str = tokens[2]

    # Examples:
    #   :au[tocmd][!] {event} {pat} [nested] {cmd}
    #   :au[tocmd][!] {event} {pat}
    #   :au[tocmd][!] *       {pat}
    #                         <---- rest_str ---->
    rest_tokens = rest_str.split(None, 1)
    autocmd_info['pat'] = rest_tokens[0]

    if len(rest_tokens) == 1:
        # Examples:
        #   :au[tocmd][!] {event} {pat}
        #   :au[tocmd][!] *       {pat}
        return autocmd_info

    #   :au[tocmd][!] {event} {pat} [nested] {cmd}
    #   :au[tocmd][!] {event} {pat}
    #   :au[tocmd][!] *       {pat}
    #                           ^
    #                     rest_tokens[1]
    rest_str = rest_tokens[1]
    has_nested_token = rest_str.startswith('nested ')
    if not has_nested_token:
        # Examples:
        #   :au[tocmd][!] {event} {pat} {cmd}
        #                                 ^
        #                              rest_str
        autocmd_info['cmd'] = _parse_cmd(rest_str)
        return autocmd_info

    # Examples:
    #   :au[tocmd][!] {event} {pat} nested {cmd}
    #                               <- rest_str ->
    rest_str = rest_str.split(None, 1)[1]
    autocmd_info['cmd'] = _parse_cmd(rest_str)
    autocmd_info['nested'] = True
    return autocmd_info


def get_autocmd_content(node):
    return node.get(AUTOCMD_CONTENT)


def _parse_cmd(cmd_str):
    # TODO: Implement it
    return cmd_str


def _parse_events(token):
    parts = token.split(',')
    return [_autocmd_event_map.get(event_name.lower()) for event_name in parts]


def is_autocmd_event_like(token):
    return all([is_autocmd_event(part) for part in token.split(',')])
