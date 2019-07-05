from netCDF4 import Dataset
import sys
import numpy as np
import csv

filepath = sys.argv[1]
netCDFfile = sys.argv[2]

ds = Dataset(netCDFfile, 'a')

#print(ds)

ds_variables = ds.variables
print(ds_variables)

with open(filepath, mode='r') as csv_file:
    csv_reader = csv.reader(csv_file, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
    for lineSplit in csv_reader:
        print(lineSplit)
        if lineSplit[0] != ';':

            #print(len(lineSplit))

            if len(lineSplit) >= 14:
                # TODO: match instrument, serial number, time_in, time_out

                # global attributes
                if lineSplit[0] == '1':
                    name = lineSplit[11]
                    att_type = lineSplit[12]
                    if att_type == 'float64':
                        value = np.float64(lineSplit[13])
                    elif att_type == 'float32':
                        value = np.float32(lineSplit[13])
                    elif att_type == 'int16':
                        value = np.float16(lineSplit[13])
                    else:
                        value = lineSplit[13]
                    print("add global %s (%s) = %s" % (name, att_type, value))
                    ds.setncattr(name, value)

                # variable attributes
                if lineSplit[0] == '3':  # variable attribute
                    var_name = lineSplit[1]
                    print(var_name)
                    if var_name in ds_variables:
                        name = lineSplit[11]
                        att_type = lineSplit[12]
                        if att_type == 'float64':
                            value = np.float64(lineSplit[13])
                        elif att_type == 'float32':
                            value = np.float32(lineSplit[13])
                        elif att_type == 'int16':
                            value = np.float16(lineSplit[13])
                        else:
                            value = lineSplit[13]
                        print("add variable %s attribute %s (%s) = %s" % (var_name, name, att_type, value))
                        ds_variables[var_name].setncattr(name, value)

ds.close()
