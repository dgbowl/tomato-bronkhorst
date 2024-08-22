from tomato.driverinterface_1_0 import ModelInterface, Attr, Task
from propar import PP_TYPE_FLOAT, instrument as Instrument
from typing import Any

class DriverInterface(ModelInterface):
    class DeviceManager(ModelInterface.DeviceManager):
        instrument: Instrument

        def __init__(self, driver: ModelInterface, key: tuple[str, int], **kwargs: dict):
            super().__init__(driver, key, **kwargs)
            address, channel = key
            self.instrument = Instrument(comport = address, address = channel)

        def do_task(self, task: Task, **kwargs):
            # TODO: implement task loop
            pass

        def set_attr(self, attr: str, val: Any, **kwargs: dict):
            # TODO: implement setters
            pass

        def get_attr(self, attr: str, **kwargs: dict):
            property_map = {
                'temperature': {'proc_nr': 33, 'parm_nr': 7, 'parm_type': PP_TYPE_FLOAT},
                'flow': {'param_id': 205},
                'pressure': {'proc_nr': 33, 'parm_nr': 5},
                'max_flow': {'param_id': 128},
                'flow_unit': {'param_id': 129}
            }
            if attr in property_map:
                params = property_map[attr]
                if 'param_id' in params:
                    return self.instrument.readParameter(params['param_id'])
                else:
                    values = self.instrument.read_parameters([params])
                    return values[0]['data']
            else:
                raise ValueError(f"Unknown property: {attr}") # TODO: check validation

        def attrs(self, **kwargs) -> dict[str, Attr]:
            return dict(
                temperature=Attr(type=float, units="degC"),
                flow=Attr(type=float, units="ml/min", rw=True, status=True), # TODO: Units should be probed in __init__
                # pressure=Attr(type=float, units="bar", rw=True), # TODO: Units should be probed in __init__
            )

        def capabilities(self, **kwargs) -> set:
            return {
                "constant_flow",
            #    "constant_pressure",
            } # TODO: How do we know what's supported?

if __name__ == "__main__":
    kwargs = dict(address="COM4", channel=4)
    interface = DriverInterface()
    print(f"{interface=}")
    print(f"{interface.dev_register(**kwargs)=}")
    print(f"{interface.devmap=}")
    print(f"{interface.dev_get_attr(attr='temperature', **kwargs)=}")
    print(f"{interface.dev_get_attr(attr='flow', **kwargs)=}")
    print(f"{interface.dev_status(**kwargs)=}")
