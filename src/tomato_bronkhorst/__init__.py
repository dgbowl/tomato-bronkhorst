from datetime import datetime
from typing import Any
from propar import instrument as Instrument
import serial
import xarray as xr
import pint
import logging
from tomato.driverinterface_2_1 import Attr, ModelInterface, ModelDevice
from tomato.driverinterface_2_1.decorators import coerce_val
from tomato.driverinterface_2_1.types import Val

logger = logging.getLogger(__name__)

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
    """Helper function that converts attributes used in tomato to Bronkhorst propar specific values."""
    if attr in {"flow", "pressure"}:
        dde_nr = PROPERTY_MAP["fmeasure"]
    elif attr in {"setpoint"}:
        dde_nr = PROPERTY_MAP["fsetpoint"]
    else:
        dde_nr = PROPERTY_MAP[attr]
    return dde_nr


class Device(ModelDevice):
    instrument: Instrument
    """:class:`propar.Instrument`, used for communication with the device"""

    device_type: str
    """stores whether device is a pressure or flow controller, using :obj:`SENSOR_MAP`"""

    device_unit: str
    """stores the unit of the setpoint and capacity of this device, using :obj:`UNIT_MAP`"""

    capacity_max: pint.Quantity
    """the minimum device capacity in :obj:`self.device_unit` units"""

    capacity_min: pint.Quantity
    """the maximum device capacity in :obj:`self.device_unit` units"""

    @property
    def fmeasure(self) -> float:
        dde_nr = dde_from_attr("fmeasure")
        return self.instrument.readParameter(dde_nr=dde_nr)

    def __init__(self, driver: ModelInterface, key: tuple[str, str], **kwargs: dict):
        address, channel = key
        try:
            self.instrument = Instrument(comport=address, address=int(channel))
        except serial.SerialException as e:
            logger.error(e, exc_info=True)
            raise RuntimeError(str(e)) from e
        try:
            self.device_type = SENSOR_MAP[self._read_property("sensor_type")]
            umap = UNIT_MAP[self._read_property("capacity_unit")]
        except KeyError as e:
            logger.error(e, exc_info=True)
            raise RuntimeError(
                f"attempting to read from interface on {address!r} resulted in a "
                "KeyError, it is likely the device at the address is not a Bronkhorst device."
            ) from e
        self.device_unit = umap["unit"]
        self.capacity_min = pint.Quantity(
            self._read_property("capacity_min"), self.device_unit
        )
        self.capacity_max = pint.Quantity(
            self._read_property("capacity_max"), self.device_unit
        )
        super().__init__(driver, key, **kwargs)

    def attrs(self, **kwargs) -> dict[str, Attr]:
        """Returns a dict of available attributes for the device, depending on its type (PC or MFC)."""
        attrs_dict = {
            "temperature": Attr(
                type=pint.Quantity,
                units="celsius",
                status=False,
            ),
            "control_mode": Attr(
                type=str, status=True, rw=True, options=set(MODE_MAP.keys())
            ),
            "setpoint": Attr(
                type=pint.Quantity,
                units=self.device_unit,
                status=True,
                rw=True,
                maximum=self.capacity_max,
                minimum=self.capacity_min,
            ),
        }
        return attrs_dict

    @coerce_val
    def set_attr(self, attr: str, val: Any, **kwargs: dict) -> Val:
        dde_nr = dde_from_attr(attr)
        if isinstance(val, pint.Quantity):
            props = self.attrs()[attr]
            self.instrument.writeParameter(dde_nr=dde_nr, data=val.to(props.units).m)
        elif attr == "control_mode":
            self.instrument.writeParameter(dde_nr=dde_nr, data=MODE_MAP[val])
        else:
            self.instrument.writeParameter(dde_nr=dde_nr, data=val)
        return val

    def get_attr(self, attr: str, **kwargs: dict) -> Val:
        if attr not in self.attrs():
            raise AttributeError(f"unknown attr: {attr!r}")
        props = self.attrs()[attr]
        dde_nr = dde_from_attr(attr)
        ret = self.instrument.readParameter(dde_nr=dde_nr)
        if attr == "control_mode":
            ret = CONTROL_MAP[ret]
        elif props.units is not None:
            ret = pint.Quantity(ret, props.units)
        return ret

    def capabilities(self, **kwargs) -> set:
        if self.device_type == "pressure":
            caps = {"constant_pressure"}
        else:
            caps = {"constant_flow"}
        return caps

    def do_measure(self, **kwargs):
        data_vars = {}
        for key, props in self.attrs(**kwargs).items():
            val = self.get_attr(attr=key)
            if props.units is not None:
                data_vars[key] = (["uts"], [val.m], {"units": props.units})
            else:
                data_vars[key] = (["uts"], [val])
        if self.device_type == "pressure":
            data_vars["pressure"] = (
                ["uts"],
                [self.fmeasure],
                {"units": self.device_unit},
            )
        else:
            data_vars["flow"] = (
                ["uts"],
                [self.fmeasure],
                {"units": self.device_unit},
            )
        self.last_data = xr.Dataset(
            data_vars=data_vars,
            coords={"uts": (["uts"], [datetime.now().timestamp()])},
        )

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

    def reset(self, **kwargs):
        super().reset(**kwargs)
        try:
            self.set_attr(attr="control_mode", val="valve close")
        except Exception as e:
            logger.warning(e, exc_info=True)


class DriverInterface(ModelInterface):
    idle_measurement_interval = 10

    def DeviceFactory(self, key, **kwargs):
        return Device(self, key, **kwargs)
