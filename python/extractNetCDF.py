import sys
from netCDF4 import Dataset

# create a table (csv) that has the columns,
#  global flag (0 or 1)
#  variable (blank for global)
#  instrument model,
#  instrument serial number,
#  deployment (time_deployment and time_recovery)
#  variable name
#  variable type
#  variable value
#  attribute name
#  attribute type
#  attribute value

def print_line(type, var_name, model, serial_number, time_deployment, time_recovry, variable_name, variable_dims, variable_shape, variable_type, variable_value, attribute_name, attribute_type, attribute_value):
    print("%s,%s,%s,%s,%s,%s,%s,\"%s\",\"%s\",%s,%s,%s,%s,\"%s\"" % (type, var_name, model, serial_number, time_deployment, time_recovry, variable_name, variable_dims, variable_shape, variable_type, variable_value, attribute_name, attribute_type, attribute_value))

for s in sys.argv[1:]:
    print(s)

    nc = Dataset(s)

    time_deployment_start = nc.getncattr('time_deployment_start')
    time_deployment_end = nc.getncattr('time_deployment_end')
    instrument = nc.getncattr('instrument')
    instrument_serial_number = nc.getncattr('instrument_serial_number')

    nc_attrs = nc.ncattrs()

    for a in nc_attrs:
        attr = nc.getncattr(a)
        #print("%s type %s = %s" % (a, type(attr).__name__, attr))
        print_line(1, "*", instrument, instrument_serial_number, time_deployment_start, time_deployment_end, "", "", "", "", "", a, type(attr).__name__, attr)

    nc_vars = nc.variables

    for v in nc_vars:
        #print("var %s" % (v))
        ncVar = nc.variables[v]
        v_attrs = ncVar.ncattrs()
        # print(len(ncVar.shape))
        if len(ncVar.shape) == 0:
            print_line(2, v, instrument, instrument_serial_number, time_deployment_start, time_deployment_end, v, ncVar.shape, ncVar.dimensions, ncVar.dtype, ncVar[:], "", "", "")
        elif (len(ncVar.shape) == 1) & (ncVar.shape[0] == 1):
            print_line(2, v, instrument, instrument_serial_number, time_deployment_start, time_deployment_end, v, ncVar.shape, ncVar.dimensions, ncVar.dtype, ncVar[:], "", "", "")
        else:
            print_line(2, v, instrument, instrument_serial_number, time_deployment_start, time_deployment_end, v, ncVar.shape, ncVar.dimensions, ncVar.dtype, "", "", "", "")

        for a in v_attrs:
            attr = ncVar.getncattr(a)
            print_line(3, v, instrument, instrument_serial_number, time_deployment_start, time_deployment_end, "", "", "", "", "", a, type(attr).__name__, attr)
            #print("%s type %s = %s" % (a, type(attr).__name__, attr))

