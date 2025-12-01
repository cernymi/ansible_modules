# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=protected-access
# pylint: disable=redefined-outer-name


"""
conftest.py – pytest fixtures shared by all unit tests under the inventory/ directory.
Loaded automatically by pytest.
"""

import pytest
from packaging import version

try:
    from ansible_collections.netbox.netbox.plugins.inventory.nb_inventory import (
        InventoryModule,
    )
except ImportError:
    from plugins.inventory.nb_inventory import InventoryModule


class MockInventory:
    """
    Mock implementation of an inventory object to track host variables.

    Attributes
    ----------
    variables : dict
        Stores per-host variables in the format {hostname: {key: value}}.
    """

    def __init__(self):
        """Initialize an empty variables dictionary."""
        self.variables = {}

    def set_variable(self, hostname, key, value):
        """
        Set a variable for a given host.

        Parameters
        ----------
        hostname : str
            The hostname of the device or VM.
        key : str
            The name of the variable to set.
        value : Any
            The value to assign to the variable.
        """
        if hostname not in self.variables:
            self.variables[hostname] = {}

        self.variables[hostname][key] = value


@pytest.fixture
def inventory_fixture(
    allowed_device_query_parameters_fixture, allowed_vm_query_parameters_fixture
):
    """
    Return a fully initialized InventoryModule instance for testing.

    - Sets `api_endpoint` and `api_version`.
    - Assigns allowed device and VM query parameters from fixtures.
    - Replaces the internal inventory with `MockInventory` to track variable assignments.

    Parameters
    ----------
    allowed_device_query_parameters_fixture : list[str]
        Subset of device query parameters allowed in NetBox.
    allowed_vm_query_parameters_fixture : list[str]
        Subset of VM query parameters allowed in NetBox.

    Returns
    -------
    InventoryModule
        Configured inventory object suitable for unit tests.
    """
    inventory = InventoryModule()
    inventory.api_endpoint = "https://netbox.test.endpoint:1234"

    # Fill in data that is fetched dynamically
    inventory.api_version = version.Version("2.0")
    inventory.allowed_device_query_parameters = allowed_device_query_parameters_fixture
    inventory.allowed_vm_query_parameters = allowed_vm_query_parameters_fixture

    # Inventory mock, to validate what has been set via inventory.inventory.set_variable
    inventory.inventory = MockInventory()

    return inventory


@pytest.fixture
def allowed_device_query_parameters_fixture():
    """
    Return a subset of device query parameters for testing purposes.

    These simulate the parameters normally fetched dynamically from
    the NetBox OpenAPI endpoint.

    Returns
    -------
    list[str]
        Allowed device query parameters.
    """
    return [
        "id",
        "interfaces",
        "has_primary_ip",
        "mac_address",
        "name",
        "platform",
        "rack_id",
        "region",
        "role",
        "tag",
    ]


@pytest.fixture
def allowed_vm_query_parameters_fixture():
    """
    Return a subset of VM query parameters for testing purposes.

    These simulate the parameters normally fetched dynamically from
    the NetBox OpenAPI endpoint.

    Returns
    -------
    list[str]
        Allowed VM query parameters.
    """
    return [
        "id",
        "virtual_disks",
        "interfaces",
        "disk",
        "mac_address",
        "name",
        "platform",
        "region",
        "role",
        "tag",
    ]
