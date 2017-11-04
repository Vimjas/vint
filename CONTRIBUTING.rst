Contribute
==========

How to Add New Policy
---------------------

1. Write both valid/invalid Vim scripts

   Write both valid/invalid Vim scripts and put its to the fixture
   directory as ``test/fixture/policy/policyname_valid.vim``.

2. Write a test code

   You can test easily by using
   ``test.asserting.policy.PolicyAssertion``.

   .. code:: python

       import unittest
       from test.asserting.policy import PolicyAssertion
       from test.asserting.policy import get_fixture_path
       from lib.linting.level import Levels
       from lib.linting.policy.my_policy import MyPolicy


       class TestMyPolicy(PolicyAssertion, unittest.TestCase):
           def test_lint_valid_file(self):
               fixture_path = get_fixture_path('my_policy_valid.vim')

               self.assertFoundNoViolations(fixture_path, MyPolicy)


           def test_lint_invalid_file(self):
               fixture_path = get_fixture_path('my_policy_invalid.vim')

               expected_violations = [
                   {
                       'name': 'MyPolicy',
                       'level': Levels['WARNING'],
                       'position': {
                           'line': 2,
                           'column': 6,
                           'path': fixture_path
                       },
                   },
               ]

               self.assertFoundViolationsEqual(fixture_path,
                                               MyPolicy,
                                               expected_violations)

       if __name__ == '__main__':
           unittest.main()

3. Check the AST of the Vim scripts

   You can see AST by ``dev_tool/show_ast.py``.

   ::

       $ dev_tool/show_ast.py test/fixture/policy/policyname_valid.vim

       {'body': [{'ea': {'addr_count': 0,
                         'amount': 0,
                         'append': 0,
                         'argcmd': {},
                         'argopt': {},
                         'argpos': {'col': 5, 'i': 4, 'lnum': 1},
                         'bad_char': 0,
                         'cmd': {'flags': 'TRLBAR|EXTRA|CMDWIN|SBOXOK',
                                 'minlen': 2,
                                 'name': 'set',
                                 'parser': 'parse_cmd_common'},
                         'cmdpos': {'col': 1, 'i': 0, 'lnum': 1},
                         'usefilter': 0},
                  'pos': {'col': 1, 'i': 0, 'lnum': 1},
                  'str': u'set expandtab',
                  ...

4. Write a policy code

   You should inherit ``lib.linting.policy.AbstractPolicy`` and
   implement 2 methods;

   -  ``is_valid(Node: ast_node, Environment: env): Boolean``

      This method should return whether the given node is valid for the
      policy as Boolean. And you can use an environment that has
      ``root_ast: Node`` and ``file_path: String`` to special lint.

   -  ``listen_node_type(): NodeType[]``

      This method should return listened ``NodeType`` such as
      ``NodeType.STRING``. Use ``NodeType.TOPLEVEL`` if you need to lint
      only once.

5. Run the test

   You can test by `tox <https://tox.readthedocs.org/en/latest/>`__ or
   `py.test <http://pytest.org/latest/>`__ or the default unittest
   module.

   There are test command examples;

   ::

       $ pyenv local 2.7.8 3.4.1
       $ tox

   If you want to test by py.test, you should add ``vint/bin`` to
   ``$PATH`` to make acceptance tests pass.

   ::

       $ pip install -r requirements.txt -r test-requirements.txt`
       $ PATH="./bin:$PATH" py.test test`
