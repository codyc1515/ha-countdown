"""Countdown API"""
import logging
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import json

_LOGGER = logging.getLogger(__name__)

class CountdownApi:
    def __init__(self, token):
        self._api_token = token
        self._customer_id = ''
        self._url_base = 'https://au-api-cnc.localz.io/v1/projects/M3YwdQlhHfM8hIZMulUv9QTDlpg4T6BXL5Br6000/customers'

    def get_deliveries(self):
        headers = {
            "x-localz-chanid": "ios",
            "x-localz-deviceid": "8AACD7E1-B75E-4F15-912C-47BA3222C079",
            "x-localz-cnc-sdk-ver": "4.3.1"
        }
        response = requests.get(self._url_base + "/" + self._customer_id + "/orders?includeCompleted=true", headers=headers, auth=HTTPBasicAuth('M3YwdQlhHfM8hIZMulUv9QTDlpg4T6BXL5Br6000', 'd71SUBJCbQRr3h5hYv9b8oN0l6kGBTuCyIY8uI5r'))
        data = {}
        if response.status_code == requests.codes.ok:
            data = response.json()
            if not data:
                _LOGGER.warning('Fetched deliveries successfully, but did not find any')
            return data
        else:
            _LOGGER.error('Failed to fetch deliveries')
            return data

    def check_auth(self):
        """Check to see if our customerId is valid."""
        if self._customer_id:
            _LOGGER.debug('Login is valid')
            return True
        else:
            if self.login() == False:
                _LOGGER.debug(result.text)
                return False
            return True

    def login(self):
        """Login to the Countdown API."""
        result = False
        data = {
            "userName": self._api_token,
            "password": "password"
        }
        headers = {
            "x-localz-chanid": "ios",
            "x-localz-deviceid": "8AACD7E1-B75E-4F15-912C-47BA3222C079",
            "x-localz-cnc-sdk-ver": "4.3.1"
        }
        loginResult = requests.post(self._url_base + "/login", json=data, headers=headers, auth=HTTPBasicAuth('M3YwdQlhHfM8hIZMulUv9QTDlpg4T6BXL5Br6000', 'd71SUBJCbQRr3h5hYv9b8oN0l6kGBTuCyIY8uI5r'))
        if loginResult.status_code == requests.codes.ok:
            jsonResult = loginResult.json()
            self._customer_id = jsonResult['customerId']
            _LOGGER.debug('Successfully logged in')
            self.get_deliveries()
            result = True
        else:
            _LOGGER.error(loginResult.text)
        return result
