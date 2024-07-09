#here we try our code on a dummy device
#first step towards a package 
#test 1 as mentionned on the e-mails
import time
import numpy as np
import xarray as xr

#this is the version using polar bronkhorst library
# A dummy serial port class with the required functions and attributes.
class dummy_serial():
    def __init__(self, port, baudrate, **kwargs):
        # Initialize the port, port and baudrate can be controlled
        # in instrument and master initialization.
        print(port, baudrate)
        self._time = 0
        self._temperature_data = []
        self._flow_rate_data = []
        self._pressure_data = []

        # Add a list of nodes for the dummy device
        # typically it is supposed to print the devices connected
        self._nodes = ['EL-FLOW Select', 'EL-PRESSURE', 'EL-FLOW']

    def close(self):
        # Close the port
        print('close')

    def open(self):
        # Open the port
        print('open')

    def read(self, size=1):
        # Read data from port, return bytes object
        return b'dummy'

    def write(self, data):
        # Write data to port, bytes object as input
        print(data)

    @property
    def in_waiting(self):
        # Return number of bytes available for reading
        return 5

    def read_temperature(self):
        # Simulate reading temperature
        temperature = np.random.uniform(20, 25)
        self._temperature_data.append(temperature)
        self._time += 1
        return temperature

    def read_flow_rate(self):
        # Simulate reading flow rate
        flow_rate = np.random.uniform(0, 10)
        self._flow_rate_data.append(flow_rate)
        return flow_rate

    def read_pressure(self):
        # Simulate reading pressure
        pressure = np.random.uniform(1000, 1010)
        self._pressure_data.append(pressure)
        return pressure
# 
    def get_collected_data(self):
        timestamps = np.arange(self._time)

        temperature_array = xr.DataArray(
            self._temperature_data,
            coords=[timestamps],
            dims=["time"],
            name="temperature",
            attrs={"units": "°C"}
        )

        flow_rate_array = xr.DataArray(
            self._flow_rate_data,
            coords=[timestamps],
            dims=["time"],
            name="flow_rate",
            attrs={"units": "ml/min"}
        )

        pressure_array = xr.DataArray(
            self._pressure_data,
            coords=[timestamps],
            dims=["time"],
            name="pressure",
            attrs={"units": "hPa"}
        )

        dataset = xr.Dataset({
            "temperature": temperature_array,
            "flow_rate": flow_rate_array,
            "pressure": pressure_array
        })

        return dataset

    def get_nodes(self):
        """Return a list of nodes for the dummy device."""
        return self._nodes

# Instrument instance with dummy serial port.
dut = dummy_serial('dummy_port', 9600)

if __name__ == "__main__":
    # Ask user for experiment duration
    print('Enter the duration of the experiment in seconds:')
    duration = int(input('Duration in s: '))

    # Display the list of nodes
    nodes = dut.get_nodes()
    for node in nodes:
        print(node)

    # Collect data
    end_time = time.time() + duration
    while time.time() < end_time:
        temperature = dut.read_temperature()
        flow_rate = dut.read_flow_rate()
        pressure = dut.read_pressure()

        print(
            f"Time: {time.time():.2f} s, "
            f"Temperature: {temperature:.2f} °C, "
            f"Flow Rate: {flow_rate:.2f} ml/min, "
            f"Pressure: {pressure:.2f} hPa"
        )

        time.sleep(1)

    # Get collected data
    collected_data = dut.get_collected_data()
    print('\nCollected data:')
    print(collected_data)
