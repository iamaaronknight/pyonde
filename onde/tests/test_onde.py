import os
from unittest import TestCase

import yaml

from onde import Onde
from onde.onde import TooManyArgumentsError
package_onde = Onde()


class TestOndeBase(TestCase):
    def setUp(self):
        super(TestOndeBase, self).setUp()
        self.temp_yaml_path = package_onde.path('temp_yaml')

    def tearDown(self):
        super(TestOndeBase, self).tearDown()
        try:
            os.remove(self.temp_yaml_path)
        except OSError:
            pass

    def _create_yaml(self, data, path=None):
        if not path:
            path = self.temp_yaml_path
        with open(path, 'w') as temp_yaml:
            temp_yaml.write(yaml.dump(data=data))
            temp_yaml.close()


class TestOndeInstantiation(TestOndeBase):
    def test_paths_file_can_be_passed_in_as_an_argument(self):
        self._create_yaml(
            data=[{'alias_1': ['test/foo']}],
            path=self.temp_yaml_path
        )
        onde = Onde(paths_file_path=self.temp_yaml_path)
        self.assertEqual(onde.paths, {'alias_1': 'test/foo'})
        self.assertEqual(onde.aliases, ['alias_1'])

    def test_paths_file_can_be_read_from_paths_dot_yaml_in_root_directory(self):
        # This test uses the paths.yaml file for the Onde package itself.
        onde = Onde()
        self.assertIn('main', onde.aliases)
        self.assertEqual(onde.paths.get('main'), 'onde/onde.py')


class TestOnde(TestOndeBase):

    def setUp(self):
        super(TestOnde, self).setUp()
        self._create_yaml([
            {'alias_1': ['test/foo']},
            {'alias_2': [
                'test/bar',
                {'alias_3': ['{dir_name}/{file_name}.txt']}
            ]},
        ])
        self.onde = Onde(paths_file_path=self.temp_yaml_path)

    def test_aliases_lists_aliases(self):
        self.assertEqual(self.onde.aliases, [
            'alias_1',
            'alias_2',
            'alias_3',
        ])

    def test_paths_lists_paths(self):
        self.assertEqual(self.onde.paths, {
            'alias_1': 'test/foo',
            'alias_2': 'test/bar',
            'alias_3': 'test/bar/{dir_name}/{file_name}.txt',
        })

    def test_path_returns_path(self):
        self.assertEqual(self.onde.path('alias_1'), 'test/foo')

    def test_path_with_kwarg_replaces_path_variable_with_specified_string(self):
        self.assertEqual(
            self.onde.path('alias_3', dir_name='test_dir', file_name='test_file'),
            'test/bar/test_dir/test_file.txt'
        )

    def test_path_with_positional_arg_replaces_path_variable_with_specified_string(self):
        self.assertEqual(
            self.onde.path('alias_3', 'test_dir', 'test_file'),
            'test/bar/test_dir/test_file.txt'
        )

    def test_path_with_too_many_positional_args_raises_an_error(self):
        with self.assertRaises(TooManyArgumentsError):
            self.onde.path('alias_3', 'test_dir', 'test_file', 'something_extra')
