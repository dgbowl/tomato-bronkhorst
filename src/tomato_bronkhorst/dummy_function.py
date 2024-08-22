import time
import numpy as np
import xarray as xr
import argparse
import sys

class DummyBronkhorstDevice:
    def __init__(self, port):
        print(f"Initializing dummy device on port: {port}")
        self._time = 0
        self._temperature_data = []
        self._flow_rate_data = []
        self._pressure_data = []
        self._nodes = ['EL-FLOW Select', 'EL-PRESSURE', 'EL-FLOW']
        self.max_flow_rate = 10.0  # ml/min
        self.max_flow_unit = 'ml/min'

    def setup_instrument(self, port):
        print(f"Setting up instrument on port: {port}")
        return self

    def read_property(self, property: str):
        if property == 'temperature':
            return np.random.uniform(20, 25)
        elif property == 'flow_rate':
            return np.random.uniform(0, self.max_flow_rate)
        elif property == 'pressure':
            return np.random.uniform(1000, 1010)
        elif property == 'max_flow_rate':
            return self.max_flow_rate
        elif property == 'flow_unit':
            return self.max_flow_unit
        else:
            raise ValueError(f"Unknown property: {property}")

    def open_valve_fully(self):
        print("Opening valve fully...")

    def close_valve(self):
        print("Closing valve fully...")

    def collect_data(self, duration):
        temperature_data = []
        flow_rate_data = []
        pressure_data = []
        timestamps = []
        end_time = time.time() + duration
        while time.time() < end_time:
            temperature = self.read_property('temperature')
            flow_rate = self.read_property('flow_rate')
            pressure = self.read_property('pressure')

            temperature_data.append(temperature)
            flow_rate_data.append(flow_rate)
            pressure_data.append(pressure)
            timestamps.append(time.time())

            print(
                f"Time: {time.time():.2f} s, "
                f"Temperature: {temperature:.2f} °C, "
                f"Flow Rate: {flow_rate:.2f} {self.max_flow_unit}, "
                f"Pressure: {pressure:.2f} hPa"
            )

            time.sleep(1)

        self.close_valve()

        temperature_array = xr.DataArray(
            temperature_data,
            coords=[timestamps],
            dims=["time"],
            name="temperature",
            attrs={"units": "°C"}
        )

        flow_rate_array = xr.DataArray(
            flow_rate_data,
            coords=[timestamps],
            dims=["time"],
            name="flow_rate",
            attrs={"units": self.max_flow_unit}
        )
        pressure_array = xr.DataArray(
            pressure_data,
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

def list_available_devices():
    print("\nSearching for available devices...")
    available_ports = ['COM1', 'COM2', 'COM3', 'COM4']  # Dummy list of ports
    if not available_ports:
        print("No devices found.")
    else:
        print("\nAvailable Devices:")
        for i, port in enumerate(available_ports):
            print(f"{i+1}. Port: {port}")

def get_valid_port():
    while True:
        port = input("Enter the COM port (e.g., 'COM4'): ")
        if isinstance(port, str):
            return port
        else:
            print("Invalid input. Please enter a valid COM port as a string.")

def get_experiment_duration():
    while True:
        try:
            duration = int(input('Enter the duration of the experiment in seconds: '))
            return duration
        except ValueError:
            print("Invalid input. Please enter an integer value for the duration.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Bronkhorst Flow Controller Automation")
    parser.add_argument("--port", type=str, help="COM port to use (e.g., 'COM4')")
    parser.add_argument("--duration", type=int, help="Duration of the experiment in seconds")
    
    if 'ipykernel' in sys.modules:
        args, unknown = parser.parse_known_args()
    else:
        args = parser.parse_args()
    
    return args

if __name__ == "__main__":
    args = parse_arguments()

    list_available_devices()

    port = args.port if args.port else get_valid_port()
    duration = args.duration if args.duration else get_experiment_duration()

    device = DummyBronkhorstDevice(port)
    dataset = device.collect_data(duration)
    print('\nCollected data:')
    print(dataset)