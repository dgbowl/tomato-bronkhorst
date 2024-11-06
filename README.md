# tomato-bronkhorst
`tomato` driver for Bronkhorst flow and pressure controllers.

This driver is a wrapper around the [`bronkhorst-propar`](https://github.com/bronkhorst-developer/bronkhorst-propar) library. This driver is developed by the [ConCat lab at TU Berlin](https://tu.berlin/en/concat).

## Supported functions

### Capabilities
- `constant_pressure` for pressure controllers (`0` in `SENSOR_MAP`)
- `constant_flow` for (mass) flow controllers (`1` and `3` in `SENSOR_MAP`)

### Attributes
- `pressure` for pressure controllers, `RO`, `float`
- `flow` for flow controllers, `RO`, `float`
- `control_mode` for all devices, `RW`, `str` from the `MODE_MAP`
- `setpoint` for all devices, `RW`, `float` within the capacity range
- `temperature` for all devices, if available

## Contributors

- Peter Kraus
- Alexandre Gbocho
