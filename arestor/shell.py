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

"""This module contains the entry point for the command line application."""

import argparse
import sys

from oslo_log import log as logging

from arestor.cli import base as cli_base
from arestor.cli import commands as cli_commands
from arestor import config

CONFIG = config.CONFIG


class ArestorCli(cli_base.Application):

    """Command line application for interacting with Arestor."""

    commands = [
        (cli_commands.Server, "commands"),
        (cli_commands.User, "commands"),
    ]

    def setup(self):
        """Setup the command line parser.

        Extend the parser configuration in order to expose all
        the received commands.
        """
        self._parser = argparse.ArgumentParser()
        commands = self._parser.add_subparsers(title="[commands]",
                                               dest="command")

        self._register_parser("commands", commands)


def main():
    """The Arestor command line application."""
    logging.setup(CONFIG, "arestor")
    arestor = ArestorCli(sys.argv[1:])
    arestor.run()
    return arestor.result
