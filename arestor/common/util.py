# Copyright 2016 Cloudbase Solutions Srl
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

"""A collection of utilities used across the project."""

import base64
import functools
import hashlib
import json

import cherrypy
from Crypto.Cipher import AES
from Crypto import Random
from oslo_log import log as logging
import redis

from arestor.common import exception
from arestor import config as arestor_config

CONFIG = arestor_config.CONFIG
LOG = logging.getLogger(__name__)


def get_attribute(root, attribute):
    """Search for the received attribute name in the object tree.

    :param root: the root object
    :param attribute: the name of the required attribute
    """
    command_tree = [root]
    while command_tree:
        current_object = command_tree.pop()
        if hasattr(current_object, attribute):
            return getattr(current_object, attribute)

        parent = getattr(current_object, "parent", None)
        if parent:
            command_tree.append(parent)

    raise exception.ArestorException("The %(attribute)r attribute is "
                                     "missing from the object tree.",
                                     attribute=attribute)


def check_credentials(method):
    """Check if the user has access to the required method."""

    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        """Check if the request is valid."""
        response = {
            "meta": {
                "status": kwargs.pop("status", True),
                "verbose": kwargs.pop("verbose", "OK")
            },
            "content": None
        }
        if not response["meta"]["status"]:
            cherrypy.response.headers['Content-Type'] = 'application/json'
            cherrypy.response.status = 400
            return json.dumps(response)
        return method(*args, **kwargs)

    return wrapper


class AESCipher(object):

    """Wrapper over AES Cipher."""

    def __init__(self, key):
        """Setup the new instance."""
        self._block_size = AES.block_size
        self._key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, message):
        """Encrypt the received message."""
        message = self._padding(message, self._block_size)
        initialization_vector = Random.new().read(self._block_size)
        cipher = AES.new(self._key, AES.MODE_CBC, initialization_vector)
        return base64.b64encode(initialization_vector +
                                cipher.encrypt(message))

    def decrypt(self, message):
        """Decrypt the received message."""
        message = base64.b64decode(message)
        initialization_vector = message[:self._block_size]
        cipher = AES.new(self._key, AES.MODE_CBC, initialization_vector)
        raw_message = cipher.decrypt(message[self._block_size:])
        return self._remove_padding(raw_message).decode('utf-8')

    @staticmethod
    def _padding(message, block_size):
        """Add padding."""
        return (message + (block_size - len(message) % block_size) *
                chr(block_size - len(message) % block_size))

    @staticmethod
    def _remove_padding(message):
        """Remove the padding."""
        return message[:-ord(message[len(message) - 1:])]


class RedisConnection(object):

    """High level wrapper over the redis data structures operations."""

    def __init__(self):
        """Instantiates objects able to store and retrieve data."""
        self._rcon = None
        self._host = CONFIG.redis.host
        self._port = CONFIG.redis.port
        self._db = CONFIG.redis.database
        self.refresh()

    def _connect(self):
        """Try establishing a connection until succeeds."""
        try:
            rcon = redis.StrictRedis(self._host, self._port, self._db)
            # Return the connection only if is valid and reachable
            if not rcon.ping():
                return None
        except (redis.ConnectionError, redis.RedisError) as exc:
            LOG.error("Failed to connect to Redis Server: %s", exc)
            return None

        return rcon

    def refresh(self, tries=3):
        """Re-establish the connection only if is dropped."""
        for _ in range(tries):
            try:
                if not self._rcon or not self._rcon.ping():
                    self._rcon = self._connect()
                else:
                    break
            except redis.ConnectionError as exc:
                LOG.error("Failed to connect to Redis Server: %s", exc)
        else:
            raise exception.ArestorException(
                "Failed to connect to Redis Server.")

        return True

    @property
    def rcon(self):
        """Return a Redis connection."""
        self.refresh()
        return self._rcon
