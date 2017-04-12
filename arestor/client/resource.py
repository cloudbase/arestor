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
import requests

from arestor.client import base as base_client
from arestor.common import exception


class ResourceClient(base_client.Client):

    """Client for resource management."""

    def resources(self, namespace=None, client_id=None, resource=None):
        """Get all the available resources.

        The list can be filtered.
        :param namespace:
            Return the resources from a given namespace.
        :param client_id:
            Return the resources for a given client_id.
        :param resource:
            Return all the resources with a given name.
        """
        filters = {
            "namespace": namespace if namespace else "",
            "client_id": client_id if client_id else "",
            "resource": resource if resource else "",
        }

        url = "/admin/resource?{}".format(
            requests.compat.urlencode(filters))
        try:
            response = self.get(url)
            response.raise_for_status()
            resources = json.loads(response.text)
        except requests.HTTPError as ex:
            raise exception.ClientError(messag=ex)
        except ValueError:
            raise exception.ClientError(msg="Malformed response.")

        if not resources["meta"]["status"]:
            raise exception.ClientError(msg=resources["meta"]["verbose"])

        return resources["content"]

    def resource(self, resource_id):
        """Get the required resource."""
        url = "/admin/resource?{}".format(
            requests.compat.urlencode({"resource_id": resource_id}))
        try:
            response = self.get(url)
            response.raise_for_status()
            resource = json.loads(response.text)
        except requests.HTTPError as ex:
            raise exception.ClientError(msg=ex)
        except ValueError:
            raise exception.ClientError(msg="Malformed response.")

        if not resource["meta"]["status"]:
            raise exception.ClientError(msg=resource["meta"]["verbose"])

        return resource["content"]

    def create_resource(self, content):
        """Create a new resource."""
        try:
            response = self.post("/admin/resource", data=content)
            response.raise_for_status()
            data = json.loads(response.text)

        except requests.HTTPError as ex:
            raise exception.ClientError(msg=ex)
        except ValueError:
            raise exception.ClientError(msg="Malformed response.")

        if not data["meta"]["status"]:
            raise exception.ClientError(msg=data["meta"]["verbose"])

        return data["content"]

    def update_resource(self, resource_id, content):
        """Update the content of the given resource."""
        url = "/admin/resource?{}".format(
            requests.compat.urlencode({"resource_id": resource_id}))
        try:
            response = self.put(url, data=content)
            response.raise_for_status()
            resource = json.loads(response.text)
        except requests.HTTPError as ex:
            raise exception.ClientError(msg=ex)
        except ValueError:
            raise exception.ClientError(msg="Malformed response.")

        if not resource["meta"]["status"]:
            raise exception.ClientError(msg=resource["meta"]["verbose"])

        return resource["content"]

    def delete_resource(self, resource_id):
        """Delete the given resource."""
        url = "/admin/resource?{}".format(
            requests.compat.urlencode({"resource_id": resource_id}))
        try:
            response = self.delete(url)
            response.raise_for_status()
            resource = json.loads(response.text)
        except requests.HTTPError as ex:
            raise exception.ClientError(msg=ex)
        except ValueError:
            raise exception.ClientError(msg="Malformed response.")

        if not resource["meta"]["status"]:
            raise exception.ClientError(msg=resource["meta"]["verbose"])

        return resource["content"]
