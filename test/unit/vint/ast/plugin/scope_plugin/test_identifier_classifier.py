import unittest
from pathlib import Path
from pprint import pprint

from vint.ast.parsing import Parser
from vint.ast.plugin.scope_plugin.redir_assignment_parser import traverse
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    IdentifierClassifier,
)
from vint.ast.plugin.scope_plugin.identifier_attribute import (
    IDENTIFIER_ATTRIBUTE,
    IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG,
    IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG,
    IDENTIFIER_ATTRIBUTE_MEMBER_FLAG,
    IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG,
    IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG,
    IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG,
    IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT,
    IDENTIFIER_ATTRIBUTE_VARIADIC_SYMBOL_FLAG,
    IDENTIFIER_ATTRIBUTE_LAMBDA_ARGUMENT_FLAG,
    IDENTIFIER_ATTRIBUTE_LAMBDA_BODY_CONTEXT,
)
from vint.linting.lint_target import LintTargetFile


FIXTURE_BASE_PATH = Path('test', 'fixture', 'ast', 'scope_plugin')

Fixtures = {
    'DECLARING_FUNC':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_func.vim'),
    'CALLING_FUNC':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_calling_func.vim'),
    'DECLARING_FUNC_IN_FUNC':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_func_in_func.vim'),
    'DECLARING_VAR':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_var.vim'),
    'DECLARING_VAR_IN_FUNC':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_var_in_func.vim'),
    'FUNC_PARAM':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_func_param.vim'),
    'LOOP_VAR':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_loop_var.vim'),
    'DICT_KEY':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_with_dict_key.vim'),
    'DESTRUCTURING_ASSIGNMENT':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_destructuring_assignment.vim'),
    'BUILTIN':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_builtins.vim'),
    'REDIR':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_redir.vim'),
    'ARITHMETIC_ASSIGNMENT':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_arithmetic_assignment.vim'),
    'MAP_FUNC':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_map_func.vim'),
    'ISSUE_274_CURLYNAME':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_issue_274_curlyname.vim'),
    'ISSUE_274_CURLYNAME_COMPLEX':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_issue_274_curlyname_complex.vim'),
    'LAMBDA':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_lambda_param.vim')
}


