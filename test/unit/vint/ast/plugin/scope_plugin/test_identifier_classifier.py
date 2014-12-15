import unittest
from pathlib import Path

from vint.ast.parsing import Parser
from vint.ast.traversing import traverse
from vint.ast.node_type import NodeType
from vint.ast.plugin.scope_plugin.identifier_classifier import (
    IdentifierClassifier,
    IDENTIFIER_ATTRIBUTE,
    IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG,
    IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG,
    IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG
)


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
}


class TestIdentifierClassifier(unittest.TestCase):
    def create_ast(self, file_path):
        parser = Parser()
        ast = parser.parse_file(file_path)
        return ast


    def create_id_attr(self, is_definition=False, is_dynamic=False, is_member_of_subscript=False):
        return {
            IDENTIFIER_ATTRIBUTE_DEFINITION_FLAG: is_definition,
            IDENTIFIER_ATTRIBUTE_DYNAMIC_FLAG: is_dynamic,
            IDENTIFIER_ATTRIBUTE_SUBSCRIPT_MEMBER_FLAG: is_member_of_subscript,
        }


    def assertAttributesInIdentifiers(self, ast, expected_id_attr_map):
        footstamps = {id_name: False for id_name in expected_id_attr_map}

        def on_enter_handler(node):
            if IDENTIFIER_ATTRIBUTE not in node:
                return

            id_name = node['value']
            footstamps[id_name] = True

            # Print id_name for debugging
            print(NodeType(node['type']), id_name)
            self.assertEqual(expected_id_attr_map[id_name],
                             node[IDENTIFIER_ATTRIBUTE])

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
            'g:ExplicitGlobalFunc': self.create_id_attr(is_definition=True),
            'b:BufferLocalFunc': self.create_id_attr(is_definition=True),
            'w:WindowLocalFunc': self.create_id_attr(is_definition=True),
            't:TabLocalFunc': self.create_id_attr(is_definition=True),
            's:ScriptLocalFunc': self.create_id_attr(is_definition=True),
            'ImplicitGlobalFunc': self.create_id_attr(is_definition=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_calling_func(self):
        ast = self.create_ast(Fixtures['CALLING_FUNC'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'FunctionCall':
                self.create_id_attr(is_definition=False),
            'autoload#AutoloadFunctionCall':
                self.create_id_attr(is_definition=False),
            'dot':
                self.create_id_attr(is_definition=False),
            'DotFunctionCall':
                self.create_id_attr(is_definition=False,
                                    is_member_of_subscript=True),
            'subscript':
                self.create_id_attr(is_definition=False),
            "'SubscriptFunctionCall'":
                self.create_id_attr(is_definition=False,
                                    is_member_of_subscript=True),
            'FunctionCallInExpressionContext':
                self.create_id_attr(is_definition=False),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_declaring_func_in_func(self):
        ast = self.create_ast(Fixtures['DECLARING_FUNC_IN_FUNC'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'FuncContext': self.create_id_attr(is_definition=True),
            'l:ExplicitFuncLocalFunc': self.create_id_attr(is_definition=True),
            'ImplicitFuncLocalFunc':
                self.create_id_attr(is_definition=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_declaring_var(self):
        ast = self.create_ast(Fixtures['DECLARING_VAR'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:explicit_global_var': self.create_id_attr(is_definition=True),
            'b:buffer_local_var': self.create_id_attr(is_definition=True),
            'w:window_local_var': self.create_id_attr(is_definition=True),
            't:tab_local_var': self.create_id_attr(is_definition=True),
            's:script_local_var': self.create_id_attr(is_definition=True),
            'implicit_global_var': self.create_id_attr(is_definition=True),
            '$ENV_VAR': self.create_id_attr(is_definition=True),
            '@"': self.create_id_attr(is_definition=True),
            '&opt_var': self.create_id_attr(is_definition=True),
            'v:count': self.create_id_attr(is_definition=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_declaring_var_in_func(self):
        ast = self.create_ast(Fixtures['DECLARING_VAR_IN_FUNC'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'FuncContext': self.create_id_attr(is_definition=True),
            'l:explicit_func_local_var': self.create_id_attr(is_definition=True),
            'implicit_func_local_var': self.create_id_attr(is_definition=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_declaring_with_dict_key(self):
        ast = self.create_ast(Fixtures['DICT_KEY'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:dict': self.create_id_attr(is_definition=False),
            'Function1': self.create_id_attr(is_definition=True, is_member_of_subscript=True),
            "'Function2'": self.create_id_attr(is_definition=True, is_member_of_subscript=True),
            'key1': self.create_id_attr(is_definition=True, is_member_of_subscript=True),
            "'key2'": self.create_id_attr(is_definition=True, is_member_of_subscript=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_destructuring_assignment(self):
        ast = self.create_ast(Fixtures['DESTRUCTURING_ASSIGNMENT'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:for_var1': self.create_id_attr(is_definition=True),
            'g:for_var2': self.create_id_attr(is_definition=True),
            'g:let_var1': self.create_id_attr(is_definition=True),
            'g:let_var2': self.create_id_attr(is_definition=True),
            'g:list': self.create_id_attr(is_definition=False),
            '1': self.create_id_attr(is_definition=True, is_member_of_subscript=True),
            'g:index_end': self.create_id_attr(is_definition=False, is_member_of_subscript=True, is_dynamic=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_func_param(self):
        ast = self.create_ast(Fixtures['FUNC_PARAM'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'g:FunctionWithNoParams': self.create_id_attr(is_definition=True),
            'g:FunctionWithOneParam': self.create_id_attr(is_definition=True),
            'param': self.create_id_attr(is_definition=True),
            'g:FunctionWithTwoParams': self.create_id_attr(is_definition=True),
            'param1': self.create_id_attr(is_definition=True),
            'param2': self.create_id_attr(is_definition=True),
            'g:FunctionWithVarParams': self.create_id_attr(is_definition=True),
            'g:FunctionWithParamsAndVarParams': self.create_id_attr(is_definition=True),
            'param_var1': self.create_id_attr(is_definition=True),
            'g:FunctionWithRange': self.create_id_attr(is_definition=True),
            '...': self.create_id_attr(is_definition=True),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)


    def test_attach_identifier_attributes_with_loop_var(self):
        ast = self.create_ast(Fixtures['LOOP_VAR'])
        id_classifier = IdentifierClassifier()

        expected_id_attr_map = {
            'implicit_global_loop_var': self.create_id_attr(is_definition=True),
            'g:array': self.create_id_attr(is_definition=False),
        }

        attached_ast = id_classifier.attach_identifier_attributes(ast)

        self.assertAttributesInIdentifiers(attached_ast, expected_id_attr_map)



if __name__ == '__main__':
    unittest.main()
