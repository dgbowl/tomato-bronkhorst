from typing import Any, Union
from propar import PP_TYPE_FLOAT
from propar import instrument as Instrument
from tomato.driverinterface_1_0 import Attr, ModelInterface



PROPERTY_MAP = {

    #what you asked in the e-mail :
    # TASK 16/10/2024 :
    #on the manual we only get the dde number of fmeasure and setpoint but using the database
    #we got all the other informations



    "fmeasure" : {"dde_nr" : 205 ,"proc_nr": 33, "parm_nr": 0, "param_id": 65}, #to test in priority
    "fsetpoint" : {"dde_nr" : 206 ,"proc_nr": 33, "parm_nr": 3, "param_id": 65},#test in priority too !


    #additional elements present in the section 4 :
    #"setpoint_monitor_mode" : {"dde_nr" : 329 ,"proc_nr": 115, "parm_nr": 23, "param_id": 0},
    #"setpoint_exponential_smoothing_filter " : {"dde_nr" : 73 ,"proc_nr": 117, "parm_nr": 3, "param_id": 65},
    #"analog_setpoint_zero_scale" : {"dde_nr" : 112 ,"proc_nr": 1, "parm_nr": 29, "param_id": 33},
    #"analog_setpoint_full_scale" : {"dde_nr" : 113 ,"proc_nr": 1, "parm_nr": 30, "param_id": 32},
    #"setpoint_minimum" : {"dde_nr" : 339 ,"proc_nr": 114, "parm_nr": 14, "param_id": 65},
    #"control_mode" : {"dde_nr" : 12 ,"proc_nr": 1, "parm_nr": 4, "param_id": 0},
    #"valve_output" : {"dde_nr" : 55 ,"proc_nr": 114, "parm_nr": 1, "param_id": 64},




    #TEMPERATURE ATTRIBUTES : (added to the def __init__ , now is it where it belongs ?)
    "temperature": {"proc_nr": 33, "parm_nr": 7, "param_id": 65},#checked with mfc on the database
    "mass_flow" : {"dde_nr": 198, 'proc_nr': 33, 'parm_nr': 4, 'param_id' : 65},

    #"sensor_calibration_temp" : {"dde_nr" : 300 ,"proc_nr": 116, "parm_nr": 65, "param_id": 65}, #checked with db
    #"capacity_unit_type_temp" : {"dde_nr" : 245,"proc_nr": 33, "parm_nr": 10, "param_id": 65},


    #FLUID ATTRIBUTES :
    #"flow": {"param_id": 205}, #manuel
    "standard_flow": {'dde_nr': 253, 'proc_nr': 113, 'parm_nr': 22, 'param_id': 65},
    "fluid_name": {"dde_nr" : 25,"proc_nr": 1, "parm_nr": 17, "param_id": 96}, #database
    "fluid_temp": {"dde_nr" : 181,"proc_nr": 113, "parm_nr": 16, "param_id": 65}, #database
    "fluid_properties": {"dde_nr" : 238,"proc_nr": 33, "parm_nr": 31, "param_id": 0}, #database



    #"max_flow": {"param_id": 128}, #not found in the database..
    #"fluid_unit": {"param_id": 129}, #not found in the database ...

    #PRESSURE ATTRIBUTES :
    #"pressure": {"param_id": 205}, #manual, not found on the database,
    #"capacity_unique_type_press" : {"dde_nr": 246,"proc_nr": 33, "parm_nr": 11, "param_id": 65},
    "pressure" : {"dde_nr": 143,"proc_nr": 33, "parm_nr": 8, "param_id": 65}, #database
    "pressure_inlet" : {"dde_nr": 178,"proc_nr": 113, "parm_nr": 13, "param_id": 65}, #database
    "pressure_outlet" : {"dde_nr": 179,"proc_nr": 113, "parm_nr": 14, "param_id": 65}, #database


    #DEVICE ATTRIBUTES
    "device_number": {"param_id": 90}, #on the manual, worked
    "serial_number": {"dde_nr" : 92 ,"proc_nr": 113, "parm_nr": 3, "param_id": 96}, #database
    "device_type" : {"dde_nr" : 90 ,"proc_nr": 113, "parm_nr": 1, "param_id": 96}, # on the database
    "device_function" : {"dde_nr" : 185 ,"proc_nr": 20, "parm_nr": 20, "param_id": 0}, #on the database
    "firmware_version": {"dde_nr" : 105,"proc_nr": 113, "parm_nr": 5, "param_id": 96}, #database
    "firmware_id": {"dde_nr" : 337,"proc_nr": 0, "parm_nr": 8, "param_id": 0}, #database

    #SETPOINT AND MEASUREMENTS:
    "setpoint_slope" : {"dde_nr" : 10 ,"proc_nr": 1, "parm_nr": 2, "param_id": 32},
    "setpoint_slope_step" : {"dde_nr" : 223 ,"proc_nr": 33, "parm_nr": 24, "param_id": 32},
    "valve_max_capacity" : {"dde_nr" : 358 ,"proc_nr": 126, "parm_nr": 16, "param_id": 65},
    "valve_open" : {'dde_nr': 190, 'proc_nr': 114, 'parm_nr': 24, 'param_id': 65}





    #"max_allowed_dosing_time" : {"dde_nr" : 359 ,"proc_nr": 104, "parm_nr": 15, "param_id" : 65},
    #"max_number_runs" : {"dde_nr" : 286 ,"proc_nr": 121, "parm_nr": 4, "param_id": 32},
    #"sensor_restriction_max_capacity": {"dde_nr" : 356 ,"proc_nr": 126, "parm_nr": 14, "param_id": 65},
    #"dosing_unit": {"dde_nr" : 410 ,"proc_nr": 112, "parm_nr": 0, "param_id": 96},
    #"capacity_unit_type" : {"dde_nr" : 244,"proc_nr": 1, "parm_nr": 30, "param_id": 96},
    #"measurement_stop_criteria" : {"dde_nr" : 284,"proc_nr": 121, "parm_nr": 2, "param_id": 32},
    #"pressure_sensor_type" : {"dde_nr" : 106 ,"proc_nr": 115, "parm_nr": 9, "param_id": 0},
            }



