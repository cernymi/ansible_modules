# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: disable=protected-access
# pylint: disable=redefined-outer-name

"""
conftest.py – pytest fixtures shared by all unit tests under the module_utils/ directory.
Loaded automatically by pytest.
"""

import pytest

try:
    from ansible_collections.netbox.netbox.plugins.module_utils.netbox_dcim import (
        NB_DEVICES,
    )
    from ansible_collections.netbox.netbox.plugins.module_utils.netbox_utils import (
        NetboxModule,
    )

    MOCKER_PATCH_PATH = (
        "ansible_collections.netbox.netbox.plugins.module_utils."
        "netbox_utils.NetboxModule"
    )
except ImportError:
    from plugins.module_utils.netbox_dcim import NB_DEVICES
    from plugins.module_utils.netbox_utils import NetboxModule

    MOCKER_PATCH_PATH = "plugins.module_utils.netbox_utils.NetboxModule"


@pytest.fixture
def data_arg_spec():
    """Ansible module data with NETBOX_ARG_SPEC"""
    return {
        "netbox_url": "http://netbox.local/",
        "netbox_token": "0123456789",
        "data": {
            "name": "Test Device1",
            "device_role": "Core Switch",
            "device_type": "Cisco Switch",
            "manufacturer": "Cisco",
            "site": "Test Site",
            "asset_tag": "1001",
            "custom_fields": {
                "Key1": "Value1",
                "Key2": "Value2",
                "Key3": "Value3",
            },
        },
        "state": "present",
        "validate_certs": False,
        "cert": None,
        "headers": None,
    }


@pytest.fixture
def data_arg_spec_data():
    """
    Normalized subset of `data_arg_spec`, containing only the `data` dictionary.

    Represents the processed or canonical form of module input data
    without metadata fields like 'netbox_url', 'netbox_token', etc.
    """
    return {
        "name": "Test Device1",
        "device_role": "core-switch",
        "device_type": "cisco-switch",
        "manufacturer": "cisco",
        "site": "test-site",
        "asset_tag": "1001",
        "custom_fields": {
            "Key1": "Value1",
            "Key2": "Value2",
            "Key3": "Value3",
        },
    }


@pytest.fixture
def data_find_ids_return():
    """
    Sample return value for the `_find_ids` method in NetboxModule tests.
    """
    return {
        "name": "Test Device1",
        "role": 1,
        "device_type": 1,
        "manufacturer": 1,
        "site": 1,
        "asset_tag": "1001",
    }


@pytest.fixture
def mock_ansible_module(mocker, data_arg_spec):
    """
    Return a mocked AnsibleModule instance for testing NetboxModule.

    The mock sets `check_mode` to False and uses `data_arg_spec` as its parameters.
    Useful for injecting into NetboxModule tests without requiring a real Ansible runtime.
    """
    module = mocker.MagicMock(name="AnsibleModule")
    module.check_mode = False
    module.params = data_arg_spec

    return module


@pytest.fixture
def mock_netbox_module_ids(mocker, mock_ansible_module, data_find_ids_return):
    """
    Return a NetboxModule instance with mocked ID lookup.

    - `_find_ids` method is patched to return `data_find_ids_return`.
    - The `nb_client` is a mock simulating `pynetbox.api`.
    - The fixture allows testing NetboxModule logic without a live NetBox instance.
    """
    find_ids = mocker.patch(f"{MOCKER_PATCH_PATH}._find_ids")
    find_ids.return_value = data_find_ids_return
    nb_client = mocker.Mock(name="pynetbox.api")
    nb_client.version = "2.10"
    netbox = NetboxModule(mock_ansible_module, NB_DEVICES, nb_client=nb_client)
    return netbox


@pytest.fixture
def mock_nb_resp(mocker, data_arg_spec_data):
    """
    Return a mocked NetBox object simulating CRUD operations.

    - `delete` returns True.
    - `update` returns True, with `side_effect` set to the normalized data update.
    - `serialize` returns `data_arg_spec_data`.

    Used to test NetboxModule logic that interacts with NetBox objects.
    """
    nb_obj = mocker.Mock(name="mock_nb_resp")
    nb_obj.delete.return_value = True
    nb_obj.update.return_value = True
    nb_obj.update.side_effect = data_arg_spec_data.update
    nb_obj.serialize.return_value = data_arg_spec_data

    return nb_obj


@pytest.fixture
def mock_endpoint(mocker, mock_nb_resp):
    """
    Return a mocked NetBox endpoint object with a `create()` method.

    - `create()` returns the mocked NetBox response object (`mock_nb_resp`).
    - Used to simulate NetBox API endpoints in unit tests without real API calls.
    """
    endpoint = mocker.Mock(name="mock_endpoint")
    endpoint.create.return_value = mock_nb_resp

    return endpoint


@pytest.fixture
def changed_serialized_obj(mock_nb_resp):
    """
    Return a modified serialized representation of a mocked NetBox object.

    - Copies the output of `mock_nb_resp.serialize()`.
    - Modifies the "name" field by appending " (modified)".
    - Updates "custom_fields" with a new value.

    Used to simulate updated object data in NetboxModule tests.
    """
    changed_serialized_obj = mock_nb_resp.serialize().copy()
    changed_serialized_obj["name"] += " (modified)"
    changed_serialized_obj["custom_fields"] = {
        "Key1": "NewValue1",
    }

    return changed_serialized_obj


@pytest.fixture
def on_creation_diff(mock_netbox_module_ids):
    """
    Return the diff representing creation of a NetBox object.
    Used in tests to verify the behavior of NetboxModule when creating new objects.
    """
    return mock_netbox_module_ids._build_diff(
        before={"state": "absent"}, after={"state": "present"}
    )


@pytest.fixture
def on_deletion_diff(mock_netbox_module_ids):
    """
    Return the diff representing deletion of a NetBox object.
    Used in tests to verify the behavior of NetboxModule when removing existing objects.
    """
    return mock_netbox_module_ids._build_diff(
        before={"state": "present"}, after={"state": "absent"}
    )


@pytest.fixture
def on_update_diff(mock_netbox_module_ids):
    """
    Return the diff representing an update to a NetBox object.
    Used to verify NetboxModule behavior when updating existing objects.
    """
    return mock_netbox_module_ids._build_diff(
        before={
            "name": "Test Device1",
            "custom_fields": {
                "Key1": "Value1",
            },
        },
        after={
            "name": "Test Device1 (modified)",
            "custom_fields": {
                "Key1": "NewValue1",
            },
        },
    )
