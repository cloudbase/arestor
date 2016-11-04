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

"""REST-like API base-class.

(Beginning of) the contract that all the resources must follow.
"""

import cherrypy

from arestor.common import constant


class BaseAPI(object):

    """Contract class for all metadata providers."""

    _cp_config = {'tools.staticdir.on': False}

    exposed = True
    """Whether this application should be available for clients."""

    resources = None
    """A list that contains all the resources (endpoints) available for the
    current metadata service."""

    port = 80
    """The port that should be used by the current metadata service."""

    def __init__(self):
        self._raw_data = {}

        for raw_resource in self.resources:
            try:
                alias, resource = raw_resource
                setattr(self, alias, resource(self))
            except ValueError:
                cherrypy.log.error("Invalid resource %r provided.",
                                   raw_resource)

    @classmethod
    def config(cls):
        """Prepare the configurations for the current metadata service."""
        return {
            'global': {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': cls.port,
                'environment': 'production',
                'log.screen': False,
                'log.error_file': '{}.log'.format(cls.__name__),
                'server.thread_pool': constant.SERVICE_THREAD_POOL,
            },
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher()
            }
        }


class Resource(object):

    """Contract class for all the resources."""

    exposed = True
    """Whether this application should be available for clients."""

    allow_methods = []
    """A list which contains all the available HTTP methods."""

    def __init__(self, parent):
        self._parent = parent

    @property
    def parent(self):
        """Return the object that contains the current resource."""
        return self._parent
