#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name = "confeitaria",
    version = "0.1dev",
    author = 'Adam Victor Brandizzi',
    author_email = 'adam@brandizzi.com.br',
    description = 'Confeitaria is a Python web framework testing hypothesis',
    license = 'LGPLv3',
    url = 'http://bitbucket.com/brandizzi/confeitaria',

    packages = find_packages(),
    package_data = {
        '': ['*.rst', '*.html']
    },

    test_suite = 'confeitaria.server.tests',
    test_loader = 'unittest:TestLoader',
    tests_require=['requests'],
)
