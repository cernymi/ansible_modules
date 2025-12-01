# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Bruno Inec (@sweenu) <bruno@inec.fr>
# Copyright: (c) 2019, Mikhail Yohman (@FragmentedPacket) <mikhail.yohman@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from functools import partial
from pathlib import Path
import pytest

try:
    from ansible_collections.netbox.netbox.tests.unit.helpers.load_data import (
        load_test_data,
    )

    MOCKER_PATCH_PATH = "ansible_collections.netbox.netbox.plugins.module_utils.netbox_utils.NetboxModule"
except ImportError:
    from tests.unit.helpers.load_data import load_test_data

    MOCKER_PATCH_PATH = "plugins.netbox_utils.NetboxModule"

load_relative_test_data = partial(load_test_data, Path(__file__).resolve().parent)


def test_init(mock_netbox_module_ids, data_find_ids_return):
    """Test that we can get a real mock NetboxModule."""
    assert mock_netbox_module_ids.data == data_find_ids_return


@pytest.mark.parametrize("before, after", load_relative_test_data("normalize_data"))
def test_normalize_data_returns_correct_data(mock_netbox_module_ids, before, after):
    norm_data = mock_netbox_module_ids._normalize_data(before)

    assert norm_data == after


@pytest.mark.parametrize("data, expected", load_relative_test_data("arg_spec_default"))
def test_remove_arg_spec_defaults(mock_netbox_module_ids, data, expected):
    new_data = mock_netbox_module_ids._remove_arg_spec_default(data)

    assert new_data == expected


@pytest.mark.parametrize("non_slug, expected", load_relative_test_data("slug"))
def test_to_slug_returns_valid_slug(mock_netbox_module_ids, non_slug, expected):
    got_slug = mock_netbox_module_ids._to_slug(non_slug)

    assert got_slug == expected


@pytest.mark.parametrize("endpoint, app", load_relative_test_data("find_app"))
def test_find_app_returns_valid_app(mock_netbox_module_ids, endpoint, app):
    assert app == mock_netbox_module_ids._find_app(
        endpoint
    ), "app: %s, endpoint: %s" % (
        app,
        endpoint,
    )


@pytest.mark.parametrize(
    "endpoint, data, expected", load_relative_test_data("choices_id")
)
def test_change_choices_id(mocker, mock_netbox_module_ids, endpoint, data, expected):
    fetch_choice_value = mocker.patch(
        "%s%s" % (MOCKER_PATCH_PATH, "._fetch_choice_value")
    )
    fetch_choice_value.return_value = "temp"
    new_data = mock_netbox_module_ids._change_choices_id(endpoint, data)
    assert new_data == expected


@pytest.mark.parametrize(
    "parent, module_data, expected",
    load_relative_test_data("build_query_params_no_child"),
)
def test_build_query_params_no_child(
    mock_netbox_module_ids, mocker, parent, module_data, expected
):
    get_query_param_id = mocker.patch(
        "%s%s" % (MOCKER_PATCH_PATH, "._get_query_param_id")
    )
    get_query_param_id.return_value = 1
    query_params = mock_netbox_module_ids._build_query_params(parent, module_data)
    assert query_params == expected, query_params


@pytest.mark.parametrize(
    "parent, module_data, child, expected",
    load_relative_test_data("build_query_params_child"),
)
def test_build_query_params_child(
    mock_netbox_module_ids, mocker, parent, module_data, child, expected
):
    get_query_param_id = mocker.patch(
        "%s%s" % (MOCKER_PATCH_PATH, "._get_query_param_id")
    )
    get_query_param_id.return_value = 1
    # This will need to be updated, but attempting to fix issue quickly
    fetch_choice_value = mocker.patch(
        "%s%s" % (MOCKER_PATCH_PATH, "._fetch_choice_value")
    )
    fetch_choice_value.return_value = 200

    query_params = mock_netbox_module_ids._build_query_params(
        parent, module_data, child=child
    )
    print(query_params)
    assert query_params == expected


@pytest.mark.parametrize(
    "parent, module_data, user_query_params, expected",
    load_relative_test_data("build_query_params_user_query_params"),
)
def test_build_query_params_user_query_params(
    mock_netbox_module_ids, mocker, parent, module_data, user_query_params, expected
):
    get_query_param_id = mocker.patch(
        "%s%s" % (MOCKER_PATCH_PATH, "._get_query_param_id")
    )
    get_query_param_id.return_value = 1
    # This will need to be updated, but attempting to fix issue quickly
    fetch_choice_value = mocker.patch(
        "%s%s" % (MOCKER_PATCH_PATH, "._fetch_choice_value")
    )
    fetch_choice_value.return_value = 200

    query_params = mock_netbox_module_ids._build_query_params(
        parent, module_data, user_query_params
    )
    assert query_params == expected


def test_build_diff_returns_valid_diff(mock_netbox_module_ids):
    before = "The state before"
    after = {"A": "more", "complicated": "state"}
    diff = mock_netbox_module_ids._build_diff(before=before, after=after)

    assert diff == {"before": before, "after": after}
