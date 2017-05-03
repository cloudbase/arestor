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


"""Arestor API endpoint for resource management."""

import cherrypy

from arestor.api import base as base_api
from arestor.common import tools as arestor_tools
from arestor.common import util as arestor_util

# TODO(mmicu): Find a better way to expose this tool
cherrypy.tools.user_required = arestor_tools.UserManager()

KEY_FORMAT = "{namespace}/{user}/{name}"


class ResourceEndpoint(base_api.Resource):

    exposed = True

    """Resource management endpoint."""

    @cherrypy.tools.user_required()
    @arestor_util.check_credentials
    @cherrypy.tools.json_out()
    def GET(self, resource_id="*", namespace="*", client_id="*",
            resource="*"):
        """The representation of userdata resource."""
        connection = self._redis.rcon
        response = {"meta": {"status": True, "verbose": "Ok"}, "content": None}

        if resource_id:
            # Prepare the representation of the received resource.
            resource = connection.hgetall(resource_id)
            if not resource:
                response["meta"]["status"] = False
                response["meta"]["verbose"] = "Resource not found"

            response["content"] = resource
            return response

        key = KEY_FORMAT.format(namespace=namespace, user=client_id,
                                name=resource)
        mockdata = connection.keys(pattern=key)
        response["content"] = mockdata
        return response

    @cherrypy.tools.user_required()
    @arestor_util.check_credentials
    @cherrypy.tools.json_out()
    def POST(self, client_id=None, namespace=None, resource=None, **kwargs):
        """Create a new resource."""
        connection = self._redis.rcon
        response = {"meta": {"status": True, "verbose": "Ok"}, "content": None}

        if not all([client_id, namespace, resource]):
            response["meta"]["status"] = False
            response["meta"]["verbose"] = "Incomplete resource description."
            cherrypy.response.status = 400
            return response

        key = KEY_FORMAT.format(user=client_id, namespace=namespace,
                                name=resource)

        response["content"] = kwargs
        for name, value in kwargs.items():
            connection.hset(key, name, value)

        return response

    @cherrypy.tools.user_required()
    @arestor_util.check_credentials
    @cherrypy.tools.json_out()
    def PUT(self, resource_id, **content):
        """Update the required resource."""
        connection = self._redis.rcon
        response = {"meta": {"status": True, "verbose": "Ok"}, "content": None}

        if not connection.exists(resource_id):
            response["meta"]["status"] = False
            response["meta"]["verbose"] = "Resource not found"
            return response

        for name, value in content.items():
            connection.hset(resource_id, name, value)

        new_content = connection.hgetall(resource_id)
        response["content"] = new_content
        return response

    @cherrypy.tools.user_required()
    @arestor_util.check_credentials
    @cherrypy.tools.json_out()
    def DELETE(self, resource_id):
        """Delete the required resource."""
        connection = self._redis.rcon
        response = {"meta": {"status": True, "verbose": "Ok"}, "content": None}

        connection.delete(resource_id)
        return response
