import datetime
from typing import Any
from propar import instrument as Instrument
from tomato.driverinterface_1_0 import Attr, ModelInterface


# Maps from
# Operational instructions for digital Multibus Mass Flow / Pressure instruments
# Doc. no.: 9.17.023AR Date: 03-05-2022
# DDE Numbers only
PROPERTY_MAP = {
    # Parameters
    "fmeasure": 205,
    "fsetpoint": 206,
    "temperature": 142,
    "control_mode": 12,
    # Constants
    "serial_number": 92,
    "sensor_type": 22,
    "capacity_min": 183,
    "capacity_max": 21,
    "capacity_unit": 129,
}

SENSOR_MAP = {
    0: "pressure",
    1: "liquid volume",
    2: "mass",
    3: "gas volume",
    4: "other",
}

UNIT_MAP = {
    "mls/min": {"unit": "ml/min", "Tref": "20 degC", "pref": "1 atm"},
    "mln/min": {"unit": "ml/min", "Tref": "0 degC", "pref": "1 atm"},
    "ls/min ": {"unit": "l/min", "Tref": "20 degC", "pref": "1 atm"},
    "ln/min ": {"unit": "l/min", "Tref": "0 degC", "pref": "1 atm"},
    "bar(a) ": {"unit": "bar", "Tref": "20 degC", "pref": "0 atm"},
    "bar(g) ": {"unit": "bar", "Tref": "20 degC", "pref": "1 atm"},
}

CONTROL_MAP = {
    0: "bus/RS232",
    1: "analog input",
    2: "FLOW-BUS slave",
    3: "valve close",
    4: "controller idle",
    5: "testing mode",
    6: "tuning mode",
    7: "setpoint 100%",
    8: "valve fully open",
    9: "calibration mode",
    10: "analog slave",
    12: "setpoint 0%",
    13: "FLOW-BUS analog slave",
    18: "RS232",
    20: "valve steering",
    21: "analog valve steering",
    22: "valve safe state",
}

MODE_MAP = {v: k for k, v in CONTROL_MAP.items()}


def dde_from_attr(attr: str) -> int:
    """Helper function that converts attributes used in tomato to Broknhorst propar specific values."""
    if attr in {"flow", "pressure"}:
        dde_nr = PROPERTY_MAP["fmeasure"]
    elif attr in {"setpoint"}:
        dde_nr = PROPERTY_MAP["fsetpoint"]
    else:
        dde_nr = PROPERTY_MAP[attr]
    return dde_nr


