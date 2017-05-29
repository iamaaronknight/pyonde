import setuptools


def readme():
    with open('README.md') as f:
        return f.read()


setuptools.setup(
    name='onde',
    version='0.1',
    description='A tool for giving meaningful names to file and directory paths',
    long_description=readme(),
    url='https://github.com/phrasemix/onde',
    author='Aaron Knight',
    author_email='iamaaronknight@gmail.com',
    license='MIT',
    packages=['onde'],
    zip_safe=False,
    install_requires=[
        'pyyaml',
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
    ],
)
