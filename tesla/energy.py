#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Author:       Casey Sparks
# Date:         January 21, 2023
# Description:
'''Class for Tesla energy products, such as Powerwall and solar.'''

from datetime import datetime
from locale import setlocale, LC_ALL
from logging import getLogger
from typing import NoReturn, Optional
import requests
from ._request_wrappers import get                                          # Wrapper for arbitrary GET requests.

log = getLogger(__name__)                                                   # Enable logging

setlocale(LC_ALL, 'en_US.UTF-8')                                            # Set locale.


class Energy():
    '''Powerwall/solar module for the Tesla API.'''
    def __init__(
        self,
        client: type,
        site_id: str
            ) -> NoReturn:
        '''
        Energy class. Used to get data about, and send commands to, products such as the Powerwall or solar panels.
            :param client:  An instance of tesla.Client.
            :param site_id: The UUID of the Tesla energy product site.
        '''
        self.base_url = 'https://owner-api.teslamotors.com/api/1/energy_sites/{site_id}/'
        self.headers = {**client.headers, **{'Authorization': f'Bearer {client.token["access_token"]}'}}

    def calendar_history(
        self,
        kind: str = 'energy',
        end_date: datetime = datetime.now(),
        interval: Optional[str] = '15m',
        period: Optional[str] = 'day'
            ) -> dict:
        '''
        Retrieves either the power generation/storage (watts) for the previous day, or the cumulative energy
        generation/storage (kWh) for a specified recent period.
            :param kind:        'power' for power statistics (W) at 15-minute intervals over a 24h period.
                                'energy' for energy statistics (kWh) for a specified period.
            :param end_date:    Specifies the last day for which statistics are retrieved.
            :param interval:    Specify the interval to query the power device (like '15m').
            :param period:      The time span for energy statistics to cover.
                                One of 'day', 'week', 'month', 'year'.
        '''
        params = {
            'kind': kind,
            'end_date': end_date.strftime('%Y-%m-%dT%T%z' if end_date.utcoffset else '%Y-%m-%dT%T%-00:00'),
            'period': period,
            'interval': interval
        }

        return get(self, 'calendar_history', params)

    def get_backup_time_remaining(self) -> dict:
        '''Retrieves backup time remaining if battery were to go off grid.'''
        return get(self, 'backup_time_remaining')

    def get_live_status(self) -> dict:
        '''Retrieves current system information.'''
        return get(self, 'live_status')

    def get_programs(self) -> dict:
        '''Retrieves energy site program information.'''
        return get(self, 'programs')

    def get_rate_tariffs(self) -> dict:
        '''Retrieves general system configuration information.'''
        response = requests.get(
            'https://owner-api.teslamotors.com/api/1/energy_sites/rate_tariffs',
            headers=self.tesla_object.headers
        )

        return response.json()['response']

    def get_site_info(self) -> dict:
        '''Retrieves general system configuration information.'''
        return get(self, 'site_info')

    def get_site_status(self) -> dict:
        '''Retrieves general system status information.'''
        return get(self, 'site_status')

    def get_tariff_rate(self) -> dict:
        '''Retrieves the user-defined utility rate plan used for time-based control mode.'''
        return get(self, 'tariff_rate')

    def history(
        self,
        kind: str = 'energy',
        period: Optional[str] = 'day'
            ) -> dict:
        '''
        Retrieves either the power generation/storage (watts) for the previous day, or the
        cumulative energy generation/storage (kWh) for a specified recent period.
            :param kind:    'power' for power statistics (W) at 15-minute intervals over a 24h period.
                            'energy' for energy statistics (kWh) for a specified period.
            :param period:  The time span for energy statistics to cover.
                            One of 'day', 'week', 'month', 'year'.
        '''
        return get(self, 'history', {'kind': kind, 'period': period})