class DriverInterface(ModelInterface):
    class DeviceManager(ModelInterface.DeviceManager):
        instrument: Instrument
        """propar.Instrument, used for communication with the device"""

        device_type: str
        """stores whether device is a pressure or flow controller, using SENSOR_MAP"""

        device_unit: str
        """stores the unit of the setpoint and capacity of thi sevice, using UNIT_MAP"""

        capacity_max: float
        """the minimum device capacity in self.device_unit units"""

        capacity_min: float
        """the maximum device capacity in self.device_unit units"""

        def __init__(
            self, driver: ModelInterface, key: tuple[str, int], **kwargs: dict
        ):
            super().__init__(driver, key, **kwargs)
            address, channel = key
            self.instrument = Instrument(comport=address, address=channel)
            self.device_type = SENSOR_MAP[self._read_property("sensor_type")]
            umap = UNIT_MAP[self._read_property("capacity_unit")]
            self.device_unit = umap["unit"]
            self.capacity_min = self._read_property("capacity_min")
            self.capacity_max = self._read_property("capacity_max")

        def attrs(self, **kwargs) -> dict[str, Attr]:
            """Returns a dict of available attributes for the device, depending on its type (PC or MFC)."""
            attrs_dict = {
                "temperature": Attr(type=float, units="Celsius"),
                "control_mode": Attr(type=str, status=True, rw=True),
                "setpoint": Attr(
                    type=float, units=self.device_unit, status=True, rw=True
                ),
            }
            if self.device_type == "pressure":
                attrs_dict["pressure"] = Attr(
                    type=float, units=self.device_unit, status=True
                )
            elif self.device_type in {"gas volume", "liquid volume"}:
                attrs_dict["flow"] = Attr(
                    type=float, units=self.device_unit, status=True
                )
            return attrs_dict

        def set_attr(self, attr: str, val: Any, **kwargs: dict):
            """
            Sets an attribute of the instrument to the provided value.

            Checks whether the attribute is in allowed read-write attrs.

            TODO: Range checks for setpoint before running writeParameter()
            """
            if attr in self.attrs() and self.attrs()[attr].rw:
                dde_nr = dde_from_attr(attr)
                if attr == "control_mode":
                    val = MODE_MAP[val]
                self.instrument.writeParameter(dde_nr=dde_nr, data=val)
            else:
                raise ValueError(f"Unknown attr: {attr!r}")

        def get_attr(self, attr: str, **kwargs: dict) -> Any:
            """
            Retrieves the value of an attribute from the instrument.

            Checks whether the attribute is in allowed attrs. Converts return values to
            expected types using maps.

            """
            if attr in self.attrs():
                dde_nr = dde_from_attr(attr)
                ret = self.instrument.readParameter(dde_nr=dde_nr)
                if attr == "control_mode":
                    ret = CONTROL_MAP[ret]
                return ret
            else:
                raise ValueError(f"Unknown attr: {attr!r}")

        def capabilities(self, **kwargs) -> set:
            """Returns a set of capabilities supported by this device."""
            if self.device_type == "pressure":
                caps = {"constant_pressure"}
            else:
                caps = {"constant_flow"}
            return caps

        def do_task(self, **kwargs):
            """
            Iterate over all attrs and get their values.

            TODO: The read can be batched.
            """
            uts = datetime.now().timestamp()
            self.data["uts"].append(uts)
            for key in self.attrs(**kwargs):
                val = self.get_attr(attr=key)
                self.data[key].append(val)

        def _read_property(self, property: str) -> Any:
            """
            Helper function for reading raw device properties.

            This function is using PROPERTY_MAP directly instead of going via self.attrs(),
            as is done in self.get_attr().
            """
            if property in PROPERTY_MAP:
                dde_nr = dde_from_attr(property)
                return self.instrument.readParameter(dde_nr=dde_nr)
            else:
                raise ValueError(f"Unknown property: {property!r}")


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
        device = interface.devmap[(port, channel)]

        print(f"{device.device_type=}")
        print(f"{device.device_unit=}")
        print(f"{device.capacity_min=}")
        print(f"{device.capacity_max=}")
        attr = "pressure" if device.device_type == "pressure" else "flow"
        print(f"{interface.dev_get_attr(attr=attr, **kwargs)=}")
        print(f"{interface.dev_set_attr(attr="control_mode", val=3, **kwargs)=}")
        time.sleep(2)
        print(f"{interface.dev_get_attr(attr=attr, **kwargs)=}")
        continue

        # Print additional attributes
        # print(f"{interface.dev_get_attr(attr='temperature', **kwargs)=}")
        # try:
        #    print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")
        # except Exception as _:
        #   pass
        print(f"{interface.dev_get_attr(attr='pressure', **kwargs)=}")

        # CHECK TOO
        #        print(f"{interface.dev_get_attr(attr='capacity_flow', **kwargs)=}")
        print(f"{interface.dev_get_attr(attr='fluid_name', **kwargs)=}")
        print(f"{interface.devmap[('COM5', channel)].attrs()=}")

        # print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")
        # print(f"{interface.dev_set_attr(attr='flow', val=30.0, **kwargs)=}")
        time.sleep(2)
        # print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")


def func():
    # Accessing the properties directly
    print(f"Device serial number: {interface.serial_number}")
    print(f"Firmware version: {interface.firmware_version}")
    print(f"fmeasure : {interface.fmeasure}")
    print(f"fsetpoint : {interface.fsetpoint}")
    print(f"mass_flow : {interface.mass_flow}")
    print(f"fluid_properties : {interface.fluid_properties}")
    print(f"fluid_temp : {interface.fluid_temp} ")
    print(f"standard_flow : {interface.standard_flow}")

    print(f"pressure_units : {interface.pressure_units}")
    print(f"standard_flow : {interface.standard_flow}")
    print(f"setpoint_slope_step : {interface.setpoint_slope_step}")
    print(f"valve_max_capcity : {interface.valve_max_capacity}")
    print(f"valve_open : {interface.valve_open}")

    print(f"Device number: {interface.device_number}")
    print(f"Sensor type: {interface.sensor_type}")
    print(f"ID number (PC): {interface.id_number_pc}")
    print(f"Capacity flow: {interface.capacity_flow}")
    print(f"Fluid name: {interface.fluid_name}")
    print(f"Fluid unit: {interface.fluid_unit}")
    print(f"Fluid unit: {interface.fluid_unit}")
