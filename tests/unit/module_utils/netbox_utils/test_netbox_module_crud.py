# SPDX-License-Identifier: GPL-3.0-or-later
# pylint: disable=protected-access
# pylint: disable=redefined-outer-name

"""
Tests for NetboxModule CRUD operations.

This suite verifies the behavior of NetboxModule when creating,
updating, and deleting NetBox objects. It covers both normal execution
and check_mode handling to ensure actions are performed or skipped
appropriately. Diff generation and serialization logic are validated
for each operation.
"""


def test_create_netbox_object_check_mode_false(
    mock_netbox_module_ids, mock_endpoint, data_arg_spec_data, on_creation_diff
):
    """Ensure object creation is executed when check_mode is disabled."""
    return_value = mock_endpoint.create().serialize()
    serialized_obj, diff = mock_netbox_module_ids._create_netbox_object(
        mock_endpoint, data_arg_spec_data
    )
    mock_endpoint.create.assert_called_with(data_arg_spec_data)
    assert serialized_obj.serialize() == return_value
    assert diff == on_creation_diff


def test_create_netbox_object_check_mode_true(
    mock_netbox_module_ids, mock_endpoint, data_arg_spec_data, on_creation_diff
):
    """Ensure object creation is skipped when check_mode is enabled."""
    mock_netbox_module_ids.check_mode = True
    serialized_obj, diff = mock_netbox_module_ids._create_netbox_object(
        mock_endpoint, data_arg_spec_data
    )
    mock_endpoint.create.assert_not_called()
    assert serialized_obj == data_arg_spec_data
    assert diff == on_creation_diff


def test_delete_netbox_object_check_mode_false(
    mock_netbox_module_ids, mock_nb_resp, on_deletion_diff
):
    """Ensure deletion is executed when check_mode is disabled."""
    mock_netbox_module_ids.nb_object = mock_nb_resp
    diff = mock_netbox_module_ids._delete_netbox_object()
    mock_nb_resp.delete.assert_called_once()
    assert diff == on_deletion_diff


def test_delete_netbox_object_check_mode_true(
    mock_netbox_module_ids, mock_nb_resp, on_deletion_diff
):
    """Ensure deletion is skipped when check_mode is enabled."""
    mock_netbox_module_ids.check_mode = True
    mock_netbox_module_ids.nb_object = mock_nb_resp
    diff = mock_netbox_module_ids._delete_netbox_object()
    mock_nb_resp.delete.assert_not_called()
    assert diff == on_deletion_diff


def test_update_netbox_object_no_changes(mock_netbox_module_ids, mock_nb_resp):
    """Ensure update is skipped when no changes are detected."""
    mock_netbox_module_ids.nb_object = mock_nb_resp
    unchanged_data = mock_nb_resp.serialize()
    serialized_object, diff = mock_netbox_module_ids._update_netbox_object(
        unchanged_data
    )
    mock_nb_resp.update.assert_not_called()
    assert serialized_object == unchanged_data
    assert diff is None


def test_update_netbox_object_with_changes_check_mode_false(
    mock_netbox_module_ids, mock_nb_resp, changed_serialized_obj, on_update_diff
):
    """Ensure update is executed when check_mode is disabled and changes exist."""
    mock_netbox_module_ids.nb_object = mock_nb_resp
    serialized_obj, diff = mock_netbox_module_ids._update_netbox_object(
        changed_serialized_obj
    )
    mock_nb_resp.update.assert_called_once_with(changed_serialized_obj)
    assert serialized_obj == mock_nb_resp.serialize()
    assert diff == on_update_diff


def test_update_netbox_object_with_changes_check_mode_true(
    mock_netbox_module_ids, mock_nb_resp, changed_serialized_obj, on_update_diff
):
    """Ensure update is skipped when check_mode is enabled and changes exist."""
    mock_netbox_module_ids.nb_object = mock_nb_resp
    mock_netbox_module_ids.check_mode = True
    updated_serialized_obj = mock_nb_resp.serialize().copy()
    updated_serialized_obj.update(changed_serialized_obj)

    serialized_obj, diff = mock_netbox_module_ids._update_netbox_object(
        changed_serialized_obj
    )
    mock_nb_resp.update.assert_not_called()
    assert serialized_obj == updated_serialized_obj
    assert diff == on_update_diff
