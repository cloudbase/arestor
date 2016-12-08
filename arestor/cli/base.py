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


"""
Client base-classes:
    (Beginning of) the contract that commands and parsers must follow.
"""

import abc

from oslo_log import log as logging
import six

from arestor.common import constant
from arestor.common import exception
from arestor.common import util

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Task(object):

    """Contract class for all the commands and clients."""

    def __init__(self):
        self._name = self.__class__.__name__

    @property
    def name(self):
        """The name of the current task."""
        return self._name

    @abc.abstractmethod
    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        pass

    @abc.abstractmethod
    def _on_task_done(self, result):
        """What to execute after successfully finished processing a task."""
        pass

    @abc.abstractmethod
    def _on_task_fail(self, exc):
        """What to do when the program fails processing a task."""
        pass

    def _prologue(self):
        """Executed once before the command running."""
        pass

    @abc.abstractmethod
    def _work(self):
        """Override this with your desired procedures."""
        pass

    def _epilogue(self):
        """Executed once after the command running."""
        pass

    def run(self):
        """Run the command."""
        result = None

        try:
            self._prologue()
            result = self._work()
            self._epilogue()
        except exception.ArestorException as exc:
            self._on_task_fail(exc)
        else:
            self._on_task_done(result)

        return result


@six.add_metaclass(abc.ABCMeta)
class Command(Task):

    """Contract class for all the commands."""

    def __init__(self, parent, parser):
        super(Command, self).__init__()
        self._args = None
        self._command_line = None
        self._parent = parent
        self._parser = parser

        self.setup()

    @property
    def args(self):
        """The command line arguments parsed by the client."""
        if self._args is None:
            self._args = util.get_attribute(self.parent, "args")
        return self._args

    @property
    def command_line(self):
        """Command line provided to parser."""
        if self._command_line is None:
            self._command_line = util.get_attribute(self.parent,
                                                    "command_line")
        return self._command_line

    @property
    def parent(self):
        """Return the object that contains the current command."""
        return self._parent

    def _on_task_done(self, result):
        """What to execute after successfully finished processing a task."""
        try:
            callback = util.get_attribute(self.parent, "on_task_done")
            callback(self, result)
        except exception.ArestorException:
            LOG.debug("%(command)r: No callback found for task_done.",
                      {"command": self.name})

    def _on_task_fail(self, exc):
        """What to do when the program fails processing a task."""
        try:
            callback = util.get_attribute(self.parent, "on_task_fail")
            callback(self, exc)
        except exception.ArestorException:
            LOG.debug("%(command)r: No callback found for task_done.",
                      {"command": self.name})

    @abc.abstractmethod
    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        pass

    @abc.abstractmethod
    def _work(self):
        """Override this with your desired procedures."""
        pass


@six.add_metaclass(abc.ABCMeta)
class Group(object):

    """Contract class for all the command groups.

    :ivar: commands: A list which contains (command, parser_name) tuples.

    ::
    Example:
    ::
        class Example(Group):

            commands = [
                (ExampleOne, "main_parser"),
                (ExampleTwo, "main_parser"),
                (ExampleThree, "second_parser"),
            ]

            # ...
    """

    commands = None

    def __init__(self, parent, parser):
        super(Group, self).__init__()
        self._parent = parent
        self._parser = parser
        self._parsers = {}
        self._childs = []

        self.setup()            # Setup the current command group
        self._bind_commands()   # Bind all the received commands

    @property
    def parent(self):
        """Return the object that contains the current command group."""
        return self._parent

    @classmethod
    def check_command(cls, command):
        """Check if the received command is valid and can be
        property used.
        """
        if not issubclass(command, (Command, Group)):
            return False

        return True

    def _bind_commands(self):
        """Bind the received commands to the current command group."""
        for command, parser in self.commands or ():
            if not self.check_command(command):
                continue
            self.bind(command, parser)

    def _register_parser(self, name, parser):
        """Register a new parser in this command."""
        self._parsers[name] = parser

    def _get_parser(self, name):
        """Get an parser from the current command group."""
        try:
            return self._parsers[name]
        except KeyError:
            raise exception.Invalid("Invalid parser name %(name)s",
                                    name=name)

    def bind(self, command, parser_name):
        """Bind the received command to the current one."""
        parser = self._get_parser(parser_name)
        self._childs.append(command(self, parser))

    def on_task_done(self, task, result):
        """What to execute after successfully finished processing a task."""
        self.parent.on_task_done(task, result)

    def on_task_fail(self, task, exc):
        """What to do when the program fails processing a task."""
        self.parent.on_task_fail(task, exc)

    @abc.abstractmethod
    def setup(self):
        """Extend the parser configuration in order to expose this command."""
        pass


class Application(Group, Task):

    """Contract class for all the command line applications.

    :ivar: commands: A list which contains (command, parser_name) tuples

    ::
    Example:
    ::
        class Example(CommandGroup):

            commands = [
                (ExampleOne, "main_parser"),
                (ExampleTwo, "main_parser"),
                (ExampleThree, "second_parser"),
            ]

            # ...
    """

    def __init__(self, command_line):
        super(Application, self).__init__(parent=None, parser=None)
        self._args = None
        self._command_line = command_line
        self._status = constant.TASK_RUNNING
        self._result = None

    @property
    def args(self):
        """The arguments after the command line was parsed."""
        return self._args

    @property
    def command_line(self):
        """Command line provided to parser."""
        return self._command_line

    @property
    def status(self):
        """The current status of the command line application."""
        return self._status

    @property
    def result(self):
        """The result of the required command."""
        return self._result

    def on_task_done(self, task, result):
        """What to execute after successfully finished processing a task."""
        self._result = result
        self._status = constant.TASK_DONE
        LOG.info("Command %(command)s sucessfully run. (Result: %(result)s)",
                 {"command": task.name, "result": result})

    def on_task_fail(self, task, exc):
        """What to do when the program fails processing a task."""
        self._result = exc
        self._status = constant.TASK_FAILED
        LOG.error("Command %(command)s failed with: %(reason)s",
                  {"command": task.name, "reason": exc})

    @abc.abstractmethod
    def setup(self):
        """Extend the parser configuration in order to expose all
        the received commands.

        Exemple:
        ::
            # ...
            self._parser = argparse.ArgumentParser(
                description=description)
            self._main_parser.add_argument(
                "--example", help="just an example")
            subcommands = self._parser.add_subparsers(
                title="[sub-commands]")
            self._register_parser("subcommands", subcommands)
            # ...
        """
        pass

    def _on_task_done(self, result):
        """What to execute after successfully finished processing a task."""
        self.on_task_fail(self, result)

    def _on_task_fail(self, exc):
        """What to do when the program fails processing a task."""
        self.on_task_fail(self, exc)

    def _prologue(self):
        """Executed once before the command running."""
        super(Application, self)._prologue()
        self._args = self._parser.parse_args(self.command_line)

    def _work(self):
        """Parse the command line."""
        if not self.args:
            LOG.error("No command line arguments was provided.")
            return

        work_function = getattr(self.args, "work", None)
        if not work_function:
            LOG.error("No handle was provided for the required action.")
            return

        work_function()
