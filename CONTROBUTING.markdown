Contribute
==========

How to Add New Policy
---------------------

1. Write both valid/invalid Vim scripts

	Write both valid/invalid Vim scripts and put its to the fixture directory as `test/fixture/policy/policyname_valid.vim`.


2. Write a test code

	You can test easily by using `test.asserting.policy.PolicyAssertion`.

	```python
	import unittest
	from test.asserting.policy import PolicyAssertion
	from test.asserting.policy import get_fixture_path

	from lib.linting.level import Levels
	from lib.linting.policy.my_policy import MyPolicy

	PATH_VALID_VIM_SCRIPT = get_fixture_path('my_policy_valid.vim')
	PATH_INVALID_VIM_SCRIPT = get_fixture_path('my_policy_invalid.vim')


	class TestMyPolicy(PolicyAssertion, unittest.TestCase):
		def test_lint_valid_file(self):
			self.assertFoundNoViolations(PATH_VALID_VIM_SCRIPT, MyPolicy)


		def test_lint_invalid_file(self):
			expected_violations = [
				{
					'name': 'MyPolicy',
					'level': Levels['WARNING'],
					'position': {
						'line': 2,
						'column': 6,
						'path': PATH_INVALID_VIM_SCRIPT
					},
				},
				{
					'name': 'MyPolicy',
					'level': Levels['WARNING'],
					'position': {
						'line': 3,
						'column': 6,
						'path': PATH_INVALID_VIM_SCRIPT
					},
				},
			]

			self.assertFoundViolationsEqual(PATH_VALID_VIM_SCRIPT, MyPolicy, expected_violations)

	if __name__ == '__main__':
		unittest.main()
	```


3. Write a policy code

	You should inherit `lib.linting.policy.AbstractPolicy` and implement 2 methods;

	* `is_valid(Node: ast_node, Environment: env): Boolean`

		This method should return whether the given node is valid for the policy as Boolean.
		And you can use an environment that has `root_ast: Node` and `file_path: String` to
		special lint.

	* `listen_node_type(): NodeType[]`

		This method should return listened `NodeType` such as `NodeType.STRING`.
		Use `NodeType.TOPLEVEL` if you need to lint only once.


4. Run the test

	You can test by [tox](https://tox.readthedocs.org/en/latest/) or [py.test](http://pytest.org/latest/) or the default unittest module.

	There are test command examples;

	* `$ pyenv local 2.7.8 3.4.1 pypy-2.4.0`
	* `$ tox`

	If you want to test by py.test or the default unittest module,
	you should add `vint/bin` to `$PATH` to make acceptance tests pass.

	* `$ pip install -r requirements.txt -r test-requirements.txt`
	* `$ PATH="./bin:$PATH" py.test test`
