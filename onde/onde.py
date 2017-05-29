import os.path
import re
import string
from collections import namedtuple

import yaml

PATH_VARIABLE_REGEX = re.compile(r'\{.*?\}')

AliasedPath = namedtuple('AliasedPath', ['alias', 'path'])


class MissingPathVariableError(StandardError):
    def __init__(self, missing_variables):
        self.missing_variables = missing_variables

    def __str__(self):
        return "All path variables need to be specified. Missing variables: {}".format(string.join(self.missing_variables, ', '))


class UnknownAliasError(StandardError):
    def __str__(self):
        return 'No file or directory with the specified alias was found.'


class IncorrectlyFormattedPathsFile(StandardError):
    def __init__(self, hint=''):
        self.hint = hint

    def __str__(self):
        return 'The paths file is incorrectly formatted. {} ' \
               'Please check the Onde documentation ' \
               'for guidance on how to structure the file properly.'.format(self.hint)


class DuplicateAliasesError(StandardError):
    def __init__(self, alias):
        self.alias = alias

    def __str__(self):
        return 'Duplicate alias "{}" defined in paths YAML file'.format(self.alias)


class DuplicatePathVariablesError(StandardError):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'Duplicate path variable names defined for path string "{}"'.format(self.path)


class TooManyArgumentsError(StandardError):
    def __str__(self):
        return 'Too many path variable arguments were passed into the paths() method.'


class DirectoryStructure(object):
    def __init__(self, yaml_data):
        self.yaml_data = yaml_data
        self.aliases = set()
        self.paths = set()

    def expand(self):
        for node in self.yaml_data:
            self._expand_node(node)

    def _expand_node(self, node, parent_path=''):
        try:
            alias_ = node.keys()[0]
        except AttributeError:
            raise IncorrectlyFormattedPathsFile(hint='Each node should be a dictionary with an alias as its key.')
        except IndexError:
            raise IncorrectlyFormattedPathsFile(hint='Nodes cannot be empty.')

        node_info = node[alias_]

        try:
            new_path = self._new_path(parent_path=parent_path, new_path_part=node_info[0])
        except KeyError:
            raise IncorrectlyFormattedPathsFile(hint='Each node needs to contain data about the dirctory that it describes.')

        self._add_to_aliases(alias_, new_path)

        child_nodes = node_info[1:]
        for child_node in child_nodes:
            self._expand_node(child_node, parent_path=new_path)

    def _new_path(self, parent_path, new_path_part):
        try:
            joined = os.path.join(parent_path, new_path_part)
        except AttributeError:
            raise IncorrectlyFormattedPathsFile(hint='Node data should be a list which includes a path (required) and child nodes (optional).')

        expanded = self._expand_home_path(joined)
        escaped = string.replace(expanded, ' ', '\ ')
        return escaped

    def _expand_home_path(self, path):
        if re.search(r'^~', path):
            home_directory = os.path.expanduser('~')
            return os.path.join(home_directory, path.replace('~/', ''))
        return path

    def _add_to_aliases(self, alias, path):
        if alias in self.aliases:
            raise DuplicateAliasesError(alias)

        variables_in_path = PATH_VARIABLE_REGEX.findall(path)
        if len(variables_in_path) != len(set(variables_in_path)):
            raise DuplicatePathVariablesError(path)

        self.paths.add(AliasedPath(alias, path))
        self.aliases.add(alias)


class Onde(object):
    def __init__(self, paths_file_path=None):
        if paths_file_path:
            paths_file_path = paths_file_path
        elif os.getenv('ONDEFILE_PATH'):
            paths_file_path = os.getenv('ONDEFILE_PATH')
        else:
            paths_file_path = 'paths.yml'

        with open(paths_file_path) as data_file:
            self.directory_structure = DirectoryStructure(yaml_data=yaml.load(data_file))
            self.directory_structure.expand()

    def path(self, alias, *args, **kwargs):
        """
        Get the full path for a file with a given alias in the _yaml_data file.
        :param alias: An alias specified in the YAML file set in the root paths.yml file, passed in, or set as the ONDEFILE_PATH environment variable
        :param kwargs: Methods to match any file or directory variables indicated in the YAML with curly braces
        :return: A string representing a path to the aliased file or directory
        """
        base_path = self._get_base_path(alias)
        return self._replace_path_variables(base_path, *args, **kwargs)

    def _get_base_path(self, alias):
        for aliased_path in self.directory_structure.paths:
            if aliased_path.alias == alias:
                return aliased_path.path

        raise UnknownAliasError

    def _replace_path_variables(self, path, *args, **kwargs):
        if kwargs:
            for k, v in kwargs.iteritems():
                path = re.sub(r'\{{{}\}}'.format(k), v, path)

        unreplaced_variables_matches = PATH_VARIABLE_REGEX.findall(path)
        if args:
            for i, arg in enumerate(args):
                try:
                    path = re.sub(unreplaced_variables_matches[i], arg, path)
                except IndexError:
                    raise TooManyArgumentsError()

            unreplaced_variables_matches = PATH_VARIABLE_REGEX.findall(path)

        if unreplaced_variables_matches:
            raise MissingPathVariableError(missing_variables=unreplaced_variables_matches)
        return path

    @property
    def aliases(self):
        return sorted(list(self.directory_structure.aliases))

    @property
    def paths(self):
        return {
            aliased_path.alias: aliased_path.path
            for aliased_path in self.directory_structure.paths
        }
