"""Test the pytest_gee package."""
import ee


def test_hash_fixture(hash):
    """Test the hash fixture."""
    assert isinstance(hash, str)
    assert len(hash) == 32


def test_gee_init():
    """Test the init_ee_from_token function."""
    assert ee.Number(1).getInfo() == 1
