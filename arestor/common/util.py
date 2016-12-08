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

"""A collection of utilities used across the project."""

from arestor.common import exception


def get_attribute(root, attribute):
    """Search for the received attribute name in the object tree.

    :param root: the root object
    :param attribute: the name of the required attribute
    """
    command_tree = [root]
    while command_tree:
        current_object = command_tree.pop()
        if hasattr(current_object, attribute):
            return getattr(current_object, attribute)

        parent = getattr(current_object, "parent", None)
        if parent:
            command_tree.append(parent)

    raise exception.ArestorException("The %(attribute)r attribute is "
                                     "missing from the object tree.",
                                     attribute=attribute)
