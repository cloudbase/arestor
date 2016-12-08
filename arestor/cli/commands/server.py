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

import os
import signal

import cherrypy
from oslo_log import log as logging

from arestor import api as arestor_api
from arestor.cli import base as cli_base
from arestor.common import constant
from arestor.common import exception


LOG = logging.getLogger(__name__)


class Start(cli_base.Command):

    """Start the Arestor API."""

    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        parser = self._parser.add_parser("start",
                                         help="Start the Arestor API.")
        parser.set_defaults(work=self.run)

    def _work(self):
        """Start the Arestor API."""
        pid = os.getpid()
        with open(constant.PID_TMP_FILE, "w") as file_handle:
            file_handle.write(str(pid))
        cherrypy.quickstart(arestor_api.Root(), "/", arestor_api.Root.config())


class Stop(cli_base.Command):

    """Stop the Arestor API."""

    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        parser = self._parser.add_parser("stop", help="Stop the Arestor API.")
        parser.set_defaults(work=self.run)

    def _work(self):
        """Stop the Arestor API."""
        pid = None
        try:
            with open(constant.PID_TMP_FILE, "r") as file_handle:
                pid = int(file_handle.read().strip())
        except (ValueError, OSError) as exc:
            LOG.error("Failed to get server PID: %s", exc)
            raise exception.NotFound("Failed to get server PID.")

        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as exc:
            LOG.error("Failed to shutdown the server: %s", exc)
            return False

        return True


class Server(cli_base.Group):

    """Group for all the available server actions."""

    commands = [(Start, "actions"), (Stop, "actions")]

    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        parser = self._parser.add_parser(
            "server",
            help="Operations related to the Arestor API (start/stop).")

        actions = parser.add_subparsers()
        self._register_parser("actions", actions)
