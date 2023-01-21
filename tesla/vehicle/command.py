#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:       Casey Sparks
# Date:         January 21, 2023
# Description:
'''Class for sending commands to the Tesla vehicle API.'''

import sys
from locale import setlocale, LC_ALL
from logging import getLogger
from random import randint
from typing import NoReturn, Optional, Union
from .._request_wrappers import post                                        # Generic POST wrappers for the Tesla API.

log = getLogger(__name__)                                                   # Enable logging

setlocale(LC_ALL, 'en_US.UTF-8')                                            # Set locale.


class Command():
    '''Vehicle module for the Tesla API.'''
    def __init__(
        self,
        parent_class: type
            ) -> NoReturn:
        '''
        Class for Tesla vehicle commands. Used to send commands to a Tesla vehicle.
            :param parent_class:    The parent Vehicle class.
        '''
        self.base_url = parent_class.base_url
        self.headers = parent_class.headers

    def _check_set(
        self,
        variable: Union[int, str, None]
            ) -> bool:
        '''
        Evaluates if a variable is None, tries to set it to user input if it is, and returns the same variable.
            :param variable: The variable to evaluate.
        '''
        if variable is None:                                                # Check if variable is set.
            var_name = f'{variable=}'.split('=')[0]                         # Extract var name string.

            if hasattr(sys, 'ps1'):                                         # Check if script is interactive.
                variable = input(f'Enter {var_name}: ')

            else:
                raise TypeError(f'{variable=}')

        return variable

    def wake_up(self) -> dict:
        '''Wakes up the car from a sleeping state.'''
        return post(self, 'wake_up')

    def honk_horn(self) -> dict:
        '''Honks the horn twice.'''
        return post(self, 'command/honk_horn')

    def flash_lights(self) -> dict:
        '''Flashes the headlights once.'''
        return post(self, 'command/flash_lights')

    def remote_start_drive(self) -> dict:
        '''Enables keyless driving. There is a two minute window after issuing the command to start driving the car.'''
        return post(self, 'command/remote_start_drive')

    def trigger_homelink(
        self,
        latitude: str,
        longitude: str
            ) -> dict:
        '''
        Opens or closes the primary Homelink device.
        The provided location must be in proximity of stored location of the Homelink device.
            :param latitude:    Latitude of the stored Homelink device location.
            :param longitude:   Longitude of the stored Homelink device location.
        '''
        return post(self, 'command/trigger_homelink', params={'lat': latitude, 'lon': longitude})

    def speed_limit_set_limit(
        self,
        limit_mph: int
            ) -> dict:
        '''
        Sets the maximum speed allowed when Speed Limit Mode is active.
            :param limit_mph:   The speed limit in MPH. Must be between 50-90.
        '''
        return post(self, 'command/speed_limit_set_limit', params={'limit_mph': limit_mph})

    def speed_limit_activate(self) -> dict:
        '''Activates Speed Limit Mode at the currently set speed.'''
        params = {'pin': self._check_set(self.speed_limit_pin)}

        return post(self, 'command/speed_limit_activate', params=params)

    def speed_limit_deactivate(self) -> dict:
        '''Deactivates Speed Limit Mode if it is currently active.'''
        params = {'pin': self._check_set(self.speed_limit_pin)}

        return post(self, 'command/speed_limit_deactivate', params=params)

    def speed_limit_clear_pin(self) -> dict:
        '''Clears the currently set PIN for Speed Limit Mode.'''
        params = {'pin': self._check_set(self.speed_limit_pin)}
        self.speed_limit_pin = None                                     # Unset PIN.

        return post(self, 'command/speed_limit_clear_pin', params=params)

    def set_valet_mode(
        self,
        on: bool = True,
        valet_pin: Optional[int] = randint(0, 1000)
            ) -> dict:
        '''
        Activates or deactivates Valet Mode.
            :param on:          True to activate, False to deactivate.
            :param valet_pin:   A PIN to deactivate Valet Mode. Chooses a random PIN if not provided.
        '''
        self.valet_pin = str(valet_pin).zfill(4)                        # Set valet PIN.

        return post(self, 'command/set_valet_mode', params={'password': self.valet_pin})

    def reset_valet_pin(self) -> dict:
        '''
        Clears the currently set PIN for Valet Mode when deactivated.
        A new PIN will be required when activating from the car screen.
        '''
        self.valet_pin = None                                           # Unset valet PIN.

        return post(self, 'command/reset_valet_pin')

    def set_sentry_mode(
        self,
        on: bool = True
            ) -> dict:
        '''
        Turns sentry mode on or off.
            :param on:  True to activate, False to deactivate.
        '''
        return post(self, 'command/set_sentry_mode', params={'on': on})

    def door_unlock(self) -> dict:
        '''Unlocks the doors to the car. Extends the handles on the Model S.'''
        return post(self, 'command/door_unlock')

    def door_lock(self) -> dict:
        '''Locks the doors to the car. Retracts the handles on the S, if they are extended.'''
        return post(self, 'command/door_lock')

    def actuate_trunk(
        self,
        which_trunk: str = 'rear'
            ) -> dict:
        '''
        Opens either the front or rear trunk. On the Model S and X, it will also close the rear trunk.
            :param which_trunk: Specify 'front' or 'rear'. Defaults 'rear'.
        '''
        return post(self, 'command/actuate_trunk')

    def window_control(
        self,
        command: str = 'close',
        latitude: Optional[str] = None,
        longitude: Optional[str] = None
            ) -> dict:
        '''
        Controls the windows. Will vent or close all windows simultaneously.
            :param command:     Specify 'vent' or 'close'.
            :param latitude:    Latitude of the vehicle.
            :param longitude:   Longitude of the vehicle.
        '''
        if all([latitude, longitude]) is False:
            gps_data = self.vehicle_data()['response']['drive_state']
            latitude = gps_data[latitude]
            longitude = gps_data[longitude]

        return post(self, 'command/window_control', params={'command': command, 'lat': latitude, 'lon': longitude})

    def sun_roof_control(
        self,
        command: str = 'close'
            ) -> dict:
        '''
        Controls the panoramic sunroof on the Model S.
            :param command: Specify 'vent' or 'close'.
        '''
        return post(self, 'command/sun_roof_control', params={'state': command})

    def charge_port_door_open(self) -> dict:
        '''Opens the charge port or unlocks the cable.'''
        return post(self, 'command/charge_port_door_open')

    def charge_port_door_close(self) -> dict:
        '''For vehicles with a motorized charge port, this closes it.'''
        return post(self, 'command/charge_port_door_close')

    def charge_start(self) -> dict:
        '''If the car is plugged in but not currently charging, this will start it charging.'''
        return post(self, 'command/charge_start')

    def charge_stop(self) -> dict:
        '''If the car is currently charging, this will stop it.'''
        return post(self, 'command/charge_stop')

    def charge_standard(self) -> dict:
        '''Sets the charge limit to "standard" or ~90%.'''
        return post(self, 'command/charge_standard')

    def charge_max_range(self) -> dict:
        '''Sets the charge limit to "max range" or 100%.'''
        return post(self, 'command/charge_max_range')

    def set_charge_limit(
        self,
        percent: int = 80
            ) -> dict:
        '''
        Sets the charge limit to a custom value.
            :param percent: The percentage the battery will charge until.
        '''
        return post(self, 'command/set_charge_limit', params={'percent': percent})

    def set_charging_amps(
        self,
        charging_amps: int = 22
            ) -> dict:
        '''
        Sets the charge amps limit to a custom value.
            :param charging_amps:   The max amps to use during charging.
        '''
        return post(self, 'command/set_charging_amps', params={'charging_amps': charging_amps})

    def set_scheduled_charging(
        self,
        enable: bool = False,
        time: int = 120
            ) -> dict:
        '''
        Sets the charge limit to a custom value.
            :param enable:  True for on, False for off.
            :param time:    Time in minutes since midnight local time.
        '''
        return post(self, 'command/set_scheduled_charging', params={'enable': enable, 'time': time})

    def set_scheduled_departure(
        self,
        enable: bool = False,
        departure_time: bool = False,
        preconditioning_enabled: bool = True,
        preconditioning_weekdays_only: bool = False,
        off_peak_charging_enabled: bool = True,
        off_peak_charging_weekdays_only: bool = False,
        end_off_peak_time: int = 120
            ) -> dict:
        '''
        Set the scheduled departure.
            :param enable: True for on, False for off.
            :param departure_time: True if (preconditioning_enabled or off_peak_charging_enabled), false otherwise.
            :param preconditioning_enabled: True for on, False for off.
            :param preconditioning_weekdays_only: True for on, False for off.
            :param off_peak_charging_enabled: True for on, False for off.
            :param off_peak_charging_weekdays_only: True for on, False for off.
            :param end_off_peak_time: Time in minutes since midnight local time.
        '''
        if preconditioning_enabled or off_peak_charging_enabled:
            departure_time = True

        params = {
            'enable': enable,
            'departure_time': departure_time,
            'preconditioning_enabled': preconditioning_enabled,
            'preconditioning_weekdays_only': preconditioning_weekdays_only,
            'off_peak_charging_enabled': off_peak_charging_weekdays_only,
            'end_off_peak_time': end_off_peak_time
        }

        return post(self, 'command/set_scheduled_departure', params=params)

    def auto_conditioning_start(self) -> dict:
        '''Start the climate control (HVAC) system. Will cool or heat automatically, depending on set temperature.'''
        return post(self, 'command/auto_conditioning_start')

    def auto_conditioning_stop(self) -> dict:
        '''Stop the climate control (HVAC) system.'''
        return post(self, 'command/auto_conditioning_stop')

    def set_temps(
        self,
        driver_temp: float,
        passenger_temp: Optional[float] = None
            ) -> dict:
        '''
        Sets the target temperature (in celcius) for the climate control (HVAC) system.
        Despite accepting two parameters, only the driver_temp will be used to set the target temperature,
        unless the "split" option is activated within the climate controls menu.
            :param driver_temp: The desired temperature on the driver's side in celsius.
            :param passenger_temp: The desired temperature on the passenger's side in celsius.
        '''
        params = {
            'driver_temp': driver_temp,
            'passenger_temp': passenger_temp
        }

        return post(self, 'command/auto_conditioning_stop', params=params)

    def set_preconditioning_max(
        self,
        on: bool = True
            ) -> dict:
        '''
        Toggles the climate controls between Max Defrost and the previous setting.
            :param on: True to turn on, False to turn off.
        '''
        return post(self, 'command/auto_conditioning_stop', params={'on': on})

    def remote_seat_heater_request(
        self,
        heater: int = 0,
        level: int = 1
            ) -> dict:
        '''
        Sets the specified seat's heater level.
            :param heater:  The desired seat to heat. (0-5)
            :param level:   The desired level for the heater. (0-3)

        The heater parameter maps to the following seats:
            0: Front Left
            1: Front right
            2: Rear left
            4: Rear center
            5: Rear right
        '''
        return post(self, 'command/auto_conditioning_stop', params={'heater': heater, 'level': level})
