#!/usr/bin/env python
#
# Copyright 2015 Adam Victor Brandizzi
#
# This file is part of Confeitaria.
#
# Confeitaria is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Confeitaria is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Confeitaria.  If not, see <http://www.gnu.org/licenses/>.
from setuptools import setup, find_packages

setup(
    name="confeitaria",
    version="0.1.a3",
    author='Adam Victor Brandizzi',
    author_email='adam@brandizzi.com.br',
    description='Confeitaria is a Python web framework',
    license='LGPLv3',
    url='http://bitbucket.com/brandizzi/confeitaria',

    packages=find_packages(),
    package_data={
        'confeitaria': ['doc/*.rst', 'doc/*.html']
    },

    test_suite='confeitaria_tests',
    test_loader='unittest:TestLoader',
    tests_require=['inelegant']
)
