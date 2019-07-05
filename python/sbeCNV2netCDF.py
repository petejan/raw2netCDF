import sys
import re

from datetime import datetime
from netCDF4 import num2date, date2num
from netCDF4 import stringtochar
from netCDF4 import Dataset
import numpy as np

#
# parse the file
#

filepath = sys.argv[1]

hardware_expr   = r"\* <HardwareData DeviceType='(\S+)' SerialNumber='(\S+)'>"
name_expr       = r"# name (\d+) = (.*): *(.*)"
end_expr        = r"\*END\*"
sampleExpr      = r"\* sample interval = (\d+) seconds"
startTimeExpr   = r"# start_time = (.*)"
intervalExpr    = r"# interval = (\S+): (\d+)"

nvalues_expr    = r"# nvalues = (\d+)"
nquant_expr     = r"# nquan = (\d+)"

use_expr        = r"<(Use.*)>(.?)<\/\1>"
equa_group      = r"<(.*) equation='(\d+)' >"

sensor_start    = r"<sensor(.*)>"
sensor_end      = r"</sensor(.*)>"
comment         = r"<!--(.+?)-->"
tag             = r".*<(.+?)>(.+)<\/\1>|.*<(.+=.*)>"

instr_exp       = "\* Sea-Bird.?(\S+)"

hdr = True
dataLine = 0
name = []
text = []
number_samples_read = 0
nVars = 0

# map sea bird name to netCDF variable name
nameMap = {}
nameMap["TIMEK"] = "TIME"
nameMap["TV290C"] = "TEMP"
nameMap["COND0SM"] = "CNDC"
nameMap["PRDM"] = "PRES_REL"
nameMap["SAL00"] = "PSAL"
nameMap["SBEOPOXMMKG"] = "DOX2"
nameMap["SBEOPOXMLL"] = "DOXS"
nameMap["SBEOPOXMML"] = "DOX1"
nameMap["SBEOXTC"] = "DOX_TEMP"
nameMap["OXSOLMMKG"] = "OXSOL"
nameMap["DENSITY00"] = "DENSITY"
nameMap["FLAG "] = None

# also map units .....

with open(filepath, 'r', errors='ignore') as fp:
    line = fp.readline()
    cnt = 1
    while line:
        #print("Line {}: {} : {}".format(cnt, dataLine, line.strip()))

        if hdr:
            matchObj = re.match(instr_exp, line)
            if matchObj:
                #print("instr_exp:matchObj.group() : ", matchObj.group())
                #print("instr_exp:matchObj.group(1) : ", matchObj.group(1))
                instrument_model = matchObj.group(1)

            matchObj = re.match(tag, line)
            if matchObj:
                print("tag:matchObj.group() : ", matchObj.group())
                #print("tag:matchObj.group(1) : ", matchObj.group(1))
                #print("tag:matchObj.group(2) : ", matchObj.group(2))
                #print("tag:matchObj.group(3) : ", matchObj.group(3))

            matchObj = re.match(hardware_expr, line)
            if matchObj:
                #print("hardware_expr:matchObj.group() : ", matchObj.group())
                #print("hardware_expr:matchObj.group(1) : ", matchObj.group(1))
                #print("hardware_expr:matchObj.group(2) : ", matchObj.group(2))
                instrument_model = matchObj.group(1)
                instrument_serialnumber = matchObj.group(2)

            matchObj = re.match(sampleExpr, line)
            if matchObj:
                #print("sampleExpr:matchObj.group() : ", matchObj.group())
                #print("sampleExpr:matchObj.group(1) : ", matchObj.group(1))
                sample_interval = int(matchObj.group(1))

            matchObj = re.match(intervalExpr, line)
            if matchObj:
                #print("intervalExpr:matchObj.group() : ", matchObj.group())
                #print("intervalExpr:matchObj.group(1) : ", matchObj.group(1))
                #print("intervalExpr:matchObj.group(1) : ", matchObj.group(2))
                sample_interval = int(matchObj.group(2))

            matchObj = re.match(nvalues_expr, line)
            if matchObj:
                #print("nvalues_expr:matchObj.group() : ", matchObj.group())
                #print("nvalues_expr:matchObj.group(1) : ", matchObj.group(1))
                number_samples = int(matchObj.group(1))

            matchObj = re.match(use_expr, line)
            if matchObj:
                print("use_expr:matchObj.group() : ", matchObj.group())
                #print("use_expr:matchObj.group(1) : ", matchObj.group(1))

            matchObj = re.match(name_expr, line)
            if matchObj:
                #print("name_expr:matchObj.group() : ", matchObj.group())
                #print("name_expr:matchObj.group(1) : ", matchObj.group(1))
                #print("name_expr:matchObj.group(2) : ", matchObj.group(2))
                #print("name_expr:matchObj.group(3) : ", matchObj.group(3))
                nameN = int(matchObj.group(1))
                comment = matchObj.group(3)
                unitObj = re.match(r".*\[((.*), )?(.*)\]", comment)
                #print("unit match ", unitObj, comment)
                unit = None
                if unitObj:
                    unit = unitObj.group(3)
                    #print("unit:unitObj.group(3) : ", unit)

                # construct a var name from the sea bird short name
                varName = matchObj.group(2)
                varName = re.sub(r'[-/]', '', varName).upper()

                ncVarName = None
                if varName in nameMap:
                    ncVarName = nameMap[varName]
                    if ncVarName:
                        name.insert(nVars, (nameN, ncVarName, matchObj.group(3), unit))
                        nVars = nVars + 1
                print("name {} : {} ncName {}".format(nameN, varName, ncVarName))

            matchObj = re.match(end_expr, line)
            if matchObj:
                hdr = False
                nVariables = len(name)

                data = np.zeros((number_samples, nVariables))
                data.fill(np.nan)
        else:
            lineSplit = line.split()
            ##print(data)
            splitVarNo = 0
            try:
                for v in name:
                    ##print("{} : {}".format(i, v))
                    data[number_samples_read][splitVarNo] = float(lineSplit[v[0]])
                    splitVarNo = splitVarNo + 1
                number_samples_read = number_samples_read + 1
            except ValueError:
                #print("bad line")
                pass

            dataLine = dataLine + 1

        line = fp.readline()
        cnt += 1

