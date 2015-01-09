import unittest
import enum
from pathlib import Path

from vint.ast.parsing import Parser
from vint.ast.plugin.scope_plugin.scope_linker import ScopeLinker, ScopeVisibility


FIXTURE_BASE_PATH = Path('test', 'fixture', 'ast', 'scope_plugin')


class Fixtures(enum.Enum):
    DECLARING_FUNC = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_func.vim')
    CALLING_FUNC = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_calling_func.vim')
    DECLARING_FUNC_IN_FUNC = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_func_in_func.vim')
    DECLARING_VAR = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_var.vim')
    DECLARING_VAR_IN_FUNC = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_var_in_func.vim')
    FUNC_PARAM = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_func_param.vim')
    LOOP_VAR = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_loop_var.vim')
    DICT_KEY = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_with_dict_key.vim')
    DESTRUCTURING_ASSIGNMENT = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_destructuring_assignment.vim')
    DECLARING_AND_REFERENCING = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_declaring_and_referencing.vim')
    REDIR = Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_redir.vim')


class TestScopeLinker(unittest.TestCase):
    def create_ast(self, file_path):
        parser = Parser()
        ast = parser.parse_file(file_path.value)
        return ast


    def create_variable(self, is_implicit=False, is_builtin=False):
        return {
            'is_implicit': is_implicit,
            'is_builtin': is_builtin,
        }


    def create_scope(self, scope_visibility, variables=None, functions=None,
                     child_scopes=None):
        return {
            'scope_visibility': scope_visibility,
            'functions': functions or {},
            'variables': variables or {},
            'child_scopes': child_scopes or [],
        }


    def assertScopeTreeEqual(self, expected_scope_tree, actual_scope_tree):
        self.maxDiff = 20000

        self.assertEqual(expected_scope_tree, actual_scope_tree)


    def test_built_scope_tree_by_process_with_declaring_func(self):
        ast = self.create_ast(Fixtures.DECLARING_FUNC)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
            },
            functions={
                'g:ExplicitGlobalFunc': [self.create_variable()],
                'g:ImplicitGlobalFunc': [self.create_variable(is_implicit=True)],
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                    },
                    functions={
                        's:ScriptLocalFunc': [self.create_variable()]
                    },
                    child_scopes=[
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            },
                        ),
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            },
                        ),
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            },
                        ),
                    ]
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_scope_tree_by_process_with_declaring_func_in_func(self):
        ast = self.create_ast(Fixtures.DECLARING_FUNC_IN_FUNC)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
            },
            functions={
                'g:FuncContext': [self.create_variable(is_implicit=True)],
                'g:ImplicitGlobalFunc': [self.create_variable(is_implicit=True)],
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                    },
                    child_scopes=[
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            },
                            child_scopes=[
                                self.create_scope(
                                    ScopeVisibility.FUNCTION_LOCAL,
                                    variables={
                                        'l:': [self.create_variable()],
                                        'a:': [self.create_variable()],
                                        'a:0': [self.create_variable()],
                                        'a:000': [self.create_variable()],
                                    }
                                ),
                            ]
                        ),
                    ]
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_scope_tree_by_process_with_declaring_var(self):
        ast = self.create_ast(Fixtures.DECLARING_VAR)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
                'g:explicit_global_var': [self.create_variable()],
                'b:buffer_local_var': [self.create_variable()],
                'w:window_local_var': [self.create_variable()],
                't:tab_local_var': [self.create_variable()],
                'g:implicit_global_var': [self.create_variable(is_implicit=True)],
                '$ENV_VAR': [self.create_variable()],
                '@"': [self.create_variable()],
                '&opt_var': [self.create_variable()],
                'v:count': [self.create_variable(is_builtin=True)],
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                        's:script_local_var': [self.create_variable()],
                    }
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_scope_tree_by_process_with_declaring_var_in_func(self):
        ast = self.create_ast(Fixtures.DECLARING_VAR_IN_FUNC)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
            },
            functions={
                'g:FuncContext': [self.create_variable(is_implicit=True)],
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                    },
                    child_scopes=[
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                                'l:explicit_func_local_var': [self.create_variable()],
                                'l:implicit_func_local_var': [self.create_variable(is_implicit=True)],
                            }
                        )
                    ]
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_scope_tree_by_process_with_declaring_with_dict_key(self):
        ast = self.create_ast(Fixtures.DICT_KEY)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
                # Member functions are not analyzable
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                        # Member functions are not analyzable
                    },
                    child_scopes=[
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'l:self': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            }
                        ),
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'l:self': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            }
                        ),
                    ]
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_scope_tree_by_process_with_destructuring_assignment(self):
        ast = self.create_ast(Fixtures.DESTRUCTURING_ASSIGNMENT)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
                'g:for_var1': [self.create_variable()],
                'g:for_var2': [self.create_variable()],
                'g:let_var1': [self.create_variable()],
                'g:let_var2': [self.create_variable()],
                'g:let_var3': [self.create_variable()],
                'g:rest': [self.create_variable()],
                # g:list members are not analyzable
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                    },
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_scope_tree_by_process_with_func_param(self):
        ast = self.create_ast(Fixtures.FUNC_PARAM)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
            },
            functions={
                'g:FunctionWithNoParams': [self.create_variable()],
                'g:FunctionWithOneParam': [self.create_variable()],
                'g:FunctionWithTwoParams': [self.create_variable()],
                'g:FunctionWithVarParams': [self.create_variable()],
                'g:FunctionWithParamsAndVarParams': [self.create_variable()],
                'g:FunctionWithRange': [self.create_variable()],
                'g:FunctionWithDict': [self.create_variable()],
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                    },
                    child_scopes=[
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            }
                        ),
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                                'a:param': [self.create_variable()],
                            }
                        ),
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                                'a:param1': [self.create_variable()],
                                'a:param2': [self.create_variable()],
                            }
                        ),
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:1': [self.create_variable()],
                                'a:2': [self.create_variable()],
                                'a:3': [self.create_variable()],
                                'a:4': [self.create_variable()],
                                'a:5': [self.create_variable()],
                                'a:6': [self.create_variable()],
                                'a:7': [self.create_variable()],
                                'a:8': [self.create_variable()],
                                'a:9': [self.create_variable()],
                                'a:10': [self.create_variable()],
                                'a:11': [self.create_variable()],
                                'a:12': [self.create_variable()],
                                'a:13': [self.create_variable()],
                                'a:14': [self.create_variable()],
                                'a:15': [self.create_variable()],
                                'a:16': [self.create_variable()],
                                'a:17': [self.create_variable()],
                                'a:18': [self.create_variable()],
                                'a:19': [self.create_variable()],
                                'a:20': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            }
                        ),
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:param_var1': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:1': [self.create_variable()],
                                'a:2': [self.create_variable()],
                                'a:3': [self.create_variable()],
                                'a:4': [self.create_variable()],
                                'a:5': [self.create_variable()],
                                'a:6': [self.create_variable()],
                                'a:7': [self.create_variable()],
                                'a:8': [self.create_variable()],
                                'a:9': [self.create_variable()],
                                'a:10': [self.create_variable()],
                                'a:11': [self.create_variable()],
                                'a:12': [self.create_variable()],
                                'a:13': [self.create_variable()],
                                'a:14': [self.create_variable()],
                                'a:15': [self.create_variable()],
                                'a:16': [self.create_variable()],
                                'a:17': [self.create_variable()],
                                'a:18': [self.create_variable()],
                                'a:19': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            }
                        ),
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:param': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                                'a:firstline': [self.create_variable()],
                                'a:lastline': [self.create_variable()],
                            }
                        ),
                        self.create_scope(
                            ScopeVisibility.FUNCTION_LOCAL,
                            variables={
                                'l:': [self.create_variable()],
                                'l:self': [self.create_variable()],
                                'a:': [self.create_variable()],
                                'a:0': [self.create_variable()],
                                'a:000': [self.create_variable()],
                            }
                        ),
                    ]
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_scope_tree_by_process_with_func_call(self):
        ast = self.create_ast(Fixtures.CALLING_FUNC)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            # no declarative variables
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                    },
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_scope_tree_by_process_with_loop_var(self):
        ast = self.create_ast(Fixtures.LOOP_VAR)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
                'g:implicit_global_loop_var': [self.create_variable(is_implicit=True)]
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                    }
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_scope_tree_by_process_with_redir(self):
        ast = self.create_ast(Fixtures.REDIR)
        linker = ScopeLinker()

        linker.process(ast)

        expected_scope_tree = self.create_scope(
            ScopeVisibility.GLOBAL_LIKE,
            variables={
                'g:': [self.create_variable()],
                'b:': [self.create_variable()],
                'w:': [self.create_variable()],
                't:': [self.create_variable()],
                'v:': [self.create_variable()],
                'g:var': [self.create_variable()]
            },
            child_scopes=[
                self.create_scope(
                    ScopeVisibility.SCRIPT_LOCAL,
                    variables={
                        's:': [self.create_variable()],
                    }
                )
            ]
        )

        self.assertScopeTreeEqual(expected_scope_tree, linker.scope_tree)


    def test_built_identifier_links_by_process(self):
        ast = self.create_ast(Fixtures.DECLARING_AND_REFERENCING)

        # Function call reference identifier node
        ref_id_node = ast['body'][1]['left']['left']

        linker = ScopeLinker()
        linker.process(ast)

        scope_tree = linker.scope_tree
        # Expect a script local scope
        expected_scope = scope_tree['child_scopes'][0]

        link_registry = linker.link_registry
        actual_scope = link_registry.get_context_scope_by_identifier(ref_id_node)

        self.assertScopeTreeEqual(expected_scope, actual_scope)


    def test_built_declarative_identifier_links_by_process(self):
        ast = self.create_ast(Fixtures.DECLARING_AND_REFERENCING)

        # Function name identifier node
        dec_id_node = ast['body'][0]['left']

        linker = ScopeLinker()
        linker.process(ast)

        scope_tree = linker.scope_tree
        # Expect a script local scope
        expected_scope = scope_tree['child_scopes'][0]

        link_registry = linker.link_registry
        actual_scope = link_registry.get_context_scope_by_identifier(dec_id_node)

        self.assertScopeTreeEqual(expected_scope, actual_scope)


    def test_built_reference_variable_links_by_process(self):
        ast = self.create_ast(Fixtures.DECLARING_AND_REFERENCING)

        # Function name identifier node
        expected_dec_id = ast['body'][0]['left']

        linker = ScopeLinker()
        linker.process(ast)

        scope_tree = linker.scope_tree
        # Function local scope
        scope = scope_tree['child_scopes'][0]
        variable_func = scope['functions']['s:Function'][0]

        link_registry = linker.link_registry
        actual_dec_id = link_registry.get_declarative_identifier_by_variable(variable_func)

        self.assertScopeTreeEqual(expected_dec_id, actual_dec_id)


if __name__ == '__main__':
    unittest.main()
