from typing import Any, Union
from propar import PP_TYPE_FLOAT
from propar import instrument as Instrument
from tomato.driverinterface_1_0 import Attr, ModelInterface


PROPERTY_MAP = {
    "temperature": {"proc_nr": 33, "parm_nr": 7, "parm_type": PP_TYPE_FLOAT},
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

# TODO: change map from int -> str to str -> str
UNIT_MAP = {
    "flow": {
        1: "mg/h",
        2: "g/h",
        3: "kg/h",
        4: "g/s",
        "mls/min": "ml/min",
        6: "l/min",
        7: "l/h",
        8: "mg/min",
        9: "g/min",
        10: "kg/min",
        11: "lb/h",
    },
    "pressure": {
        0: "bar",
        1: "psi",
        2: "Pa",
        3: "kPa",
        4: "torr",
        5: "atm",
        6: "mbar",
        7: "mH2O",
    },
}


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
        device_type: str
        flow_units: str = ""
        pressure_units: str = ""

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
            self.device_type = self._get_device_type()

            if self.device_type == "MFC":
                self.flow_units = self._get_flow_units()
            # elif self.device_type == "PC":
            self.pressure_units = self._get_pressure_units()
            self.max_flow_rate = self._read_property("max_flow")
            self.flow = self._read_property("flow")
            self.pressure = self._read_property("pressure")

            # ModelInterface.serial_number = self.instrument.readParameter(1, 92)
            # ModelInterface.device_number = self.read_property("device_number")
            # ModelInterface.sensor_type = self.read_property("pressure_sensor_type")
            # ModelInterface.id_number_pc = self.read_property("identification_number_press")
            # ModelInterface.firmware_version = self.read_property("firmware_version")
            # ModelInterface.serial_number = self.read_property("serial_number")
            # ModelInterface.capacity_flow = self.read_property("capacity_flow")
            # ModelInterface.temperature = self.read_property("temperature")
            # ModelInterface.fluid_name = self.read_property("fluid_name")
            # ModelInterface.fluid_unit = self.read_property("fluid_unit")

        def _get_device_type(self) -> str:
            """Determines the type of device based on its parameters."""

            # TODO : fix this lookup - (1, 72) is the serial!
            device_type = self.instrument.readParameter(1, 72)
            print(device_type.strip())
            if device_type.strip().endswith("1883A"):
                return "PC"
            else:
                return "MFC"

            if device_type == 90:
                return "MFC"
            elif device_type == 91:
                return "PC"
            else:
                raise ValueError(
                    f"Unknown device type: {device_type}. Expected 90 for MFC or 91 for PC."
                )

        def attrs(self, **kwargs) -> dict[str, Attr]:
            """
            Returns a dictionary of available attributes for the device, depending on its type (PC or MFC).

            Returns:
                dict: A dictionary of attribute names and their respective metadata.
            """
            # Initialize an empty dictionary
            attrs_dict = {}

            # If the device is of type "PC", define specific attributes for PC devices
            if self.device_type == "PC":
                attrs_dict = {
                    "pressure": Attr(
                        type=float, units=self.pressure_units, rw=False, status=True
                    ),
                    "temperature": Attr(type=float, units="Celsius", rw=False),
                    "fluid_name": Attr(type=str, rw=False),
                    # TODO: Check.
                    # "pressure_sensor_type": Attr(type=str, rw=False), # Assuming fluid_name is available for PC devices
                }

            # If the device is of type "MFC", define attributes for MFC devices
            elif self.device_type == "MFC":
                attrs_dict = {
                    "flow": Attr(
                        type=float, units=self.flow_units, rw=False, status=True
                    ),
                    "temperature": Attr(type=float, units="Celsius", rw=False),
                    "fluid_name": Attr(type=str, rw=False),
                    # TODO: Check properties below
                    "pressure": Attr(
                        type=float, units=self.pressure_units, rw=False, status=True
                    ),
                    "max_flow": Attr(type=float, units=self.flow_units, rw=False),
                    "capacity_flow": Attr(type=float, units=self.flow_units, rw=False),
                }

            # Common attributes across all device types
            # attrs_dict.update({
            #     "firmware_version": Attr(type=str, rw=False),
            #     "serial_number": Attr(type=str, rw=False),
            #     "identification_number_press": Attr(type=str, rw=False),
            #     "pressure_sensor_type": Attr(type=str, rw=False),
            # })
            return attrs_dict

        # TODO: debug setting values
        def set_attr(self, attr: str, val: Any, **kwargs: dict):
            if attr in self.attrs():
                params = PROPERTY_MAP[attr]
                if "param_id" in params:
                    self.instrument.writeParameter(params["param_id"], val)
                else:
                    self.instrument.write_parameters([{**params, "data": val}])
            else:
                raise ValueError(f"Unknown property: {attr}")

        def get_attr(self, attr: str, **kwargs: dict) -> Any:
            """Retrieves the value of an attribute from the instrument."""
            if attr in self.attrs():
                params = PROPERTY_MAP[attr]
                if "param_id" in params:
                    return self.instrument.readParameter(params["param_id"])
                else:
                    values = self.instrument.read_parameters([params])
                    return values[0]["data"]
            else:
                raise ValueError(f"Unknown property: {attr}")

        def capabilities(self, **kwargs) -> set:
            caps = {"constant_flow"}
            if self.device_type == "PC":
                caps.add("constant_pressure")
            # I positionned the return attrs_dict with caps to ensure to rest of the
            # code was reachable which was not the case before
            return caps

        def do_task(self, **kwargs):
            pass

        def _get_flow_units(self) -> Union[str | None]:
            """Retrieves the flow units for the device."""
            unit_id = self.instrument.readParameter(129)
            print(unit_id)
            if unit_id not in UNIT_MAP["flow"]:
                raise ValueError(f"Unknown flow unit ID: {unit_id}")
            return UNIT_MAP["flow"][unit_id]

        def _get_pressure_units(self) -> Union[str | None]:
            """Retrieves the pressure units for the device."""
            unit_id = self.instrument.readParameter(130)
            if unit_id not in UNIT_MAP["pressure"]:
                raise ValueError(f"Unknown pressure unit ID: {unit_id}")
            return UNIT_MAP["pressure"][unit_id]

        def _read_property(self, property: str) -> Any:
            if property in PROPERTY_MAP:
                params = PROPERTY_MAP[property]
                if "param_id" in params:
                    return self.instrument.readParameter(params["param_id"])
                else:
                    values = self.instrument.read_parameters([params])
                    return values[0]["data"]
            else:
                raise ValueError(f"Unknown property: {property}")


# here : dynamic input/output are added
if __name__ == "__main__":
    import time

    interface = DriverInterface()

    if False:
        # Get COM port input, from the df
        port = input("Enter the COM port (e.g., 'COM4'): ")

        # Get channel input
        while True:
            try:
                channel = int(input("Enter the channel number: "))
                break
            except ValueError:
                print("Invalid input. Please enter a valid integer for the channel.")
    port = "COM5"
    print(f"{interface=}")

    for channel in [80, 81, 82]:
        kwargs = dict(address=port, channel=channel)

        print(f"{interface.dev_register(**kwargs)=}")
        print(f"{interface.dev_status(**kwargs)=}")

        # Print additional attributes
        print(f"{interface.dev_get_attr(attr='temperature', **kwargs)=}")
        try:
            print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")
        except Exception as _:
            pass
        print(f"{interface.dev_get_attr(attr='pressure', **kwargs)=}")
        # print(f"{interface.dev_get_attr(attr='max_flow', **kwargs)=}")
        # print(f"{interface.dev_get_attr(attr='capacity_flow', **kwargs)=}")
        print(f"{interface.dev_get_attr(attr='fluid_name', **kwargs)=}")
        print(f"{interface.devmap[('COM5', channel)].attrs()=}")

    print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")
    print(f"{interface.dev_set_attr(attr='flow', val=30.0, **kwargs)=}")
    time.sleep(2)
    print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")


def func():
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
