"""Test the pytest_gee package."""
import ee


def test_hash_fixture(gee_hash):
    """Test the hash fixture."""
    assert isinstance(gee_hash, str)
    assert len(gee_hash) == 32


def test_gee_init():
    """Test the init_ee_from_token function."""
    assert ee.Number(1).getInfo() == 1
