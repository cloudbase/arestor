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


"""Arestor API version 1."""

from arestor.api import base as base_api
from arestor.api.v1 import openstack


class ArestorV1(base_api.BaseAPI):

    """Arestor API version 1."""

    resources = [
        ("openstack", openstack.OpenStackEndpoint),
    ]
    """A list that contains all the resources (endpoints) available for the
    current metadata service."""

    exposed = True
    """Whether this application should be available for clients."""
