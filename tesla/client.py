#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:       Casey Sparks
# Date:         January 21, 2023
# Description:
'''Tesla SDK'''

from base64 import urlsafe_b64encode
from datetime import datetime
from hashlib import sha256
from json import dump, dumps, load
from locale import setlocale, LC_ALL
from logging import getLogger
from os import chmod, urandom
from pathlib import Path
from stat import S_IWUSR, S_IRUSR, S_IRGRP
from time import ctime, time
from typing import NoReturn, Optional, Union
from urllib.parse import urljoin
from webbrowser import open as browser_open
from requests_oauthlib import OAuth2Session
from .__version__ import __version__
from .account import Account
from .vehicle import Vehicle


log = getLogger(__name__)                                                   # Enable logging

setlocale(LC_ALL, 'en_US.UTF-8')                                            # Set locale.


class JsonDict(dict):
    '''Pretty-printing dictionary.'''
    def __str__(self) -> str:
        '''Serialize dict to JSON-formatted string with indents.'''
        return dumps(self, indent=4)


class Client(OAuth2Session):
    '''Parent class for authentication and all other product and API classes.'''
    def __init__(
        self,
        email: str,
        user_agent: Optional[str] = f'{__name__}/{__version__}',
        cache_file: Optional[Path] = Path.home() / '.cache/tesla/cache.json',
        sso_base_url: Optional[str] = 'https://auth.tesla.com',
        app_user_agent: Optional[str] = 'TeslaApp/4.10.0',
        verify: bool = True,
        **kwargs
            ) -> NoReturn:
        '''
        Implements a session manager for the Tesla Motors Owner API
            :param email:           SSO identity.
            :param user_agent:      The User-Agent string.
            :param cache_file:      Path to cache file used by default loader and dumper.
            :param sso_base_url:    URL of SSO service.
            :param app_user_agent:  X-Tesla-User-Agent string.
            :param verify:          Verify SSL certificate.
        '''
        if not email:
            raise ValueError('`email` is not set')

        super(Client, self).__init__(client_id='ownerapi', **kwargs)
        self.auto_refresh_kwargs = {'client_id': 'ownerapi'}
        self.base_url = 'https://owner-api.teslamotors.com/api/1/'
        self.cache_file = cache_file
        self.email = email
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': user_agent,
            'X-Tesla-User-Agent': app_user_agent
        }
        self.sso_base_url = sso_base_url
        self.token = str()
        self.verify = verify
        self.account = None
        self.vehicles = None

        log.debug(f'Using SSO service URL: {self.sso_base_url}')
        log.debug(f'Using email {self.email}')

        if cache_file.exists():
            log.debug(f'Found cache file: {self.cache_file}')

        log.debug(f'Using headers: {self.headers}')

    @property
    def expires_at(self) -> str:
        '''Returns unix time when token needs refreshing.'''
        return self.token.get('expires_at')

    @property
    def expired(self) -> str:
        '''Returns unix time until token needs refreshing.'''
        return self.expires_at - time() <= 0

    @staticmethod
    def _new_code_verifier() -> str:
        '''Generate code verifier for PKCE per RFC 7636 section 4.1.'''
        code_verifier = urlsafe_b64encode(urandom(32)).rstrip(b'=')

        log.debug(f'Generated new code verifier: {code_verifier.decode("utf-8")}')

        return code_verifier

    @staticmethod
    def _authenticate(
        url: str
            ) -> str:
        '''
        Default authenticator method.
            :param url: Login URL for tesla.com.
        '''
        print('Use browser to login. Page Not Found will be shown at success.')

        if browser_open(url):
            log.debug(f'Opened {url} with default browser')
        else:
            print(f'Open this URL to authenticate: {url}')

        return input('Enter URL after authentication: ')

    def _load_cache(self) -> dict:
        '''Default cache loader method.'''
        try:
            cache = load(open(self.cache_file))

            if cache[self.email]['sso']['expires_at'] <= datetime.now().strftime('%s'):
                self.expired = True                                         # Token expired. Empty cache.

        except BaseException:
            log.warning(f'Cannot load cache: {self.cache_file}')

            if not self.cache_file.parent.exists():
                self.cache_file.parent.mkdir()                              # Create config file parent directory.

            cache = dict()

        log.debug(f'Cache: {cache}')

        return cache

    def _dump_cache(
        self,
        cache: dict
            ) -> NoReturn:
        '''
        Default cache dumper method.
            :param cache: Response dict returned by self._fetch_token.
        '''
        try:
            dump(cache, open(self.cache_file, 'w'))
            chmod(self.cache_file, (S_IWUSR | S_IRUSR | S_IRGRP))

        except IOError:
            log.error('Cache not updated')

        else:
            log.debug(f'Dumped cache to {self.cache_file.absolute().__str__()}')

    def _token_updater(
        self,
        token: Optional[str] = None
            ) -> NoReturn:
        '''
        Handles token persistency. Raises ValueError.
            :param token:
        '''
        cache = self._load_cache()

        if not isinstance(cache, dict):
            raise ValueError('`self._load_cache()` must return dict.')

        if self.authorized and not self.expired:                            # Write token to cache.
            cache[self.email] = {'url': self.sso_base_url, 'sso': self.token}
            self._dump_cache(cache)

        elif self.email in cache:                                           # Read token from cache.
            self.sso_base_url = cache[self.email].get('url', self.sso_base_url)
            self.token = cache[self.email].get('sso', dict())

            if not self.token:
                return

            if 0 < self.expires_at < time():                                # Log the token validity.
                log.debug('Cached SSO token expired. Fetching new token.')
                self.fetch_token()
            else:
                log.debug(f'Cached SSO token expires at {ctime(self.expires_at)}.')

        else:
            log.critical(f'No cached credentials found in {self.cache_file.absolute().__str__()}.')

    def authorization_url(
        self,
        auth_url_path: str = '/oauth2/v3/authorize',
        **kwargs
            ) -> Union[str, None]:
        '''
        Overriddes base method to form an authorization URL with PKCE extension for Tesla's SSO service.
            :param auth_url_path:   Authorization endpoint url.
            :kwarg state:           A state string for CSRF protection.
        '''
        if self.authorized:
            return None

        # Generate code verifier, challenge.
        self.code_verifier = self._new_code_verifier()
        kwargs['code_challenge'] = urlsafe_b64encode(sha256(self.code_verifier).digest()).rstrip(b'=')
        kwargs['code_challenge_method'] = 'S256'
        url = urljoin(self.sso_base_url, auth_url_path)
        without_hint, state = super(Client, self).authorization_url(url, **kwargs)
        # Detect account's registered region
        kwargs['login_hint'] = self.email
        kwargs['state'] = state
        with_hint = super(Client, self).authorization_url(url, **kwargs)[0]
        response = self.get(with_hint, allow_redirects=False)

        if response.is_redirect:
            with_hint = response.headers['Location']
            self.sso_base_url = urljoin(with_hint, '/')
            log.debug(f'New SSO service URL {self.sso_base_url}')

        return with_hint if response.ok else without_hint

    def fetch_token(
        self,
        token_path: str = 'oauth2/v3/token',
        **kwargs
            ) -> dict:
        '''
        Overriddes base method to sign into Tesla's SSO service using Authorization Code grant with PKCE extension.
            :param token_path:              Token endpoint URL.
            :kwarg authorization_response:  Authorization response URL.
            :kwarg code_verifier:           Code verifier cryptographic random string.
        '''
        if self.authorized:
            return self.token

        if kwargs.get('authorization_response') is None:                    # Open SSO page for user auth.
            kwargs['authorization_response'] = self._authenticate(self.authorization_url())

        # Use authorization code in redirected location to get token.
        kwargs['include_client_id'] = True

        kwargs.setdefault('code_verifier', self.code_verifier)
        kwargs.setdefault('verify', self.verify)
        super(Client, self).fetch_token(urljoin(self.sso_base_url, token_path), **kwargs)
        self._token_updater()                                               # Save new token

        self.account = Account(self)                                        # Instantiate Account subclass.

        return self.token

    def refresh_token(
        self,
        token_path: str = 'oauth2/v3/token',
        **kwargs
            ) -> dict:
        '''
        Overriddes base method to refresh Tesla's SSO token. Raises ValueError and ServerError.
            :param token_path:       The token endpoint.
            :kwarg refresh_token:   The refresh_token to use.
        '''
        if not self.authorized and not kwargs.get('refresh_token'):
            raise ValueError('`refresh_token` is not set')

        kwargs.setdefault('verify', self.verify)
        super(Client, self).refresh_token(urljoin(self.sso_base_url, token_path), **kwargs)
        self._token_updater()                                               # Save new token.

        return self.token

    def close(self) -> NoReturn:
        '''Overriddes base method to remove all adapters on close.'''
        super(Client, self).close()
        self.adapters.clear()

    def logout(
        self,
        sign_out: bool = False
            ) -> Union[str, None]:
        '''
        Removes token from cache, returns logout URL, and optionally logs out of default browser.
            :param sign_out: Sign out using system's default web browser.
        '''
        if not self.authorized:
            return None

        url = urljoin(self.sso_base_url, '/oauth2/v3/logout?client_id=ownerapi')

        if sign_out:                                                        # Built-in signout method
            if browser_open(url):
                log.debug(f'Opened {url} with default browser')
            else:
                print(f'Open this URL to sign out: {url}')

        self.token = dict()                                                 # Empty token dict.

        self._token_updater()                                               # Update token.

        del self.access_token

        return url

    def login(self) -> NoReturn:
        '''Log in to the Tesla API and populate account data.'''
        self._token_updater()                                               # Try to read token from cache
        self.fetch_token()                                                  # Log in if not authed.
        self.vehicles = {                                                   # Map vehicles by name.
            vehicle['display_name']: Vehicle(self, vehicle)
            for vehicle
            in self.account.vehicles
        }
