#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:       Casey Sparks
# Date:         January 21, 2023
# Description:
'''Generic wrappers for requests to the Tesla API.'''

from locale import setlocale, LC_ALL
from logging import getLogger
from typing import Optional
from urllib.parse import urljoin
from requests import get as rget, post as rpost, HTTPError

log = getLogger(__name__)                                                   # Enable logging

setlocale(LC_ALL, 'en_US.UTF-8')                                            # Set locale.


def get(
    tesla_object: type,
    endpoint: str,
    params: Optional[dict] = None
        ) -> dict:
    '''
    Send an arbitrary GET request to the Tesla owner's API.
        :param tesla_object:    `account.Account`, `energy.Energy`, or `vehicle.Vehicle` class.
        :param endpoint:        The REST API endpoint to request.
        :param params:          Optional HTTP parameters to send in the request.
    '''
    url = urljoin(tesla_object.base_url, endpoint)

    log.debug(f'Url: {url}')
    log.debug(f'Headers: {tesla_object.headers}')
    log.debug(f'Params: {params}')

    try:
        response = rget(
            url,
            headers=tesla_object.headers,
            params=params
        )
        log.debug(response)

        return response.json()['response']

    except HTTPError as err:
        raise err


def post(
    tesla_object: type,
    endpoint: str,
    params: Optional[dict] = None,
    data: Optional[dict] = None
        ) -> dict:
    '''
    Send an arbitrary POST request to the Tesla owner's API.
        :param tesla_object:    `Tesla` or `Vehicle` class.
        :param endpoint:        The REST API endpoint to POST to.
        :param params:          www-form-encoded parameters.
        :param data:            Data to send in the body of the request.
    '''
    url = urljoin(tesla_object.base_url, endpoint)

    log.debug(f'Url: {url}')
    log.debug(f'Headers: {tesla_object.headers}')
    log.debug(f'Data: {data}')
    log.debug(f'Params: {params}')

    try:
        response = rpost(
            url,
            headers=tesla_object.headers,
            data=data,
            params=params
        )

        log.debug(response)

        return response.json()['response']

    except HTTPError as err:
        raise err
