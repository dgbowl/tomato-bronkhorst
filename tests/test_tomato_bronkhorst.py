from tomato_bronkhorst import DriverInterface, Device

if __name__ == "__main__":
    import time

    kwargs = dict(address="COM3", channel="80")
    interface = DriverInterface()
    # device = Device(driver="bronkhorst", key=("COM5", "80"))
    # print(f"{interface=}")
    print(f"{interface.cmp_register(**kwargs)=}")


if False:
    cmp = interface.devmap[("COM5", "80")]
    print(f"{cmp=}")
    print(f"{cmp.device_type=}")
    print(f"{cmp.capabilities()=}")
    print(f"{cmp.capacity_max=}")
    print(f"{cmp.last_data=}")
    print(f"{cmp.device_unit=}")
    print(f"{cmp.do_measure()=}")
    time.sleep(1)
    print(f"{cmp.last_data=}")
    print(f"{cmp.set_attr(attr="control_mode", val="bus/RS232")=}")
    time.sleep(1)
    print(f"{cmp.last_data=}")
    print(f"{cmp.do_measure()=}")
    print(f"{cmp.last_data=}")
    print(f"{cmp.set_attr(attr="setpoint", val="1700 mbar")=}")
    print(f"{cmp.do_measure()=}")
    time.sleep(1)
    print(f"{cmp.last_data=}")
    print(f"{cmp.do_measure()=}")
    time.sleep(10)
    print(f"{cmp.last_data=}")
    print(f"{cmp.set_attr(attr="setpoint", val="1200 mbar")=}")
    print(f"{cmp.do_measure()=}")
    time.sleep(10)
    print(f"{cmp.last_data=}")
    print(f"{cmp.do_measure()=}")
    time.sleep(1)
    print(f"{cmp.last_data=}")
    print(f"{cmp.set_attr(attr="setpoint", val=1.7)=}")
    time.sleep(1)
    print(f"{cmp.do_measure()=}")
    print(f"{cmp.last_data=}")
    print("Disconnect Now")
    time.sleep(5)
    print(f"{cmp.last_data.pressure=}")