print("nSamples %d samplesRead %d nVariables %d data shape %s" % (number_samples, number_samples_read, nVariables, data.shape))

# trim data
odata = data[:number_samples_read]
print(odata.shape)

#
# built the netCDF file
#

ncTimeFormat = "%Y-%m-%dT%H:%M:%SZ"

outputName = filepath + ".nc"

print("output file : %s" % outputName)

ncOut = Dataset(outputName, 'w', format='NETCDF4')

ncOut.instrument_make = 'Sea-Bird Electronics'
ncOut.instrument_serial_number = instrument_serialnumber
ncOut.instrument_model = instrument_model

#     TIME:axis = "T";
#     TIME:calendar = "gregorian";
#     TIME:long_name = "time";
#     TIME:units = "days since 1950-01-01 00:00:00 UTC";

tDim = ncOut.createDimension("TIME", number_samples_read)
ncTimesOut = ncOut.createVariable("TIME", "d", ("TIME",), zlib=True)
ncTimesOut.long_name = "time"
ncTimesOut.units = "days since 1950-01-01 00:00:00 UTC"
ncTimesOut.calendar = "gregorian"
ncTimesOut.axis = "T"

t_epoc = (datetime(2000, 1, 1)-datetime(1950, 1, 1)).total_seconds()

i = 0
for v in name:
    print("Variable %s : unit %s" % (v[1], v[3]))
    varName = v[1]
    if varName == 'TIME':
        #print(data[:, v[0]])
        ncTimesOut[:] = (odata[:, v[0]] + t_epoc) / 3600 / 24
        #print("Create time variable ", ncTimesOut[0])
    else:
        ncVarOut = ncOut.createVariable(varName, "f4", ("TIME",), fill_value=np.nan, zlib=True)
        ncVarOut.comment = v[2]
        if v[2]:
            ncVarOut.units = v[3]
        #print("Create Variable %s : %s" % (ncVarOut, data[v[0]]))
        ncVarOut[:] = odata[:, v[0]]

    i = i + 1

ncOut.setncattr("time_coverage_start", num2date(ncTimesOut[0], units=ncTimesOut.units, calendar=ncTimesOut.calendar).strftime(ncTimeFormat))
ncOut.setncattr("time_coverage_end", num2date(ncTimesOut[-1], units=ncTimesOut.units, calendar=ncTimesOut.calendar).strftime(ncTimeFormat))
ncOut.setncattr("date_created", datetime.utcnow().strftime(ncTimeFormat))

ncOut.close()
