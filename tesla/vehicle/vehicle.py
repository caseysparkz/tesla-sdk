#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:       Casey Sparks
# Date:         January 21, 2023
# Description:
'''Parent class for the Tesla vehicle API.'''

from locale import setlocale, LC_ALL
from logging import getLogger
from os import getenv
from typing import NoReturn, Optional
from urllib.parse import urljoin
from .command import Command
from .state import State


log = getLogger(__name__)                                                   # Enable logging

setlocale(LC_ALL, 'en_US.UTF-8')                                            # Set locale.


class Vehicle():
    '''Parent class for a Tesla vehicle.'''
    def __init__(
        self,
        client: type,
        data: dict,
        licence_plate: Optional[str] = None,
        speed_limit_pin: Optional[int] = getenv('TESLA_SPEED_PIN') or None,
        valet_pin: Optional[int] = getenv('TESLA_VALET_PIN') or None
            ) -> NoReturn:
        '''
        Vehicle class. Used to get data about, and send commands to, a Tesla vehicle.
            :param client:          Instance of tesla.Client().
            :param data:            Vehicle data as returned by tesla.account.Account.vehicles().
            :param speed_limit_pin: PIN for speed limit mode.
            :param valet_pin:       PIN for valet mode.
        '''
        self.data = {**data, **{'licence_plate': str(licence_plate)}}
        self.base_url = urljoin(client.base_url, f'vehicles/{data["id"]}/')
        self.headers = {**client.headers, **{'Authorization': f'Bearer {client.token["access_token"]}'}}
        self.Command = Command(self)
        self.State = State(self)

    def set_licence_plate(
        self,
        licence_plate: str
            ) -> NoReturn:
        '''
        Add licence plate data to Vehicle object.
            :param licence_plate:   The licence plate of your vehicle.
        '''
        if licence_plate.isalnum():
            self.data['licence_plate'] = licence_plate.upper()
        else:
            raise ValueError('`licence_plate` must be alpha-numeric.')
