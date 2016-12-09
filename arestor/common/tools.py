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

"""This module contains a collection of tools used across the project."""

import hashlib
import json
import uuid

from Crypto import Random
import cherrypy
from oslo_log import log as logging

from arestor import config as arestor_config
from arestor.common import util as arestor_util

CONFIG = arestor_config.CONFIG
LOG = logging.getLogger(__name__)


class Users(object):

    def __init__(self):
        connection = arestor_util.RedisConnection()
        self._redis = connection.rcon

    def get_secret(self, api_key):
        """Get the secret for the user with received api key."""
        return self._redis.hget("user.secret", api_key)

    def get_user(self, api_key):
        """Get information regarding user which has received api key."""
        return json.load(self._redis.hget("user.info", api_key))

    def add_user(self, user):
        """Add a new user into the database."""
        api_key = uuid.uuid1().hex
        user_secret = hashlib.sha256(Random.new().read(1024)).hexdigest()

        self._redis.hset("user.info", api_key, json.dumps(user))
        self._redis.hset("user.secret", api_key, user_secret)

    def remove_user(self, api_key):
        """Remove the user from the database."""
        for hash_name in ("user.info", "user.secret"):
            if self._redis.hexists(hash_name, api_key):
                self._redis.hdel(hash_name, api_key)

    def list_users(self):
        """List all the available information regarding the users."""
        user_info = self._redis.hgetall("user.info")
        for api_key, information in user_info.items():
            user_info[api_key] = json.loads(information)
        return user_info


class UserManager(cherrypy.Tool):

    """Check if the request is valid and the resource is available."""

    def __init__(self):
        """Setup the new instance."""
        super(UserManager, self).__init__('before_handler', self.load,
                                          priority=10)
        self._users = Users()

    @staticmethod
    def _process_content(secret):
        """Get information from request and update request params."""
        request = cherrypy.request
        content = request.params.pop('content', None)
        if not content:
            return True

        cipher = arestor_util.AESCipher(secret)
        try:
            params = json.loads(cipher.decrypt(content))
        except ValueError as exc:
            LOG.error("Failed to decrypt content: %s", exc)
            return False

        if not isinstance(params, dict):
            LOG.error("Invalid content type provided: %s", type(params))
            return False

        for key, value in params.items():
            request.params[key] = value

        return True

    def load(self):
        """Process information received from client."""
        request = cherrypy.request
        api_key = request.params.get('api_key')
        secret = self._users.get_secret(api_key)

        request.params["status"] = False
        request.params["verbose"] = "OK"

        if not secret:
            request.params["verbose"] = "Invalid api key provided."
            return

        if not self._process_content(secret):
            request.params["verbose"] = "Invalid request."
            return

        request.params["status"] = True
