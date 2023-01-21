#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:       Casey Sparks
# Date:         January 21, 2023
# Description:
'''Class for the Tesla account API.'''

from locale import setlocale, LC_ALL
from logging import getLogger
from typing import NoReturn
from ._request_wrappers import get                                          # Wrapper for arbitrary GET requests.

log = getLogger(__name__)                                                   # Enable logging

setlocale(LC_ALL, 'en_US.UTF-8')                                            # Set locale.


class Account():
    '''Account module for the Tesla API.'''
    def __init__(
        self,
        client: type
            ) -> NoReturn:
        '''
        Instantiates the Tesla API client.
            :param client:  An instance of tesla.Client.
        '''
        self.base_url = client.base_url
        self.headers = {**client.headers, **{'Authorization': f'Bearer {client.token["access_token"]}'}}

    @property
    def me(self) -> dict:
        '''Provide data on the current user.'''
        return get(self, 'users/me')

    @property
    def feature_config(self) -> dict:
        '''Get the feature configuration for the current user's mobile app.'''
        return get(self, 'users/feature_config')

    @property
    def notification_preferences(self) -> dict:
        '''Get current notification settings.'''
        return get(self, 'notification_preferences')

    @property
    def products(self) -> list:
        '''Lists all Tesla products owned by the user.'''
        return get(self, 'products')

    @property
    def subscriptions(self) -> dict:
        '''Get active Tesla subscriptions.'''
        return get(self, 'vehicle_subscriptions')

    @property
    def vault_profile(self) -> dict:
        '''Mystery endpoint that returns some base64-encoded garbage.'''
        return get(self, 'users/vault_profile')

    @property
    def vehicles(self) -> list:
        '''Lists all vehicles owned by the user.'''
        return get(self, 'vehicles')
