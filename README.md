# Onde

Onde ('OWN-jee') is a simple Python tool for naming and referencing file and directory paths meaningfully.


## Usage
Install Onde with pip:

`pip install onde`

To use Onde, create a YAML file named `paths.yml` in the root directory of your project that maps important files and directories to convenient aliases that you can use to refer to those files.


**paths.yml**
```yaml
- some_alias:
  - "/some_absolute_path/some_file.txt"
- another_alias:
  - "some_relative_path/another_file.txt"
- A third alias:
  - "~/some_folder/a_file.txt"
```

You then use Onde by instantiating it and calling `paths`:

```python
>>> from onde import Onde

>>> onde = Onde()

>>> onde.path('some_alias')
'/some_absolute_path/some_file.txt'

>>> onde.path('another_alias')
'some_relative_path/another_file.txt'

>>> onde.path('A third alias')
'/Users/myusername/some_folder/a_file.txt'
```


Paths can include variables, which are wrapped in curly braces. When calling `paths()` you can fill in the variables:

**paths.yml**
```yaml
- my_alias: 
  - "/{my_directory}/{my_file}.txt"
```

```python
>>> from onde import Onde

>>> Onde().path('my_alias', 'hey_there', my_file='hows_it_going')
'/hey_there/hows_it_going.txt'
```

Directories can be nested, to make it easy to refer to represent multiple significant locations within a file system:

**paths.yml**
```yaml
 - top_level: 
   - "some/folder"
   - thing1: 
     - "path/to/child_1"
   - thing2: 
     - "path/to/child_2"
     - deeply_embedded_thing: 
       - "deeply/embedded/thing.txt"
```

```python
>>> from onde import Onde

>>> onde = Onde()

>>> onde.path('top_level')
'some/folder'

>>> onde.path('thing1')
'some/folder/path/to/child1'

>>> onde.path('thing2')
'some/folder/path/to/child2'

>>> onde.path('deeply_embedded_thing')
'some/folder/path/to/child2/deeply/embedded/thing.txt'
```


Aliases must be unique within the paths YAML file. Attempting to import a YAML file with duplicate aliases will raise an exception.

Path variables must also be unique for each path.

A well-formed Onde paths file should be in the format:
```yaml
- alias:
  - 'path_segment'
  - child_alias:
    - 'path_segment'
  - child_alias:
    - 'path_segment'
```

Each mapping has a single alias as its key and a list as the value of that key. The first item in the list is a path segment, which will be appended to all of the path segments above it. Every item after that is a child alias.


## Contributing
Pull requests are welcome!

To install: `python setup.py install`
To run tests: `python setup.py test`

## License
Onde is written by Aaron Knight <iamaaronknight@gmail.com>.  It is released
under the MIT license. See the LICENSE.txt file for more details.

