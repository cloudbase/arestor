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

"""Arestor API endpoint for Packet Mocked Metadata."""

import json
import base64
import cherrypy

from oslo_log import log as logging

from arestor.api import base as base_api
from arestor.common import exception
from arestor.common import util as arestor_util


LOG = logging.getLogger(__name__)

FAKE_PHONE_HOME_URL = "fake_phone_home_url"


class _PacketResource(base_api.Resource):
    """Base class for Packet resources."""

    exposed = True

    def _get_packet_data(self, name, field=None):
        """Retrieve the required resource from the Packet namespace"""
        data = None
        try:
            data = self._get_data(namespace="packet",
                                  name=name, field=field)
            if field == "data":
                data = json.loads(arestor_util.get_as_string(data))
        except (exception.NotFound, ValueError):
            pass
        return data

    def _set_packet_data(self, name, field=None, value=None):
        """Set the required resource from the Packet namespace."""
        data = None
        try:
            data = self._set_data(namespace="packet",
                                  name=name, field=field, value=value)
        except (ValueError, TypeError):
            pass
        return data


class _InstanceIdResource(_PacketResource):

    def GET(self):
        return self._get_packet_data("uuid", "data")


class _HostnameResource(_PacketResource):

    def GET(self):
        return self._get_packet_data("hostname", "data")


class _SSHKeysResource(_PacketResource):

    # pylint: disable=invalid-name, redefined-builtin
    @cherrypy.popargs('id')
    def GET(self, id=None):
        keys = self._get_packet_data("public_keys", "data")
        if id is None:
            if keys:
                return str(len(keys))
            return "0"
        else:
            return keys[int(id)]


class _PhoneHomeUrlKey(_PacketResource):

    def GET(self):
        public_keys = self._get_packet_data("public_keys", "data").values()
        if public_keys:
            return public_keys[0]
        return None


class _PhoneHomeUrlPassword(_PacketResource):

    def GET(self):
        return self._get_packet_data("password_home_phone", "data")


class _UserdataResource(_PacketResource):

    def GET(self):
        """The representation of userdata resource."""
        userdata = self._get_packet_data("user_data", "data")
        if userdata:
            return base64.b64decode(userdata)
        return ""


class _PhoneHomeUrlResource(base_api.BaseAPI, _PacketResource):

    resources = [
        ("key", _PhoneHomeUrlKey),
        ("password", _PhoneHomeUrlPassword)
    ]

    # pylint: disable=bad-super-call
    def __init__(self, *args):
        super(_PhoneHomeUrlResource, self).__init__()
        super(_PacketResource, self).__init__(*args)

    @cherrypy.tools.json_out()
    def GET(self):
        public_keys = self._get_packet_data("public_keys", "data").values()
        try:
            key = public_keys[0]
        except IndexError:
            key = None
        return {
            "key": key,
            "password": self._get_packet_data("password_home_phone", "data")
        }

    def POST(self):
        password = str(cherrypy.request.body.read())
        if password:
            self._set_packet_data("password_home_phone", "data",
                                  json.loads(password).get('password'))
        return {"meta": {"status": True, "verbose": "Ok"}, "content": None}


class _Metadata(base_api.BaseAPI, _PacketResource):

    exposed = True
    resources = [
        ("id", _InstanceIdResource),
        ("hostname", _HostnameResource),
        ("ssh_keys", _SSHKeysResource),
        ("phone_home_url", _PhoneHomeUrlResource),
    ]

    # pylint: disable=bad-super-call
    def __init__(self, *args):
        super(_Metadata, self).__init__()
        super(_PacketResource, self).__init__(*args)

    @cherrypy.tools.json_out()
    def GET(self):
        meta_data = {
            "id": self._get_packet_data("uuid", "data"),
            "hostname": self._get_packet_data("hostname", "data"),
            "ssh_keys": self._get_packet_data("public_keys", "data"),
            "phone_home_url": '/'.join([PacketEndpoint.get_base_url(),
                                        FAKE_PHONE_HOME_URL]),
        }
        return meta_data


class PacketEndpoint(base_api.BaseAPI):

    """Arestor API endpoint for Packet Mocked Metadata."""

    resources = [
        ("metadata", _Metadata),
        ("userdata", _UserdataResource),
        (FAKE_PHONE_HOME_URL, _PhoneHomeUrlResource)
    ]
    """A list that contains all the resources (endpoints) available for the
    current metadata service."""

    exposed = True
    """Whether this application should be available for clients."""

    def __getattr__(self, name):
        """Handle for invalid resource name or alias."""

        # Note(alexcoman): The cherrypy MethodDispatcher will replace the
        # `-` from the resource / endpoint name with `_`. In order to avoid
        # any problems we will try to avoid this scenario.
        if "_" in name:
            return self.__dict__.get(name.replace("_", "-"))

        raise AttributeError("%r object has no attribute %r" %
                             (self.__class__.__name__, name))

    @classmethod
    def get_base_url(cls):
        url = cherrypy.url()
        while not url.split('/')[-1].startswith("instance-"):
            url = '/'.join(url.split('/')[:-1])
        return url
