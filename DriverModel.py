from tomato.driverinterface_1_0 import ModelInterface, Attr, Task
from propar import PP_TYPE_FLOAT, instrument as Instrument
from typing import Any

# Move property_map outside the class as in rq 1
property_map = {
    'temperature': {'proc_nr': 33, 'parm_nr': 7, 'parm_type': PP_TYPE_FLOAT},
    'flow': {'param_id': 205},
    'pressure': {'proc_nr': 33, 'parm_nr': 5},
    'max_flow': {'param_id': 128},
    'flow_unit': {'param_id': 129}
}

class DriverInterface(ModelInterface):

    class DeviceManager(ModelInterface.DeviceManager):
        instrument: Instrument

        def __init__(self, driver: ModelInterface, key: tuple[str, int], **kwargs: dict):
            super().__init__(driver, key, **kwargs)
            address, channel = key
            self.instrument = Instrument(comport=address, address=channel)
            
            # Determine device type
            self.device_type = self.determine_device_type()
            
            # Store device information
            self.serial_number = self.instrument.readParameter(1, 92)
            self.flow_units = self.get_flow_units()
            self.pressure_units = self.get_pressure_units()

        def determine_device_type(self):
            device_type = self.instrument.readParameter(1, 72)
            return "MFC" if device_type == 8 else "PC" if device_type == 9 else "Unknown"

        def get_flow_units(self):
            flow_unit_id = self.instrument.readParameter(129)
            unit_map = {
                0: "mln/min", 1: "ln/min", 2: "lh/min", 3: "m3n/h", 4: "m3h/h",
                5: "mg/h", 6: "g/h", 7: "kg/h", 8: "g/s", 9: "ml/min",
                10: "l/min", 11: "l/h", 12: "m3/h", 13: "mg/min", 14: "g/min",
                15: "kg/min", 16: "lb/h", 17: "SLPM", 18: "NLPM", 19: "SCFH",
                20: "SCFM", 21: "NM3/h", 22: "NL/h", 23: "NL/min", 24: "SCCM"
            }
            return unit_map.get(flow_unit_id, "unknown")

        def get_pressure_units(self):
            pressure_unit_id = self.instrument.readParameter(130)
            unit_map = {
                0: "bar", 1: "psi", 2: "Pa", 3: "kPa", 4: "torr",
                5: "atm", 6: "mbar", 7: "mH2O", 8: "mmH2O", 9: "kg/cm2"
            }
            return unit_map.get(pressure_unit_id, "unknown")

    def do_task(self, task: Task, **kwargs):
        if task.name == "list_devices":
            list_available_devices()  # Call the existing function
        elif task.name == "connect_device":
            port = kwargs.get('port', self.get_valid_port())
            self.connect_device(port)
        elif task.name == "open_valve":
            self.open_valve_fully()
        elif task.name == "close_valve":
            self.close_valve()
        elif task.name == "collect_data":
            duration = kwargs.get('duration', self.get_experiment_duration())
            dataset = self.collect_data(duration)
            return dataset
        else:
            raise ValueError(f"Unknown task: {task.name}")

    def connect_device(self, port):
        self.instrument = Instrument(port)
        self.nodes = self.instrument.master.get_nodes()
        if not self.nodes:
            print("No devices found on the network.")
        else:
            print("\nAvailable Devices:")
            for i, node in enumerate(self.nodes):
                print(f"{i + 1}. {node}")
        
        # Get additional parameters
        self.max_flow_rate = self.get_attr('max_flow')
        self.max_flow_unit = self.get_attr('flow_unit')

    def get_valid_port(self):
        return get_valid_port()  # Call the existing function

    def get_experiment_duration(self):
        return get_experiment_duration()  # Call the existing function

    def open_valve_fully(self):
        print("Opening valve fully...")
        self.instrument.setpoint = 100.0

    def close_valve(self):
        print("Closing valve fully...")
        self.instrument.setpoint = 0.0

    def collect_data(self, duration):
        return BronkhorstDevice(self.instrument.comport).collect_data(duration)  # Call the existing method

    def set_attr(self, attr: str, val: Any, **kwargs: dict):
        if attr in property_map:
            params = property_map[attr]
            if 'param_id' in params:
                self.instrument.writeParameter(params['param_id'], val)
            else:
                self.instrument.write_parameters([{**params, 'data': val}])
        else:
            raise ValueError(f"Unknown property: {attr}")

    def get_attr(self, attr: str, **kwargs: dict):
        if attr in property_map:
            params = property_map[attr]
            if 'param_id' in params:
                return self.instrument.readParameter(params['param_id'])
            else:
                values = self.instrument.read_parameters([params])
                return values[0]['data']
        else:
            raise ValueError(f"Unknown property: {attr}")

    def attrs(self, **kwargs) -> dict[str, Attr]:
        attrs_dict = {
            'temperature': Attr(type=float, units="degC"),
            'flow': Attr(type=float, units=self.flow_units, rw=True, status=True),
        }
        if self.device_type == "PC":
            attrs_dict['pressure'] = Attr(type=float, units=self.pressure_units, rw=True)
        return attrs_dict

    def capabilities(self, **kwargs) -> set:
        caps = {"constant_flow"}
        if self.device_type == "PC":
            caps.add("constant_pressure")
        return caps

if __name__ == "__main__":
    kwargs = dict(address="COM4", channel=4)
    interface = DriverInterface()
    print(f"{interface=}")
    print(f"{interface.dev_register(**kwargs)=}")
    print(f"{interface.devmap=}")
    print(f"{interface.dev_get_attr(attr='temperature', **kwargs)=}")
    print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")
    print(f"{interface.dev_status(**kwargs)=}")
