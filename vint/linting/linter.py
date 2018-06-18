import re
import logging
from pathlib import Path
from vint._bundles import vimlparser
from vint.encodings.decoder import EncodingDetectionError
from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse
from vint.ast.plugin.scope_plugin import ScopePlugin
from vint.linting.config.config_container import ConfigContainer
from vint.linting.config.config_dict_source import ConfigDictSource
from vint.linting.config.config_comment_source import ConfigCommentSource
from vint.linting.config.config_util import get_config_value
from vint.linting.level import Level


class Linter(object):
    """ A class for Linters.
    This class provides a linting algorithm that know how to lint by Policy
    class, and how to manage enabled policies by using Config classes.

    The class manage what policies are enabled by using the Config class.
    The config should be refreshed when a config comment is found.
    Then the Linter class notify refresh request to the Config class in
    traversing.

    The Linter class lint by event-driven traversing.
    Enabled policies request to call their when the nodes necesary to validate
    are found in traversing. The Linter class collect violations that are
    returned by policies.
    """
    def __init__(self, policy_set, config_dict_global):
        self._plugins = {
            'scope': ScopePlugin(),
        }
        self._policy_set = policy_set

        self._config_comment_source = ConfigCommentSource()
        self._config = self._decorate_config(config_dict_global,
                                             self._config_comment_source)

        self._parser = self.build_parser()

        self._listeners_map = {}


    def build_parser(self):
        config_dict = self._config.get_config_dict()
        enable_neovim = get_config_value(config_dict, ['cmdargs', 'env', 'neovim'], False)

        parser = Parser(self._plugins, enable_neovim=enable_neovim)
        return parser


    def _decorate_config(self, config_dict_global, config_comment_source):
        config_dict_source = ConfigDictSource(config_dict_global)

        config_container = ConfigContainer(config_dict_source,
                                           config_comment_source)

        return config_container


    def _parse_vimlparser_error(self, err_message):
        match = re.match(r'vimlparser: (?P<description>.*): line (?P<line_number>\d+) col (?P<column_number>\d+)$', err_message)
        return match.groupdict()


    def _create_parse_error(self, path, err_message):
        parser_error = self._parse_vimlparser_error(err_message)
        return {
            'name': 'SyntaxError',
            'level': Level.ERROR,
            'description': parser_error['description'],
            'reference': 'vim-jp/vim-vimlparser',
            'position': {
                'line': int(parser_error['line_number']),
                'column': int(parser_error['column_number']),
                'path': Path(path),
            },
        }


    def _create_decoding_error(self, path, err_message):
        return {
            'name': 'DecodingError',
            'level': Level.ERROR,
            'description': err_message,
            'reference': 'no reference',
            'position': {
                'line': 0,
                'column': 0,
                'path': Path(path),
            },
        }


    def _log_file_path_to_lint(self, file_path):
        msg = 'checking: `{file_path}`'.format(file_path=file_path)
        logging.debug(msg)


    def lint_file(self, path):
        self._log_file_path_to_lint(path)

        try:
            root_ast = self._parser.parse_file(path)
        except vimlparser.VimLParserException as exception:
            parse_error = self._create_parse_error(path, str(exception))
            return [parse_error]
        except EncodingDetectionError as exception:
            decoding_error = self._create_decoding_error(path, str(exception))
            return [decoding_error]

        self._traverse(root_ast, path)

        return self._violations


    def lint_text(self, text):
        self._log_file_path_to_lint('stdin')

        try:
            root_ast = self._parser.parse(text)
        except vimlparser.VimLParserException as exception:
            parse_error = self._create_parse_error('stdin', str(exception))
            return [parse_error]
        except EncodingDetectionError as exception:
            decoding_error = self._create_decoding_error('stdin', str(exception))
            return [decoding_error]

        self._traverse(root_ast, 'stdin')

        return self._violations


    def _traverse(self, root_ast, path):
        self._prepare_for_traversal()

        lint_context = {
            'path': path,
            'root_node': root_ast,
            'stack_trace': [],
            'plugins': self._plugins,
            'config': self._config.get_config_dict(),
        }

        traverse(root_ast,
                 on_enter=lambda node: self._handle_enter(node, lint_context),
                 on_leave=lambda node: self._handle_leave(node, lint_context))


    def _prepare_for_traversal(self):
        self._violations = []
        self._update_listeners_map()


    def _handle_enter(self, node, lint_context):
        self._refresh_policies_if_necessary(node)
        self._fire_listeners(node, lint_context)

        lint_context['stack_trace'].append(node)


    def _handle_leave(self, node, lint_context):
        lint_context['stack_trace'].pop()


    def _fire_listeners(self, node, lint_context):
        node_type = NodeType(node['type'])

        if node_type not in self._listeners_map:
            return

        listening_policies = self._listeners_map[node_type]

        for listening_policy in listening_policies:
            violation = listening_policy.get_violation_if_found(node, lint_context)

            if violation is not None:
                self._violations.append(violation)


    def _refresh_policies_if_necessary(self, node):
        config_comment_source = self._config_comment_source

        if not config_comment_source.is_requesting_update(node):
            return

        self._refresh_policies(node)


    def _refresh_policies(self, node):
        config_comment_source = self._config_comment_source
        config_comment_source.update_by_node(node)

        self._update_listeners_map()


    def _update_enabled_policies(self):
        policy_set = self._policy_set
        config = self._config

        config_dict = config.get_config_dict()
        policy_set.update_by_config(config_dict)


    def _update_listeners_map(self):
        self._update_enabled_policies()

        self._listeners_map = {}
        policy_set = self._policy_set

        for policy in policy_set.get_enabled_policies():
            listened_node_types = policy.listen_node_types()

            for listened_node_type in listened_node_types:
                if listened_node_type not in self._listeners_map:
                    self._listeners_map[listened_node_type] = [policy]
                else:
                    self._listeners_map[listened_node_type].append(policy)
