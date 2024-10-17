# test related to the dummy version (second function)
# the test function has to be in the same folder as the dummy
# pytest -vv dummy_test2.py to launch the test
# sends a warning.... something that we could work on ?
import pytest
import xarray as xr
import numpy as np
from dummy_function import DummyBronkhorstDevice


@pytest.fixture
def device():
    """Fixture to create a DummyBronkhorstDevice instance."""
    # Set a fixed random seed for predictable data in tests
    np.random.seed(42)
    return DummyBronkhorstDevice("COM4")


def test_read_property(device):
    """Test the read_property method for various properties."""
    # Test valid properties
    assert 20 <= device.read_property("temperature") <= 25
    assert 0 <= device.read_property("flow_rate") <= device.max_flow_rate
    assert 1000 <= device.read_property("pressure") <= 1010
    assert device.read_property("max_flow_rate") == 10.0
    assert device.read_property("flow_unit") == "ml/min"

    # Test invalid property
    with pytest.raises(ValueError):
        device.read_property("invalid_property")


def test_collect_data(device, duration=5):
    """Test the collect_data method."""
    dataset = device.collect_data(duration)

    # Check dataset structure and types
    assert isinstance(dataset, xr.Dataset)
    assert all(var in dataset for var in ["temperature", "flow_rate", "pressure"])
    assert dataset["temperature"].dtype == float
    assert dataset["flow_rate"].dtype == float
    assert dataset["pressure"].dtype == float

    # Check data dimensions and units
    assert dataset.dims == {"time": duration}
    assert dataset["temperature"].attrs["units"] == "°C"
    assert dataset["flow_rate"].attrs["units"] == "ml/min"
    assert dataset["pressure"].attrs["units"] == "hPa"

    # Check data values (ensure they're within expected ranges)
    assert all(20 <= temp <= 25 for temp in dataset["temperature"].values)
    assert all(
        0 <= flow <= device.max_flow_rate for flow in dataset["flow_rate"].values
    )
    assert all(1000 <= press <= 1010 for press in dataset["pressure"].values)


def test_valve_actions(device):
    """Test valve open and close actions (currently just print statements)."""
    device.open_valve_fully()
    device.close_valve()
