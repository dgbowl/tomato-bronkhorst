#tested and works
#to add : automatically close the valve after we are done with the measurements 

import propar
import time
import numpy as np
import xarray as xr

# Function to read the temperature 
def read_temperature(instrument):
    params = [{'proc_nr': 33, 'parm_nr': 7, 'parm_type': propar.PP_TYPE_FLOAT}]
    values = instrument.read_parameters(params)
    return values[0]['data']

# Main function
def main():
    # Automatically connect to the local instrument
    instrument = propar.instrument('COM4')

    # Get list of connected devices
    nodes = instrument.master.get_nodes()

    if not nodes:
        print("No devices found on the network.")
    else:
        print("\nAvailable Devices:")
        for i, node in enumerate(nodes):
            print(f"{i+1}. {node}")

    # --- Get additional parameters --- 
    db = propar.database()
    temperature_params = db.get_propar_parameter(proc_nr=33, parm_nr=7)
    pressure_params = db.get_propar_parameter(proc_nr=33, parm_nr=5)
    max_flow_rate, max_flow_unit = instrument.readParameter(128), instrument.readParameter(129)

    # --- Ask user for experiment duration --- 
    print('Enter the duration of the experiment in seconds:')
    duration = int(input('Duration in s: '))

    # --- Collect and process data --- (enhanced)
    temperature_data = []
    timestamps = []
    end_time = time.time() + duration
    while time.time() < end_time:
        temperature = read_temperature(instrument)  # Use the read_temperature function
        flow_rate = instrument.readParameter(205)  # Get flow rate
        pressure = instrument.readParameter(33, 5) # Get pressure

        temperature_data.append(temperature)
        timestamps.append(time.time())

        print(
    f"Time: {time.time():.2f} s, "
    f"Temperature: {temperature:.2f} °C, "  
    f"Flow Rate: {flow_rate:.2f} {max_flow_unit or 'Unknown'}, "
#    f"Pressure: {pressure:.2f} {pressure_params[0].unit or 'Unknown'}"
)


        time.sleep(1)

    # --- Create xarray Dataset ---
    temperature_array = xr.DataArray(
        temperature_data,
        coords=[timestamps],
        dims=["time"],
        name="temperature",
        attrs={"units": "°C"}  # Add units attribute
    )

    # Create xarray for other measurements
    flow_rate_array = xr.DataArray(
        [instrument.readParameter(205) for _ in range(len(temperature_data))],  
        coords=[timestamps],
        dims=["time"],
        name="flow_rate",
        attrs={"units": max_flow_unit}
    )
    pressure_array = xr.DataArray(
        [instrument.readParameter(33, 5) for _ in range(len(temperature_data))],  
        coords=[timestamps],
        dims=["time"],
        name="pressure",
#        attrs={"units": pressure_params[0].unit}
    )

    dataset = xr.Dataset({
        "temperature": temperature_array,
        "flow_rate": flow_rate_array,
        "pressure": pressure_array
    })


    print('\n Collected data:')
    print(dataset)


if __name__ == "__main__":
    main()
