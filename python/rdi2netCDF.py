#!/usr/bin/python3

# raw2netCDF
# Copyright (C) 2019 Peter Jansen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import re

import datetime
from netCDF4 import num2date, date2num
from netCDF4 import Dataset
import numpy as np
import struct

header_decoder = {'keys': ['spare', 'dataTypes'],
                  'unpack': "<BB"}
fixed_decoder = {'keys': ['cpuVER', 'cpuREV', 'sysConfig', 'read', 'lag_len', 'no_beam', 'num_cells',
                          'pings_per_ensemble', 'cell_length', 'blank_after_tx', 'profile_mode', 'low_corr',
                          'code_reps', 'gd_min', 'error_vel_max', 'tpp_min', 'tpp_sec', 'tpp_hun_sec', 'coord_trans',
                          'head_alignment', 'head_bias', 'sensor_source', 'sensor_avaliable', 'bin1_dist',
                          'xmit_pulse_len', 'ref_layer', 'false_target_thredh', 'spare', 'tx_lag_dist', 'cpu_board',
                          'system_bandwidth', 'system_power', 'spare2', 'inst_serial', 'beam_angle'],
                 'unpack': "<BBHBBBBHHHBBBBHBBBBHHBBHHHBBHQHBBLB"}
variable_decoder = {'keys': ['ensemble_no', 'year', 'month', 'day', 'hour', 'minute', 'second', 'hsec',
                             'ensemble_msb', 'result', 'speed_of_sound', 'depth_of_trans', 'heading', 'pitch',
                             'roll', 'salinity', 'temperature', 'mpt_min', 'mpt_sec', 'mpt_hsec', 'hdg_stdev',
                             'pitch_stdev', 'roll_stdev', 'adc0', 'adc1', 'adc2', 'adc3', 'adc4', 'adc5', 'adc6', 'adc7',
                             'error_status', 'spare1', 'pressure', 'press_variance', 'spare2', 'rtc_cen',
                             'rtc_year', 'rtc_month', 'rtc_day', 'rtc_hour', 'rtc_min', 'rtc_sec', 'rtc_hsec'],
                    'unpack': "<H7BB8HBBBBBB8BIHIIB8B"}

def main(files):
    filepath = files[1]
    with open(filepath, "rb") as binary_file:
        data = binary_file.read(2)
        while data:
            print("hdr ", data)
            if data == b'\x7f\x7f':

                data = binary_file.read(2)
                (ensemble_len,) = struct.unpack("<H", data)

                print("length ", ensemble_len)
                ensemble = binary_file.read(ensemble_len-4)

                cksum = binary_file.read(2)
                print("checksum ", cksum)

                header = struct.unpack(header_decoder["unpack"], ensemble[0:2])
                header_decoded = dict(zip(header_decoder['keys'], header))
                print("header ", header_decoded)

                n = 2
                addrs = [0 for x in range(0, header_decoded["dataTypes"])]
                for i in range(0, header_decoded["dataTypes"]):
                    addr_data = ensemble[n:n+2]
                    addrs[i] = struct.unpack("<H", addr_data)[0]
                    #print("addr ", addrs[i])
                    n += + 2

                while n < (ensemble_len - 4):
                    data = ensemble[n:n+2]
                    n += 2
                    print("data hdr ", data)
                    if data == b'\x00\x00':
                        data = ensemble[n:n+57]
                        n += 57
                        fixed = struct.unpack(fixed_decoder["unpack"], data)
                        fixed_decoded = dict(zip(fixed_decoder['keys'], fixed))
                        print("fixed ", fixed_decoded)

                    elif data == b'\x80\x00':
                        data = ensemble[n:n+63]
                        n += 63
                        variable = struct.unpack(variable_decoder["unpack"], data)
                        variable_decoded = dict(zip(variable_decoder['keys'], variable))
                        print("variable header ", variable_decoded)
                        ts = datetime.datetime(year=variable_decoded['rtc_cen']*100 + variable_decoded['rtc_year'], month=variable_decoded['rtc_month'],
                                               day=variable_decoded['rtc_day'],
                                               hour=variable_decoded['rtc_hour'], minute=variable_decoded['rtc_min'], second=variable_decoded['rtc_sec'],
                                               microsecond=variable_decoded['rtc_hsec']*1000*10)
                        print("ts = ", ts)

                    if data == b'\x00\x01':  # velocity data
                        data = ensemble[n:n+8*fixed_decoded['num_cells']]
                        n += len(data)
                    elif data == b'\x00\x02':  # correlation mag
                        data = ensemble[n:n+4*fixed_decoded['num_cells']]
                        n += len(data)
                    elif data == b'\x00\x03':  # echo intensity
                        data = ensemble[n:n+4*fixed_decoded['num_cells']]
                        n += len(data)
                    elif data == b'\x00\x04':  # percent good
                        data = ensemble[n:n+4*fixed_decoded['num_cells']]
                        n += len(data)
                    elif data == b'\x00\x05':  # status data
                        data = ensemble[n:n+4*fixed_decoded['num_cells']]
                        n += len(data)

            data = binary_file.read(2)

    # create the netCDF file
    outputName = filepath + ".nc"

    print("output file : %s" % outputName)

    ncOut = Dataset(outputName, 'w', format='NETCDF4')

    # add global attributes
    instrument_model = 'WORKHORSE'
    instrument_serialnumber = fixed_decoded['inst_serial']

    ncOut.instrument = 'RDI - ' + instrument_model
    ncOut.instrument_model = instrument_model
    ncOut.instrument_serial_number = instrument_serialnumber

    return outputName


if __name__ == "__main__":
    main(sys.argv)
