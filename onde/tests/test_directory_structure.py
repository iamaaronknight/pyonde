import os
from unittest import TestCase

from onde.onde import DirectoryStructure, AliasedPath, DuplicatePathVariablesError, DuplicateAliasesError, \
    IncorrectlyFormattedPathsFile


class TestDirectoryStructure(TestCase):

    def test_it_expands_multiple_directories(self):
        yaml_data = [
            {'first': ['test/thing_1']},
            {'second': ['/test/thing_2']},
        ]
        directory_structure = DirectoryStructure(yaml_data=yaml_data)
        directory_structure.expand()
        self.assertEqual(len(directory_structure.paths), 2)
        self.assertIn(AliasedPath(alias='first', path='test/thing_1'), directory_structure.paths)
        self.assertIn(AliasedPath(alias='second', path='/test/thing_2'), directory_structure.paths)

    def test_it_expands_nested_directories(self):
        yaml_data = [
            {'top_level': [
                '/test',
                {'next_level': ['foo']},
            ]},
        ]
        directory_structure = DirectoryStructure(yaml_data=yaml_data)
        directory_structure.expand()
        self.assertEqual(len(directory_structure.paths), 2)
        self.assertIn(AliasedPath(alias='top_level', path='/test'), directory_structure.paths)
        self.assertIn(AliasedPath(alias='next_level', path='/test/foo'), directory_structure.paths)

    def test_it_expands_the_users_home_directory(self):
        directory_structure = DirectoryStructure(yaml_data=[{'expanded': ['~/test']}])
        directory_structure.expand()
        self.assertEqual(
            directory_structure.paths[0].path,
            os.path.join(os.path.expanduser('~'), 'test')
        )

    def test_it_deals_with_spaces_in_paths(self):
        directory_structure = DirectoryStructure(yaml_data=[
            {'spacy': ['test a/',
                       {'spacy2': ['Path With Dumb Spaces']}]}
        ])
        directory_structure.expand()
        self.assertEqual(
            directory_structure.paths[1].path,
            'test\ a/Path\ With\ Dumb\ Spaces'
        )


class TestDirectoryStructureErrors(TestCase):

    def test_it_raises_an_error_when_the_same_path_variable_shows_up_more_than_once(self):
        directory_structure = DirectoryStructure(yaml_data=[
            {'top': ['~/test/{duplicate_variable}{duplicate_variable}']}
        ])
        with self.assertRaises(DuplicatePathVariablesError):
            directory_structure.expand()

    def test_it_raises_an_error_when_the_same_alias_is_used_more_than_once(self):
        directory_structure = DirectoryStructure(yaml_data=[
            {'duplicate_alias': ['~/test/foo']},
            {'duplicate_alias': ['~/test/bar']}
        ])
        with self.assertRaises(DuplicateAliasesError):
            directory_structure.expand()

    def test_it_raises_an_error_with_incorrectly_formatted_yaml_data(self):
        with self.assertRaises(IncorrectlyFormattedPathsFile):
            DirectoryStructure(yaml_data={'incorrectly': ['formatted']}).expand()

        with self.assertRaises(IncorrectlyFormattedPathsFile):
            DirectoryStructure(yaml_data=[{'incorrectly': 'formatted'}]).expand()

        with self.assertRaises(IncorrectlyFormattedPathsFile):
            DirectoryStructure(yaml_data=[{'incorrectly': ['formatted', 'data']}]).expand()

        with self.assertRaises(IncorrectlyFormattedPathsFile):
            DirectoryStructure(yaml_data=[{'incorrectly': {'formatted': 'data'}}]).expand()

        with self.assertRaises(IncorrectlyFormattedPathsFile):
            DirectoryStructure(yaml_data=[{'incorrectly': ['formatted', {'data': 'here'}]}]).expand()

        with self.assertRaises(IncorrectlyFormattedPathsFile):
            DirectoryStructure(yaml_data=[['incorrect']]).expand()

        with self.assertRaises(IncorrectlyFormattedPathsFile):
            DirectoryStructure(yaml_data=[{}]).expand()