class TestIdentifierClassifier(unittest.TestCase):
    def create_ast(self, file_path):
        parser = Parser()
        ast = parser.parse(LintTargetFile(file_path))
        return ast


    def create_id_attr(self, is_declarative=False, is_dynamic=False,
                       is_member=False, is_function=False,
                       is_autoload=False, is_declarative_parameter=False,
                       is_on_lambda_string=False, is_variadic=False,
                       is_lambda_argument=False, is_on_lambda_body=False):
        return {
            IDENTIFIER_ATTRIBUTE_DECLARATION_FLAG: is_declarative,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: is_dynamic,
            IDENTIFIER_ATTRIBUTE_MEMBER_FLAG: is_member,
            IDENTIFIER_ATTRIBUTE_FUNCTION_FLAG: is_function,
            IDENTIFIER_ATTRIBUTE_AUTOLOAD_FLAG: is_autoload,
            IDENTIFIER_ATTRIBUTE_FUNCTION_ARGUMENT_FLAG: is_declarative_parameter,
            IDENTIFIER_ATTRIBUTE_LAMBDA_STRING_CONTEXT: is_on_lambda_string,
            IDENTIFIER_ATTRIBUTE_VARIADIC_SYMBOL_FLAG: is_variadic,
            IDENTIFIER_ATTRIBUTE_LAMBDA_ARGUMENT_FLAG: is_lambda_argument,
            IDENTIFIER_ATTRIBUTE_LAMBDA_BODY_CONTEXT: is_on_lambda_body,
        }


    def assertAttributesInIdentifiers(self, ast, expected_id_attr_map):
        footstamps = {id_name: False for id_name in expected_id_attr_map}

        def on_enter_handler(node):
            if IDENTIFIER_ATTRIBUTE not in node:
                return

            id_name = node['value']
            footstamps[id_name] = True

            self.assertEqual(
                expected_id_attr_map[id_name],
                node[IDENTIFIER_ATTRIBUTE],
                "Identifier Attribute of {1}({0}) have unexpected differences".format(NodeType(node['type']), id_name)
            )

        traverse(ast, on_enter=on_enter_handler)

        # Check all identifier like node was tested
        self.assertTrue(all(footstamps.values()),
                        self._create_fail_message_for_assertion_attr(footstamps))


    def _create_fail_message_for_assertion_attr(self, footstamps):
        unvisiteds = filter(lambda item: not item[1], footstamps.items())
        unvisited_id_names = map(lambda footstamp: footstamp[0], unvisiteds)
        return 'Some identifier like node was not visited: ' + ', '.join(unvisited_id_names)


    def test_attach_identifier_attributes_with_declaring_func(self):
        ast = self.create_ast(Fixtures['DECLARING_FUNC'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:ExplicitGlobalFunc': self.create_id_attr(is_declarative=True, is_function=True),
            's:ScriptLocalFunc': self.create_id_attr(is_declarative=True, is_function=True),
            'ImplicitGlobalFunc': self.create_id_attr(is_declarative=True, is_function=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_calling_func(self):
        ast = self.create_ast(Fixtures['CALLING_FUNC'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'FunctionCall':
                self.create_id_attr(is_declarative=False,
                                    is_function=True),
            'autoload#AutoloadFunctionCall':
                self.create_id_attr(is_declarative=False,
                                    is_autoload=True,
                                    is_function=True),
            'dot':
                self.create_id_attr(is_declarative=False),
            'DotFunctionCall':
                self.create_id_attr(is_declarative=False,
                                    is_member=True,
                                    is_function=True),
            'subscript':
                self.create_id_attr(is_declarative=False),
            "'SubscriptFunctionCall'":
                self.create_id_attr(is_declarative=False,
                                    is_member=True,
                                    is_function=True),
            'FunctionCallInExpressionContext':
                self.create_id_attr(is_declarative=False,
                                    is_function=True),
            'FunctionToBeDeleted':
                self.create_id_attr(is_declarative=False,
                                    is_function=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_declaring_func_in_func(self):
        ast = self.create_ast(Fixtures['DECLARING_FUNC_IN_FUNC'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'FuncContext': self.create_id_attr(is_declarative=True,
                                               is_function=True),
            'ImplicitGlobalFunc':
                self.create_id_attr(is_declarative=True,
                                    is_function=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_declaring_var(self):
        ast = self.create_ast(Fixtures['DECLARING_VAR'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:explicit_global_var': self.create_id_attr(is_declarative=True),
            'b:buffer_local_var': self.create_id_attr(is_declarative=True),
            'w:window_local_var': self.create_id_attr(is_declarative=True),
            't:tab_local_var': self.create_id_attr(is_declarative=True),
            's:script_local_var': self.create_id_attr(is_declarative=True),
            'implicit_global_var': self.create_id_attr(is_declarative=True),
            '$ENV_VAR': self.create_id_attr(is_declarative=True),
            '@"': self.create_id_attr(is_declarative=True),
            '&opt_var': self.create_id_attr(is_declarative=True),
            'v:count': self.create_id_attr(is_declarative=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_declaring_var_in_func(self):
        ast = self.create_ast(Fixtures['DECLARING_VAR_IN_FUNC'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'FuncContext': self.create_id_attr(is_declarative=True, is_function=True),
            'l:explicit_func_local_var': self.create_id_attr(is_declarative=True),
            'implicit_func_local_var': self.create_id_attr(is_declarative=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_declaring_with_dict_key(self):
        ast = self.create_ast(Fixtures['DICT_KEY'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:dict': self.create_id_attr(is_declarative=False),
            'Function1': self.create_id_attr(is_declarative=True,
                                             is_member=True,
                                             is_function=True),
            "'Function2'": self.create_id_attr(is_declarative=True,
                                               is_member=True,
                                               is_function=True),
            'key1': self.create_id_attr(is_declarative=True,
                                        is_member=True,
                                        is_function=False),
            "'key2'": self.create_id_attr(is_declarative=True,
                                          is_member=True,
                                          is_function=False),
            "g:key3": self.create_id_attr(is_declarative=False,
                                          is_member=False,
                                          is_function=False),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_destructuring_assignment(self):
        ast = self.create_ast(Fixtures['DESTRUCTURING_ASSIGNMENT'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:for_var1': self.create_id_attr(is_declarative=True),
            'g:for_var2': self.create_id_attr(is_declarative=True),
            'g:let_var1': self.create_id_attr(is_declarative=True),
            'g:let_var2': self.create_id_attr(is_declarative=True),
            'g:let_var3': self.create_id_attr(is_declarative=True),
            'g:rest': self.create_id_attr(is_declarative=True),
            'g:list': self.create_id_attr(is_declarative=False),
            '1': self.create_id_attr(is_declarative=True, is_member=True),
            'g:index_end': self.create_id_attr(is_declarative=False, is_dynamic=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_func_param(self):
        ast = self.create_ast(Fixtures['FUNC_PARAM'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:FunctionWithNoParams': self.create_id_attr(is_declarative=True, is_function=True),
            'g:FunctionWithOneParam': self.create_id_attr(is_declarative=True, is_function=True),
            'param': self.create_id_attr(is_declarative=True, is_declarative_parameter=True),
            'g:FunctionWithTwoParams': self.create_id_attr(is_declarative=True, is_function=True),
            'param1': self.create_id_attr(is_declarative=True, is_declarative_parameter=True),
            'param2': self.create_id_attr(is_declarative=True, is_declarative_parameter=True),
            'g:FunctionWithVarParams': self.create_id_attr(is_declarative=True, is_function=True),
            'g:FunctionWithParamsAndVarParams': self.create_id_attr(is_declarative=True, is_function=True),
            'param_var1': self.create_id_attr(is_declarative=True, is_declarative_parameter=True),
            'g:FunctionWithRange': self.create_id_attr(is_declarative=True, is_function=True),
            '...': self.create_id_attr(is_declarative=True, is_declarative_parameter=True, is_variadic=True),
            'g:FunctionWithDict': self.create_id_attr(is_declarative=True, is_function=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_loop_var(self):
        ast = self.create_ast(Fixtures['LOOP_VAR'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'implicit_global_loop_var': self.create_id_attr(is_declarative=True),
            'g:array': self.create_id_attr(is_declarative=False),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_redir(self):
        ast = self.create_ast(Fixtures['REDIR'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:var': self.create_id_attr(is_declarative=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_arithmetic_assignment(self):
        ast = self.create_ast(Fixtures['ARITHMETIC_ASSIGNMENT'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:variable_defined': self.create_id_attr(),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_map_func(self):
        ast = self.create_ast(Fixtures['MAP_FUNC'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'v:val': self.create_id_attr(is_on_lambda_string=True),
            'g:pattern': self.create_id_attr(is_on_lambda_string=True),
            'map': self.create_id_attr(is_function=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_issue_274_curlyname(self):
        ast = self.create_ast(Fixtures['ISSUE_274_CURLYNAME'])
        id_classifier = IdentifierClassifier()

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        curlyname_node = attached_ast['body'][0]['left']

        # For debugging.
        pprint(curlyname_node)

        self.assertTrue(curlyname_node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG])


    def test_issue_274_curlyname_complex(self):
        ast = self.create_ast(Fixtures['ISSUE_274_CURLYNAME_COMPLEX'])
        id_classifier = IdentifierClassifier()

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        curlyname_node = attached_ast['body'][0]['body'][1]['right']

        # For debugging.
        pprint(curlyname_node)

        self.assertTrue(curlyname_node[IDENTIFIER_ATTRIBUTE][IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG])


    def test_lambda(self):
        ast = self.create_ast(Fixtures['LAMBDA'])
        id_classifier = IdentifierClassifier()

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        expected_id_attr_map = {
            'i': self.create_id_attr(is_declarative=True, is_lambda_argument=True),
            'y': self.create_id_attr(is_on_lambda_body=True),
            'map': self.create_id_attr(is_function=True),
            '...': self.create_id_attr(is_declarative=True, is_lambda_argument=True, is_variadic=True),
        }

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


if __name__ == '__main__':
    unittest.main()
