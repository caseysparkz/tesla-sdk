#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:       Casey Sparks
# Date:         October 25, 2022
# Notes:        There is absolutely **no need** to update this file as the SDK continues to develop.
#               Instead, make changes to `tesla/__version__.py`.
# Description:
'''Python SDK for the Tesla API.'''

from setuptools import find_packages, setup
from tesla.__version__ import (                                             # Auto-updating magic from __version__.py.
    __title__,
    __description__,
    __author__,
    __author_email__,
    __version__,
    __url__,
    __requirements__,
    __include__
)

setup(
    name=__title__,
    description=__description__,
    author=__author__,
    author_email=__author_email__,
    version=__version__,
    url=__url__,
    install_requires=__requirements__,
    packages=find_packages(include=__include__)
)
