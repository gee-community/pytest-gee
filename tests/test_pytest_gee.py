"""Test the pytest_gee package."""

import pytest_gee


def test_hello_world():
    """Hello world test."""
    assert pytest_gee.Hello().hello_world() == "hello world !"
