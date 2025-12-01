# SPDX-License-Identifier: GPL-3.0-or-later
# pylint: disable=protected-access
# pylint: disable=redefined-outer-name

"""
Unit tests for NetboxModule version comparison and sanitization methods.
"""

import re
import pytest


@pytest.mark.parametrize("version", ["2.13", "2.12", "2.11", "2.10.8", "2.10"])
def test_version_check_greater_true(mock_netbox_module_version, version):
    """
    _version_check_greater returns True
    for versions greater than a baseline.
    """
    assert mock_netbox_module_version._version_check_greater(version, "2.9")
    assert mock_netbox_module_version._version_check_greater(version, "2.9.11")


@pytest.mark.parametrize("version", ["2.9", "2.8", "2.7.12", "2.7"])
def test_version_check_greater_false(mock_netbox_module_version, version):
    """
    _version_check_greater returns False
    for versions less than a baseline.
    """
    assert not mock_netbox_module_version._version_check_greater(version, "2.10")
    assert not mock_netbox_module_version._version_check_greater(version, "2.10.8")


@pytest.mark.parametrize("version", ["2.9", "2.8", "2.7.5", "2.7"])
def test_version_check_greater_equal_to_true(mock_netbox_module_version, version):
    """
    _version_check_greater returns True
    when greater_or_equal=True for matching or higher versions.
    """
    assert mock_netbox_module_version._version_check_greater(
        version, "2.7", greater_or_equal=True
    )
    assert mock_netbox_module_version._version_check_greater(
        version, "2.6.12", greater_or_equal=True
    )


@pytest.mark.parametrize("version", ["2.6", "2.5", "2.4"])
def test_version_check_greater_equal_to_false(mock_netbox_module_version, version):
    """
    _version_check_greater returns False
    when greater_or_equal=True for versions lower than baseline.
    """
    assert not mock_netbox_module_version._version_check_greater(
        version, "2.7", greater_or_equal=True
    )
    assert not mock_netbox_module_version._version_check_greater(
        version, "2.7.7", greater_or_equal=True
    )


@pytest.mark.parametrize(
    "raw_value,expected",
    [
        ("2.6", "2.6"),
        ("2.6.", "2.6"),
        ("4.2-dev", "4.2"),
        ("4", "4"),
        ("4-dev", "4"),
        ("4.-dev", "4"),
        ("4.2.9-Docker-3.2.1", "4.2.9"),
        ("3.1.0-extra-info", "3.1.0"),
        ("10.20.30foobar", "10.20.30"),
    ],
)
def test_version_sanitize_to_true(mock_netbox_module_version, raw_value, expected):
    """
    _version_sanitize cleans raw version strings into valid semantic version format.
    """
    sanitized = mock_netbox_module_version._version_sanitize(raw_value)
    assert sanitized == expected
    assert re.match(r"^\d+(\.\d+)*$", sanitized)


@pytest.mark.parametrize("version", [None, [], {}, "", "aa-dev", "-4", ".4", "dev-4"])
def test_version_sanitize_value_error(mock_netbox_module_version, version):
    """
    _version_sanitize raises ValueError for invalid or malformed version strings.
    """
    with pytest.raises(ValueError):
        mock_netbox_module_version._version_sanitize(version)
