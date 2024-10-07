from typing import Any

from propar import PP_TYPE_FLOAT
from propar import instrument as Instrument
from tomato.driverinterface_1_0 import Attr, ModelInterface, Task


# you mentionned that the property map should be outside, check
# but also that the parameters were hard coded, for more I think you asked to handle this :
# here is a proposition for more flexibility :
class PropertyMap:
    """
    Class to manage the mapping of device properties to their corresponding IDs.
    """
#hard coded vs constants
    def __init__(self):
        self.proc_nr_temperature = 33
        self.param_id_temperature = 7
        self.param_id_flow = 205
        self.param_id_fluid_name = 25
        self.param_id_fluid_unit = 129
        self.param_id_pressure = 205
        self.param_id_max_flow = 128
        self.param_id_flow_unit = 129
        self.param_id_device_number = 90
        self.param_id_firmware_version = 105
        self.param_id_serial_number = 92
        self.param_id_capacity_flow = 21
        self.param_id_identification_number_press = 175
        self.param_id_pressure_sensor_type = 22
        # Define the property map as an instance variable
        self.property_map = {
            "temperature": {"proc_nr": 33, "parm_nr": 7},
            "flow": {"param_id": 205},
            "fluid_name": {"param_id": 25},
            "fluid_unit": {"param_id": 129},
            "pressure": {"param_id": 205},
            "max_flow": {"param_id": 128},
            "flow_unit": {"param_id": 129},
            "device_number": {"param_id": 90},
            "firmware_version": {"param_id": 105},
            "serial_number": {"param_id": 92},
            "capacity_flow": {"param_id": 21},
            "identification_number_press": {"param_id": 175},
            "pressure_sensor_type": {"param_id": 22},
        }


    def _get_property(self, property_name):
        """
        Retrieves the property details for a given property name.
        Args:
            property_name (str): The name of the property to retrieve.
        Raises:
            ValueError: If the property does not exist in the property_map.
        Returns:
        dict: The details of the property (proc_nr, param_id, etc.).
        """
        # trunk-ignore(ruff/F821)
        # trunk-ignore(ruff/F821)
        property_details = self.property_map.get(property_name, None)
        if property_details is None:
            raise ValueError(f"Property '{property_name}' does not exist in the property map.")

        return property_details  # Return the property details if found


#the goal here was to
#Purpose: This method is used to add a new property (or update an existing one) in the property_map.
#takes two arguments: the property_name and the property_details
# but is it useful ?
#
    #def _add_property(self, property_name, property_details):
     #   """
      #  Adds a new property to the map.
       # Args:
        #    property_name (str): The name of the property.
         #   property_details (dict): The details of the property (proc_nr, param_id, etc.).
        #"""
        #self.property_map[property_name] = property_details


