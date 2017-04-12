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

"""Arestor base exception handling."""


class ArestorException(Exception):
    """Base Arestor exception

    To correctly use this class, inherit from it and define
    a `template` property.

    That `template` will be formated using the keyword arguments
    provided to the constructor.
    """

    template = "An unknown exception occurred."

    def __init__(self, message=None, **kwargs):
        message = message or self.template

        try:
            message = message % kwargs
        except (TypeError, KeyError):
            # Something went wrong during message formatting.
            # Probably kwargs doesn't match a variable in the message.
            message = ("Message: %(template)s. Extra or "
                       "missing info: %(kwargs)s" %
                       {"template": message, "kwargs": kwargs})

        super(ArestorException, self).__init__(message)


class CliError(ArestorException):

    """Something went wrong during the processing of command line."""

    template = "Something went wrong during the procesing of command line."


class ClientError(ArestorException):

    """Error while interacting with the client."""

    template = ("Failed to communicate with the Arestor API: %(msg)s.")


class Invalid(ArestorException):

    """The received object is not valid."""

    template = "Unacceptable parameters."


class NotFound(ArestorException):

    """The required object is not available in container."""

    template = "The %(object)r was not found in %(container)s."


class NotSupported(ArestorException):

    """The functionality required is not available in the current context."""

    template = "%(feature)s is not available in %(context)s."
