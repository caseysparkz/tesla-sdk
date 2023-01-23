#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:       Casey Sparks
# Date:         January 21, 2023
# Notes:        Rather than updating ../setup.py with each incremental change, make changes below.
#               * __include__ should be updated with each added module.
#               * __requirements__ should be updated with each added dependency.
#               * __version__ should be incremented with each release.

__title__ = 'tesla'
__description__ = 'Python3 library for the Tesla owners API.'
__author__ = 'caseyspar.kz'
__author_email__ = 'contact@caseyspar.kz'
__version__ = '0.1.2'                                                       # Update.
__url__ = 'https://github.com/caseysparkz/tesla-sdk'
__include__ = [                                                             # Update.
    'tesla',
    'tesla.*'
]
__requirements__ = [                                                        # Update.
    'requests>=2.28.1,<3',
    'requests_oauthlib>=1.3.0,<2'
]
