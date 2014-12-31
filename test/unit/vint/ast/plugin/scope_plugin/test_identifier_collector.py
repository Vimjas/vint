import unittest
from pathlib import Path

from vint.ast.parsing import Parser
from vint.ast.plugin.scope_plugin.identifier_classifier import IdentifierClassifier

FIXTURE_BASE_PATH = Path('test', 'fixture', 'ast', 'scope_plugin')

Fixtures = {
    'LOOP_VAR':
        Path(FIXTURE_BASE_PATH, 'fixture_to_scope_plugin_loop_var.vim'),
}


class TestIdentifierCollector(unittest.TestCase):
    def create_ast(self, file_path):
        parser = Parser()
        ast = parser.parse_file(file_path)

        id_classifier = IdentifierClassifier()
        attached_ast = id_classifier.attach_identifier_attributes(ast)

        return attached_ast


    def test_bucket(self):
        ast = self.create_ast(Fixtures['LOOP_VAR'])
        collector = IdentifierClassifier.IdentifierCollector()

        bucket = collector.collect_identifiers(ast)

        declaring_id_values = [id_node['value'] for id_node in
                               bucket['static_declaring_identifiers']]

        referencing_id_values = [id_node['value'] for id_node in
                                 bucket['static_referencing_identifiers']]

        expected_declaring_id_values = ['implicit_global_loop_var']
        expected_referencing_id_values = ['g:array']

        self.assertEqual(expected_declaring_id_values, declaring_id_values)
        self.assertEqual(expected_referencing_id_values, referencing_id_values)



if __name__ == '__main__':
    unittest.main()
