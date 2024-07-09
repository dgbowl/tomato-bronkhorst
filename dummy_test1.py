#test 1 for the dummy function (dummy_function1)
# pytest dummy_test1.py
# tested and works

import pytest
from dummy_function1 import dummy_serial

def test_read_temperature():
    dummy = dummy_serial('dummy_port', 9600)

    # Call the read_temperature method 10 times
    temperatures = [dummy.read_temperature() for _ in range(10)]

    # Check that the length of the temperature data is 10
    assert len(dummy._temperature_data) == 10

    # Check that the temperature values are within the expected range
    for temp in temperatures:
        assert 20 <= temp <= 25

def test_read_flow_rate():
    dummy = dummy_serial('dummy_port', 9600)

    # Call the read_flow_rate method 10 times
    flow_rates = [dummy.read_flow_rate() for _ in range(10)]

    # Check that the length of the flow rate data is 10
    assert len(dummy._flow_rate_data) == 10

    # Check that the flow rate values are within the expected range
    for flow in flow_rates:
        assert 0 <= flow <= 10

def test_read_pressure():
    dummy = dummy_serial('dummy_port', 9600)

    # Call the read_pressure method 10 times
    pressures = [dummy.read_pressure() for _ in range(10)]

    # Check that the length of the pressure data is 10
    assert len(dummy._pressure_data) == 10

    # Check that the pressure values are within the expected range
    for pressure in pressures:
        assert 1000 <= pressure <= 1010

def test_get_collected_data():
    # Create an instance of the dummy serial port
    dummy = dummy_serial('dummy_port', 9600)

    # Call the read methods to populate the data lists
    for _ in range(10):
        dummy.read_temperature()
        dummy.read_flow_rate()
        dummy.read_pressure()

    # Get the collected data
    collected_data = dummy.get_collected_data()

    # Check that the length of the data arrays is 10
    assert len(collected_data['temperature']) == 10
    assert len(collected_data['flow_rate']) == 10
    assert len(collected_data['pressure']) == 10


def test_get_nodes():
    dummy = dummy_serial('dummy_port', 9600)

    # Get the list of nodes
    nodes = dummy.get_nodes()

    # Check that the list of nodes is correct
    assert nodes == ['EL-FLOW Select', 'EL-PRESSURE', 'EL-FLOW']
