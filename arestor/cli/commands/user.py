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

from __future__ import print_function

from oslo_log import log as logging
import prettytable

from arestor.cli import base as cli_base
from arestor.common import tools as arestor_tools


LOG = logging.getLogger(__name__)


class _AddUser(cli_base.Command):

    """Add a new API client."""

    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        parser = self._parser.add_parser(
            "add", help="Add a new API client.")
        parser.add_argument(
            "--name", dest="name", required=True,
            help="The name of the client.")
        parser.add_argument(
            "--description", dest="description", required=True,
            help="More information regarding the new client.")
        parser.set_defaults(work=self.run)

    def _work(self):
        """Add a new API client."""
        users = arestor_tools.Users()
        users.add_user({"name": self.args.name,
                        "description": self.args.description})


class _RemoveUser(cli_base.Command):

    """Remove an API client."""

    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        parser = self._parser.add_parser(
            "remove", help="Remove an API client.")
        parser.add_argument(
            "--api-key", dest="api_key", required=True,
            help="The client key id.")
        parser.set_defaults(work=self.run)

    def _work(self):
        """Remove an API client."""
        users = arestor_tools.Users()
        return users.remove_user(api_key=self.args.api_key)


class _ListUsers(cli_base.Command):

    """List all the available users."""

    def _on_task_done(self, result):
        """What to execute after successfully finished processing a task."""
        table = prettytable.PrettyTable(["API Key", "Name", "Description"])
        for api_key, info in result.items():
            table.add_row([api_key, info["name"], info["description"]])
        print(table)

    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        parser = self._parser.add_parser(
            "list", help="List all the available users.")
        parser.set_defaults(work=self.run)

    def _work(self):
        """List all the available users."""
        users = arestor_tools.Users()
        return users.list_users()


class _ShowSecret(cli_base.Command):

    """Show the secret for a given user."""

    def _on_task_done(self, result):
        """What to execute after successfully finished processing a task."""
        table = prettytable.PrettyTable(["API Key", "Secret"])
        if result:
            table.add_row(result)
        print(table)

    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        parser = self._parser.add_parser(
            "show-secret", help="Show the secret for a given user.")
        parser.add_argument(
            "--api-key", dest="api_key", required=True,
            help="The client key id.")
        parser.set_defaults(work=self.run)

    def _work(self):
        """Return a specific user."""
        users = arestor_tools.Users()
        secret = users.get_secret(api_key=self.args.api_key)
        if secret:
            return self.args.api_key, secret
        else:
            return None


class User(cli_base.Group):

    """Group for all the available user actions."""

    commands = [
        (_AddUser, "actions"),
        (_RemoveUser, "actions"),
        (_ListUsers, "actions"),
        (_ShowSecret, "actions"),
    ]

    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        parser = self._parser.add_parser(
            "user", help="Operations related to users management.")

        actions = parser.add_subparsers()
        self._register_parser("actions", actions)
