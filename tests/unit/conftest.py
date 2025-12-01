# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
conftest.py – shared pytest fixtures for tests/unit tests.
Loaded automatically by pytest.
"""


def pytest_configure(config):
    """Convert all warnings into errors."""
    config.addinivalue_line("filterwarnings", "error")
