#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:       Casey Sparks
# Date:         January 21, 2023
# Description:
'''Class for retreiving state from the Tesla vehicle API.'''

from locale import setlocale, LC_ALL
from logging import getLogger
from typing import NoReturn
from .._request_wrappers import get                                         # Generic GET wrappers for the Tesla API.

log = getLogger(__name__)                                                   # Enable logging

setlocale(LC_ALL, 'en_US.UTF-8')                                            # Set locale.


class State():
    '''Vehicle module for the Tesla API.'''
    def __init__(
        self,
        parent_class: type
            ) -> NoReturn:
        '''
        Vehicle state class. Used to get data about a Tesla vehicle.
            :param parent_class:    The parent Vehicle class.
        '''
        self.base_url = parent_class.base_url
        self.headers = parent_class.headers

    def vehicle_data(self) -> dict:
        '''A rollup of all the data request endpoints plus vehicle configuration.'''
        return get(self, 'vehicle_data')

    def latest_vehicle_data(self) -> dict:
        '''Cached data, pushed by the vehicle on sleep, wake and around OTAs.'''
        return get(self, 'latest_vehicle_data')

    def charge_state(self) -> dict:
        '''Get charge information about a Tesla.'''
        return get(self, 'data_request/charge_state')

    def climate_state(self) -> dict:
        '''Get climate information from a Tesla.'''
        return get(self, 'data_request/climate_state')

    def drive_state(self) -> dict:
        '''Get drive state information from a Tesla.'''
        return get(self, 'data_request/drive_state')

    def gui_settings(self) -> dict:
        '''Get GUI settings from a Tesla.'''
        return get(self, 'data_request/gui_settings')

    def vehicle_state(self) -> dict:
        '''Returns the vehicle's physical state, such as which doors are open.'''
        return get(self, 'data_request/vehicle_state')

    def vehicle_config(self) -> dict:
        '''Returns the vehicle's configuration information including model, color, badging and wheels.'''
        return get(self, 'data_request/vehicle_config')

    def mobile_enabled(self) -> dict:
        '''Lets you know if the Mobile Access setting is enabled in the car.'''
        return get(self, 'mobile_enabled')

    def nearby_charging_sites(self) -> dict:
        '''Returns a list of nearby Tesla-operated charging stations.'''
        return get(self, 'nearby_charging_sites')

    def service_data(self) -> dict:
        '''Get service data from a Tesla.'''
        return get(self, 'service_data')
