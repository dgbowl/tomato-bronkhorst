# tomato-bronkhorst
`tomato` driver for Bronkhorst flow and pressure controllers.

This driver is a wrapper around the [`bronkhorst-propar`](https://github.com/bronkhorst-developer/bronkhorst-propar) library. This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Supported functions

### Capabilities
- `constant_pressure` for pressure controllers only (`0` in `SENSOR_MAP`)
- `constant_flow` for (mass) flow controllers (`1` and `3` in `SENSOR_MAP`)

### Attributes
- `setpoint` for all devices, `pint.Quantity(float, self.device_unit)` within the capacity range of the device
- `control_mode` for all devices, dictates valve status, `str` from the `MODE_MAP`
- `temperature` optional - if available, `RO`, `pint.Quantity(float, "celsius")`

## Contributors

- Peter Kraus
- Alexandre Gbocho
