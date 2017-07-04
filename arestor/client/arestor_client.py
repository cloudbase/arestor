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
import posixpath

from requests import compat as url_parse

from arestor.client import resource as base_client
from arestor.common import constant


def _append_forward_slash(base):
    """Append a forward slash if it's not present."""
    if not base.endswith("/"):
        base += "/"
    return base


def _url_join(base, *args):
    """Join the url fragments."""
    base = _append_forward_slash(base)
    # NOTE(mmicu): pylint is not aware about the fact
    # that we are unpacking a list here
    # pylint: disable=no-value-for-parameter
    return _append_forward_slash(
        url_parse.urljoin(base, posixpath.join(*args)))


class ArestorClient(base_client.ResourceClient):
    """Arestor client."""

    def __init__(self, base_url, api_key, secret, client_id, namespace=""):
        super(ArestorClient, self).__init__(base_url, api_key, secret)
        self._client_id = client_id
        self._namespace = namespace

        self._base_info = {
            "client_id": self._client_id,
            "namespace": self._namespace,
        }

    @property
    def client_id(self):
        """Return the client id."""
        url = _url_join(self._base_url, self._client_id, self._namespace)
        return url

    def _get_resource(self, resource_name):
        """Get resource in the mocked meta-data."""
        key = constant.KEY_FORMAT.format(
            namespace=self._base_info["namespace"],
            user=self._base_info["client_id"],
            name=resource_name)

        data = self.resource(key).get("data", {})
        try:
            data = json.loads(data)
        except ValueError:
            pass
        return data

    def get_url(self):
        """Return the url for this client."""
        url = _url_join(self._base_url, 'v1', self._namespace, self._client_id)
        return url

    def set_namespace(self, namespace):
        """Set a specific namespace."""
        self._namespace = namespace

        # TODO(mmicu): make this a @property method
        self._base_info = {
            "client_id": self._client_id,
            "namespace": self._namespace,
        }

    def _create_resource(self, resource_name, resource_data):
        """Create a new resource in the mocked meta-data."""
        data = {
            "resource": resource_name,
            "data": json.dumps(resource_data)
        }
        data.update(self._base_info)
        self.create_resource(data)

    def set_hostname(self, hostname):
        """Set the hostname in the mocked meta-data."""
        self._create_resource("hostname", hostname)

    def set_uuid(self, uuid):
        """Set the uuid in the mocked meta-data."""
        self._create_resource("uuid", uuid)

    def set_random_seed(self, random_seed):
        """Set the random_seed in the mocked meta-data."""
        self._create_resource("random_seed", random_seed)

    def set_availability_zone(self, availability_zone):
        """Set the availability_zone in the mocked meta-data."""
        self._create_resource("availability_zone", availability_zone)

    def set_launch_index(self, launch_index):
        """Set the launch_index in the mocked meta-data."""
        self._create_resource("launch_index", launch_index)

    def set_project_id(self, project_id):
        """Set the project_id in the mocked meta-data."""
        self._create_resource("project_id", project_id)

    def set_name(self, name):
        """Set the name in the mocked meta-data."""
        self._create_resource("name", name)
        self._create_resource("hostname", name)

    def set_ssh_pubkeys(self, ssh_keys):
        self._create_resource("public_keys", ssh_keys)

    def set_keys(self, cert_keys):
        self._create_resource("keys", cert_keys)

    def set_metadata(self, metadata):
        self._create_resource("metadata", metadata)

    def set_user_data(self, userdata):
        self._create_resource("user_data", userdata)

    def get_password(self):
        return self._get_resource("password")

    def get_ssh_pubkeys(self):
        ssh_keys = self._get_resource("public_keys")
        return ssh_keys

    def delete_all_data(self):
        """Delete all meta_data for the current client_id."""
        for resource_id in self.resources(client_id=self._client_id):
            self.delete_resource(resource_id)
