import propar
import time
import xarray as xr
import argparse
import sys


def list_available_devices():
    print("\nSearching for available devices...")
    available_ports = []
    for i in range(256):  # I doubt we will need as much
        port = f"COM{i}"
        try:
            instrument = propar.instrument(port)
            nodes = instrument.master.get_nodes()
            if nodes:
                available_ports.append((port, nodes))
        except Exception:
            pass  # used for testing because we do not have access to the lab

    if not available_ports:
        print("No devices found.")
    else:
        print("\nAvailable Devices:")
        for i, (port, nodes) in enumerate(available_ports):
            for j, node in enumerate(nodes):
                print(f"{i+1}.{j+1}. Port: {port}, Node: {node}")


class BronkhorstDevice:
    def setup_instrument(self, port):
        try:
            return propar.instrument(port)
        except ValueError:
            print(f"Invalid port: {port}. Please enter a valid COM port.")
            raise

    def read_property(self, property: str):
        # as you asked
        property_map = {
            "temperature": {
                "proc_nr": 33,
                "parm_nr": 7,
                "parm_type": propar.PP_TYPE_FLOAT,
            },
            "flow_rate": {"param_id": 205},
            "pressure": {"proc_nr": 33, "parm_nr": 5},
            "max_flow_rate": {"param_id": 128},
            "flow_unit": {"param_id": 129},
        }

        if property in property_map:
            params = property_map[property]
            if "param_id" in params:
                return self.instrument.readParameter(params["param_id"])
            else:
                values = self.instrument.read_parameters([params])
                return values[0]["data"]
        else:
            raise ValueError(f"Unknown property: {property}")

    def open_valve_fully(self):
        print("Opening valve fully...")
        self.instrument.setpoint = 100.0

    def close_valve(self):
        print("Closing valve fully...")
        self.instrument.setpoint = 0.0

    def __init__(self, port):
        self.instrument = self.setup_instrument(port)
        self.nodes = self.instrument.master.get_nodes()
        if not self.nodes:
            print("No devices found on the network.")
        else:
            print("\nAvailable Devices:")
            for i, node in enumerate(self.nodes):
                print(f"{i+1}. {node}")

        # Get additional parameters
        self.max_flow_rate = self.read_property("max_flow_rate")
        self.max_flow_unit = self.read_property("flow_unit")

        # Open the valve fully after connection
        self.open_valve_fully()

    # we collect the data in a python list that we convert in a xarray it is supposed to be more efficient...
    # to be tested
    def collect_data(self, duration):
        temperature_data = []
        flow_rate_data = []
        pressure_data = []
        timestamps = []
        end_time = time.time() + duration
        while time.time() < end_time:
            temperature = self.read_property("temperature")
            flow_rate = self.read_property("flow_rate")
            pressure = self.read_property("pressure")

            temperature_data.append(temperature)
            flow_rate_data.append(flow_rate)
            pressure_data.append(pressure)
            timestamps.append(time.time())

            print(
                f"Time: {time.time():.2f} s, "
                f"Temperature: {temperature:.2f} °C, "
                f"Flow Rate: {flow_rate:.2f} {self.max_flow_unit or 'Unknown'}, "
                f"Pressure: {pressure:.2f} bar"
            )

            time.sleep(1)

        self.close_valve()

        temperature_array = xr.DataArray(
            temperature_data,
            coords=[timestamps],
            dims=["time"],
            name="temperature",
            attrs={"units": "°C"},
        )

        flow_rate_array = xr.DataArray(
            flow_rate_data,
            coords=[timestamps],
            dims=["time"],
            name="flow_rate",
            attrs={"units": self.max_flow_unit},
        )
        pressure_array = xr.DataArray(
            pressure_data,
            coords=[timestamps],
            dims=["time"],
            name="pressure",
            attrs={"units": "bar"},
        )

        dataset = xr.Dataset(
            {
                "temperature": temperature_array,
                "flow_rate": flow_rate_array,
                "pressure": pressure_array,
            }
        )

        return dataset


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
            duration = int(input("Enter the duration of the experiment in seconds: "))
            return duration
        except ValueError:
            print("Invalid input. Please enter an integer value for the duration.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Bronkhorst Flow Controller Automation"
    )
    parser.add_argument("--port", type=str, help="COM port to use (e.g., 'COM4')")
    parser.add_argument(
        "--duration", type=int, help="Duration of the experiment in seconds"
    )

    # Check if we're in a Jupyter environment
    if "ipykernel" in sys.modules:
        # If in Jupyter, parse known args and ignore the rest
        args, unknown = parser.parse_known_args()
    else:
        # If not in Jupyter, parse args as usual
        args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_arguments()

    # List available devices before asking for port
    list_available_devices()

    # Use command-line arguments if provided, otherwise prompt user
    port = args.port if args.port else get_valid_port()
    duration = args.duration if args.duration else get_experiment_duration()

    device = BronkhorstDevice(port)
    dataset = device.collect_data(duration)
    print("\nCollected data:")
    print(dataset)
