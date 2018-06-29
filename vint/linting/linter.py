from typing import Dict, Any, List
import re
import logging
from typing import Dict, List, Any
from pathlib import Path
from vint._bundles import vimlparser
from vint.encodings.decoder import EncodingDetectionError
from vint.ast.parsing import Parser
from vint.ast.node_type import NodeType
from vint.ast.traversing import traverse
from vint.ast.plugin.scope_plugin import ScopePlugin
from vint.linting.lint_target import AbstractLintTarget
from vint.linting.config.config_container import ConfigContainer
from vint.linting.config.config_dict_source import ConfigDictSource
from vint.linting.config.config_abstract_dynamic_source import ConfigAbstractDynamicSource
from vint.linting.config.config_toggle_comment_source import ConfigToggleCommentSource
from vint.linting.config.config_next_line_comment_source import ConfigNextLineCommentSource
from vint.linting.config.config_util import get_config_value
from vint.linting.level import Level
from vint.linting.policy_set import PolicySet


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
        # type: (PolicySet, Dict[str, Any]) -> None
        self._is_debug = get_config_value(config_dict_global, ['cmdargs', 'verbose'], False)

        self._plugins = {
            'scope': ScopePlugin(),
        }

        self._policy_set = policy_set
        self._config_dict_global = config_dict_global
        self._parser = self.build_parser()

        self._listeners_map = {}


    def build_parser(self):
        enable_neovim = get_config_value(self._config_dict_global, ['cmdargs', 'env', 'neovim'], False)

        parser = Parser([self._plugins['scope']], enable_neovim=enable_neovim)
        return parser


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


    def lint(self, lint_target): # type: (AbstractLintTarget) -> List[Dict[str, Any]]
        logging.debug('checking: `{file_path}`'.format(file_path=lint_target.path))

        try:
            root_ast = self._parser.parse(lint_target)
        except vimlparser.VimLParserException as exception:
            parse_error = self._create_parse_error(lint_target.path, str(exception))
            return [parse_error]
        except EncodingDetectionError as exception:
            decoding_error = self._create_decoding_error(lint_target, str(exception))
            return [decoding_error]

        self._traverse(root_ast, lint_target)

        return self._violations


    def _traverse(self, root_ast, lint_target):
        if self._is_debug:
            logging.debug('{cls}: checking `{file_path}`'.format(
                cls=self.__class__.__name__,
                file_path=lint_target.path)
            )
            logging.debug('{cls}: using config as {config_dict}'.format(
                cls=self.__class__.__name__,
                config_dict=self._config_dict_global
            ))

        self._prepare_for_traversal()

        lint_context = {
            'lint_target': lint_target,
            'root_node': root_ast,
            'stack_trace': [],
            'plugins': self._plugins,
            'config': self._config.get_config_dict(),
        }

        traverse(root_ast,
                 on_enter=lambda node: self._handle_enter(node, lint_context),
                 on_leave=lambda node: self._handle_leave(node, lint_context))


    def _prepare_for_traversal(self):
        self._dynamic_configs = [
            ConfigToggleCommentSource(),
            ConfigNextLineCommentSource(is_debug=self._is_debug),
        ]  # type: List[ConfigAbstractDynamicSource]

        config_dict_source = ConfigDictSource(self._config_dict_global.copy())
        self._config = ConfigContainer(config_dict_source, *self._dynamic_configs)

        self._violations = []  # type: List[Dict[str, Any]]
        self._update_listeners_map()


    def _handle_enter(self, node, lint_context):
        self._refresh_policies_if_necessary(node)

        if self._is_debug:
            logging.debug("{cls}: checking {pos}".format(
                cls=self.__class__.__name__,
                pos=node['pos']
            ))

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
        for dynamic_config in self._dynamic_configs:
            dynamic_config.update_by_node(node)

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
