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

"""The module contains the / endpoint object for Arestor API."""

import os

import cherrypy

from arestor.api import base as api_base
from arestor.api import admin as api_admin
from arestor.api import v1 as api_v1
from arestor import config as arestor_config
from arestor.common import tools as arestor_tools

cherrypy.tools.user_required = arestor_tools.UserManager()
CONFIG = arestor_config.CONFIG


class Root(api_base.BaseAPI):

    """The / endpoint for the Arestor API."""

    resources = [
        ("admin", api_admin.AdminEndpoint),
        ("v1", api_v1.ArestorV1),
    ]

    @classmethod
    def config(cls):
        """Prepare the configurations for the current metadata service."""
        return {
            'global': {
                'server.socket_host': CONFIG.api.host,
                'server.socket_port': CONFIG.api.port,
                'environment': CONFIG.api.environment,
                'log.screen': False,
                'log.error_file': os.path.join(CONFIG.log_dir or "",
                                               "arestor-api-error.log"),
                'server.thread_pool': CONFIG.api.thread_pool,
            },
            '/': {
                'request.dispatch': api_base.MethodDispatcher()
            }
        }