class DriverInterface(ModelInterface):
    """Interface for managing device interactions.
    This class provides a framework for interfacing with devices, including
    managing device types and retrieving flow and pressure units."""

    class DeviceManager(ModelInterface.DeviceManager):
        """Manager for handling device-specific operations.

        This class initializes the device manager with the given driver and
        key, and retrieves device information such as type, flow units, and
        pressure units.
        """

        instrument: Instrument

        def __init__(
            self, driver: ModelInterface, key: tuple[str, int], **kwargs: dict
        ):
            """Initializes the DeviceManager with the specified driver and key.

            Args:
            driver (ModelInterface): The driver interface for the device.
            key (tuple[str, int]): A tuple containing the address and channel.
            **kwargs (dict): Additional keyword arguments for initialization.
            """
            super().__init__(driver, key, **kwargs)
            address, channel = key
            self.instrument = Instrument(comport=address, address=channel)
            self.device_type = self.determine_device_type()
            self.serial_number = self.instrument.readParameter(1, 92)
            self.flow_units = self.get_flow_units()
            self.pressure_units = self.get_pressure_units()
            self.max_flow_rate = self.read_property("max_flow")
            self.max_flow_unit = self.read_property("flow_unit")
            self.device_number = self.read_property("device_number")
            self.sensor_type = self.read_property("pressure_sensor_type")
            self.id_number_pc = self.read_property("identification_number_press")
            self.firmware_version = self.read_property("firmware_version")
            self.serial_number = self.read_property("serial_number")
            self.capacity_flow = self.read_property("capacity_flow")
            self.temperature = self.read_property("temperature")
            self.flow = self.read_property("flow")
            self.fluid_name = self.read_property("fluid_name")
            self.fluid_unit = self.read_property("fluid_unit")
            self.pressure = self.read_property("pressure")


    # MFC or PC if is unexpected behavior : error
        def _determine_device_type(self):
            """Determines the type of device based on its parameters.
            Returns:
            str: The type of the device, which can be "MFC" or "PC".
            Raises:
            ValueError: If the device type is neither MFC nor PC.
            """
            device_type = self.instrument.readParameter(1, 72)
            if device_type == 90:
                return "MFC"
            elif device_type == 91:
                return "PC"
            else:
                raise ValueError(f"Unknown device type: {device_type}. Expected 90 for MFC or 91 for PC.")



    def _get_flow_units(self):
        """Retrieves the flow units for the device, checked with pint.

        Returns:
            str: The flow unit as a string.

        Raises:
            ValueError: If the flow unit ID is unknown.
        """
        flow_unit_id = self.instrument.readParameter(129)
        unit_map = {
            1: "mg/h",
            2: "g/h",
            3: "kg/h",
            4: "g/s",
            5: "ml/min",
            6: "l/min",
            7: "l/h",
            8: "mg/min",
            9: "g/min",
            10: "kg/min",
            11: "lb/h",
        }

        if flow_unit_id not in unit_map:
            raise ValueError(f"Unknown flow unit ID: {flow_unit_id}")

        return unit_map[flow_unit_id]
        # cntp to check

    def _get_pressure_units(self):
        """Retrieves the pressure units for the device, checked with pint.
        Returns:
        str: The pressure unit as a string.
        Raises:
                ValueError: If the pressure unit ID is unknown.
        """
        pressure_unit_id = self.instrument.readParameter(130)
        unit_map = {
            0: "bar",
            1: "psi",
            2: "Pa",
            3: "kPa",
            4: "torr",
            5: "atm",
            6: "mbar",
            7: "mH2O",
        }

        if pressure_unit_id not in unit_map:
            raise ValueError(f"Unknown pressure unit ID: {pressure_unit_id}")

        return unit_map[pressure_unit_id]

        def _do_task(self, task: Task, **kwargs):
            pass

        def _list_available_devices(self):
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
                    pass  # used for testing in case we do not have access to the lab

            if not available_ports:
                print("No devices found.")
            else:
                print("\nAvailable Devices:")
                for i, (port, nodes) in enumerate(available_ports):
                    for j, node in enumerate(nodes):
                        print(f"{i+1}.{j+1}. Port: {port}, Node: {node}")

    def _connect_device(self, port):
        self.instrument = self.setup_instrument(port)
        self.nodes = self.instrument.master.get_nodes()
        if not self.nodes:
            print("No devices found on the network.")
        else:
            print("\nAvailable Devices:")
            for i, node in enumerate(self.nodes):
                print(f"{i+1}. {node}")

    # all of this must be in the subclass -- , so indentation + self
    def _get_valid_port(self):
        while True:
            port = input("Enter the COM port (e.g., 'COM4'): ")
            if isinstance(port, str):
                return port
            else:
                print("Invalid input. Please enter a valid COM port as a string.")

        def _get_experiment_duration(self):
            while True:
                try:
                    duration = int(
                        input("Enter the duration of the experiment in seconds: ")
                    )
                    return duration
                except ValueError:
                    print(
                        "Invalid input. Please enter an integer value for the duration."
                    )

    # as mentionned we can continue to use on th setpoint or the dde number
    def _open_valve_fully(self):
        print("Opening valve fully...")
        self.instrument.setpoint = 100.0

    def _close_valve(self):
        print("Closing valve fully...")
        self.instrument.setpoint = 0.0

    def _collect_data(self, duration):
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

        def _set_attr(self, attr: str, val: Any, **kwargs: dict):
            if attr in property_map:
                params = self.property_map_instance._get_property(attr)
                if "param_id" in params:
                    self.instrument.writeParameter(params["param_id"], val)
                else:
                    self.instrument.write_parameters([{**params, "data": val}])
            else:
                raise ValueError(f"Unknown property: {attr}")

        def _get_attr(self, attr: str, **kwargs: dict):
            """
            Retrieves the value of an attribute from the instrument.

            Args:
                attr (str): The name of the attribute to retrieve.

            Returns:
                The value of the requested attribute.
            """

        property_details = self.property_map_instance._get_property(attr)
        if property_details:
            if "param_id" in property_details:
                return self.instrument.readParameter(property_details["param_id"])
            else:
                values = self.instrument.read_parameters([property_details])
                return values[0]["data"]
        else:
            raise ValueError(f"Unknown property: {attr}")

        def _attrs(self, **kwargs) -> dict[str, Attr]:
            """
            Returns a dictionary of available attributes for the device.

            Returns:
                dict: A dictionary of attribute names and their respective metadata.
            """
            attrs_dict = {
                "temperature": Attr(type=float, units="Celsius"),
                # as mentionned now, the user can not modify the data, only read them.
                "flow": Attr(type=float, units=self.flow_units, rw=False, status=True),
                "pressure": Attr(type=float, units=self.pressure_unit_id, rw=False),
            }
            if self.device_type == "PC":
                attrs_dict["pressure"] = Attr(
                    type=float, units=self.pressure_units, rw=False
                )
            return attrs_dict

        def _capabilities(self, **kwargs) -> set:
            caps = {"constant_flow"}
            if self.device_type == "PC":
                caps.add("constant_pressure")
            return caps


if __name__ == "__main__":
    interface = DriverInterface()

    # Get COM port input, from the df
    port = input("Enter the COM port (e.g., 'COM4'): ")

    # Get channel input
    while True:
        try:
            channel = int(input("Enter the channel number: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer for the channel.")

    kwargs = dict(address=port, channel=channel)

    try:
        print(f"{interface=}")
        print(f"{interface.dev_register(**kwargs)=}")
        print(f"{interface.devmap=}")

        # Print additional attributes
        print(f"{interface.dev_get_attr(attr='temperature', **kwargs)=}")
        print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")
        print(f"{interface.dev_get_attr(attr='pressure', **kwargs)=}")
        print(f"{interface.dev_status(**kwargs)=}")

        # Accessing the properties directly
        print(f"Device serial number: {interface.serial_number}")
        print(f"Firmware version: {interface.firmware_version}")
        print(f"Max flow rate: {interface.max_flow_rate}")
        print(f"Max flow unit: {interface.max_flow_unit}")
        print(f"Device number: {interface.device_number}")
        print(f"Sensor type: {interface.sensor_type}")
        print(f"ID number (PC): {interface.id_number_pc}")
        print(f"Capacity flow: {interface.capacity_flow}")
        print(f"Fluid name: {interface.fluid_name}")
        print(f"Fluid unit: {interface.fluid_unit}")

    except Exception as e:
        print(f" An error occurred : {e}")