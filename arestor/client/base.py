# Copyright 2017 Cloudbase Solutions Srl
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import time

import requests

from arestor.common import exception
from arestor.common import util as arestor_util


class BaseClient(object):

    def __init__(self, base_url):
        self._base_url = base_url

    def _request(self, method, resource, data=None):
        """Send a request to the Arestor API."""
        url = requests.compat.urljoin(self._base_url, resource)
        try:
            response = requests.request(method=method, url=url,
                                        data=data)
        except requests.RequestException as exc:
            raise exception.ClientError(exc)

        return response

    def get(self, resource):
        """Get the required resource."""
        return self._request("GET", resource)

    def post(self, resource, data):
        """Create a new resource."""
        return self._request("POST", resource, data)

    def put(self, resource, data):
        """Update an existing resource."""
        return self._request("PUT", resource, data)

    def delete(self, resource):
        """Delete the required resource."""
        return self._request("DELETE", resource)


class Client(BaseClient):

    """Basic Arestor API client."""

    def __init__(self, base_url, api_key, secret):
        super(Client, self).__init__(base_url)
        self._key = api_key
        self._cipher = arestor_util.AESCipher(secret)

    def _get_auth_params(self):
        """Get the required authentication parameters."""
        params = {"api_key": self._key, "timestamp": str(time.time())}
        signature = self._cipher.encrypt(json.dumps(params))
        params["signature"] = signature
        return params

    def _request(self, method, resource, data=None):
        """Send a request to the Arestor API."""
        url = requests.compat.urljoin(self._base_url, resource)
        content = data or self._cipher.encrypt(json.dumps(data))
        return requests.request(method=method, url=url,
                                params=self._get_auth_params(),
                                data=content)