# TODO: change map from int -> str to str -> str
#not check :
# I do not understand why but I do not have the same flexibility with the "pressure" of the UNIT_MAP
# on the 12/16 I will try to find a way to transform the pressure part of the unit_map into a str

UNIT_MAP = {
    "flow": {
        "1" : "mg/h",
        "2": "g/h",
        "3": "kg/h",
        "4": "g/s",
        "mls/min": "ml/min",
        "6": "l/min",
        "7": "l/h",
        "8": "mg/min",
        "9": "g/min",
        "10": "kg/min",
        "11": "lb/h",
    },
    #works for the flow
    "pressure": {
        0 : "bar",
        1 : "psi",
        2 : "Pa",
        3 : "kPa",
        4 : "torr",
        5 : "atm",
        6 : "mbar",
        7 : "mH2O",
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

            #if self.device_type == "MFC":
                #self.flow_units = self._get_flow_units()
                 #   elif self.device_type == "PC":

            self.pressure_units = self._get_pressure_units()
            self.standard_flow = self._read_property("standard_flow")
            self.setpoint_slope = self._read_property("setpoint_slope")
            self.setpoint_slope_step = self._read_property("setpoint_slope_step")
            self.valve_max_capacity = self._read_property("valve_max_capacity")








            #self.max_flow_rate = self._read_property("max_flow")
            #self.flow = self._read_property("flow")
            self.pressure = self._read_property("pressure")
            self.serial_number = self.instrument.readParameter(1, 92)
            self.device_number = self._read_property("device_number")
            #self.sensor_type = self._read_property("pressure_sensor_type")
            #self.id_number_pc = self._read_property("identification_number_press")
            self.firmware_version = self._read_property("firmware_version")
            self.serial_number = self._read_property("serial_number")
            #self.flow = self._read_property("standard_flow")
#            self.capacity_flow = self._read_property("capacity_flow") no
            self.temperature = self._read_property("temperature") #tested
            self.fluid_name = self._read_property("fluid_name") #tested

            #new adds :
            #self.sensor_calibration_temp = self._read_property("sensor_calibration_temp")
            #self.fluid_unit = self._read_property("fluid_unit")
            #self.capacity_unit_type_temp = self._read_property("capacity_unit_type_temp")
            #self.fluid_temp = self._read_property("fluid_temp")
            #self.fluid_properties = self._read_property("fluid_properties")
            #self.valve_max_capacity = self._read_property("valve_max_capacity")
            #self.sensor_restriction_max_capacity = self._read_property("sensor_restriction_max_capacity")
            #self.dosing_unit = self._read_property("dosing_unit")
            #self.max_number_runs = self._read_property("max_number_runs")
            #self.max_allowed_dosing_time = self._read_property("max_allowed_dosing_time")
            #self.setpoint_slope = self._read_property("setpoint_slope")
            #self.setpoint_slope_step = self._read_property("setpoint_slope_step")
            #self.capacity_unit_type = self.read_property("capacity_unit_type")
            #self.measurement_stop_criteria = self._read_property("measurement_stop_criteria")
            #self.pressure_sensor_type = self._read_property("pressure_sensor_type")


            #key parameters to test in priority.
            self.fmeasure = self._read_property("fmeasure")
            self.fsetpoint = self._read_property("fsetpoint")
            self.valve_open = self._read_property("valve_open")


        def _get_device_type(self) -> str:
            """Determines the type of device based on its parameters."""

            # TODO : fix this lookup - (1, 72) is the serial!
            ## en cours
            device_type = self.instrument.readParameter(1, 96)
            print(device_type.strip())
            if device_type.strip().endswith("1883A"):
                return "PC"
            else:
                return "MFC"


            if self.device_type == "MFC":
                self.flow_units = self._get_flow_units()
            # elif self.device_type == "PC":
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
                   # "flow": Attr(
                    #    type=float, units=self.flow_units, rw=False, status=True),
                    "temperature": Attr(type=float, units="Celsius", rw=False),
                    "fluid_name": Attr(type=str, rw=False),
                    # TODO: Check properties below
                    "pressure": Attr(
                        type=float, units=self.pressure_units, rw=False, status=True
                    ),
    #                "max_flow": Attr(type=float, units=self.flow_units, rw=False),
                    #"capacity_flow": Attr(type=float, units=self.flow_units, rw=False),
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
                #if it does not work with the changed dde numbers then

                #then we try to debug using setpoints.
                #it seems to work

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
        #print(f"{interface.dev_get_attr(attr='temperature', **kwargs)=}")
       # try:
        #    print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")
        #except Exception as _:
         #   pass
        print(f"{interface.dev_get_attr(attr='pressure', **kwargs)=}")


        #CHECK TOO
#        print(f"{interface.dev_get_attr(attr='capacity_flow', **kwargs)=}")
        print(f"{interface.dev_get_attr(attr='fluid_name', **kwargs)=}")
        print(f"{interface.devmap[('COM5', channel)].attrs()=}")

        #print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")
        #print(f"{interface.dev_set_attr(attr='flow', val=30.0, **kwargs)=}")
        time.sleep(2)
        #print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")


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


