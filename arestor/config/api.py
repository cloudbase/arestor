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

"""Config options available for the arestor setup."""

from oslo_config import cfg

from arestor.config import base as conf_base


class ArestorAPIOptions(conf_base.Options):

    """Config options available for the arestor setup."""

    def __init__(self, config):
        super(ArestorAPIOptions, self).__init__(config, group="api")
        self._options = [
            cfg.StrOpt(
                "host", default="127.0.0.1",
                help="The IP address or the host name of the server."),
            cfg.IntOpt(
                "port", default=8080, required=True,
                help="The port that should be used by the current "
                     "metadata service."),
            cfg.StrOpt(
                "environment", default="production", required=True,
                help="Apply the given config environment."),
            cfg.IntOpt(
                "thread_pool", default=3, required=True,
                help="The number of thread workers used in order "
                     "to serve clients."),
        ]

    def register(self):
        """Register the current options to the global ConfigOpts object."""
        group = cfg.OptGroup(self.group_name, title='Arestor API Options')
        self._config.register_group(group)
        self._config.register_opts(self._options, group=group)

    def list(self):
        """Return a list which contains all the available options."""
        return self._options
