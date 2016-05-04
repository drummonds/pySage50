# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import imp
import subprocess
import platform

from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        # self.test_args = []
        # self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


# Add the current directory to the module search path.
sys.path.append('.')

# # Constants
CODE_DIRECTORY = 'pysage50'
# DOCS_DIRECTORY = 'docs'
TESTS_DIRECTORY = 'tests'
#DATA_DIRECTORY = 'gnucash_books'
PYTEST_FLAGS = ['--doctest-modules']

# define install_requires for specific Python versions
python_version_specific_requires = []


def read(filename):
    """Return the contents of a file.

    :param filename: file path
    :type filename: :class:`str`
    :return: the file's content
    :rtype: :class:`str`
    """
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


# Import metadata. Normally this would just be:
#
# from luca import metadata
#
# However, when we do this, we also import `luca/__init__.py'. If this
# imports names from some other modules and these modules have third-party
# dependencies that need installing (which happens after this file is run), the
# script will crash. What we do instead is to load the metadata module by path
# instead, effectively side-stepping the dependency problem. Please make sure
# metadata has no dependencies, otherwise they will need to be added to
# the setup_requires keyword.
metadata = imp.load_source(
    'metadata', os.path.join(CODE_DIRECTORY, 'metadata.py'))

# as of Python >= 2.7 and >= 3.2, the argparse module is maintained within
# the Python standard library, otherwise we install it as a separate package
# if sys.version_info < (2, 7) or (3, 0) <= sys.version_info < (3, 3):
#     python_version_specific_requires.append('argparse')


# See here for more options:
# <http://pythonhosted.org/setuptools/setuptools.html>

setup_dict = dict(
    name=metadata.package,
    version=metadata.version,
    author=metadata.authors[0],
    author_email=metadata.emails[0],
    maintainer=metadata.authors[0],
    maintainer_email=metadata.emails[0],
    url=metadata.url,
    description=metadata.description,
    long_description=read('README.md'),
    keywords=['Sage', 'python', 'binding', 'interface', ],
    license='MIT',
    platforms='any',
    # Find a list of classifiers here:
    # <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
    classifiers=[
        'Development Status :: 3 - pre Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=(TESTS_DIRECTORY, )),
    install_requires=[
#                         'sqlite3',
#                         'pandas',
                     ] + python_version_specific_requires,
    # Allow tests to be run with `python setup.py test'.
    tests_require=[
        'pytest',
        'py',
    ],
    # console=['scripts/piecash_ledger.py','scripts/piecash_toqif.py'],
    scripts=[],
    cmdclass = {'test': PyTest},
    test_suite="tests",
    zip_safe=False,  # don't use eggs
)


def main():
    setup(**setup_dict)


if __name__ == '__main__':
    main()
