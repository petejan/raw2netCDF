#!/bin/sh

# extract metadata
python3 python/extractNetCDFmetadata.py data/IMOS_ABOS-SOTS_COSTZ_20180801_SOFS_FV00_SOFS-7.5-2018-SBE37SMP-ODO-RS232-03715969-30m_END-20190327_C-20190606.nc  > data/imos.metadata.csv
python3 python/extractNetCDFmetadata.py data/IMOS_ABOS-SOTS_COSTZ_20180801_SOFS_FV00_SOFS-7.5-2018-SBE37SMP-ODO-RS232-03715969-30m_END-20190327_C-20190606.nc  > data/sots.metadata.csv
python3 python/extractNetCDFmetadata.py data/IMOS_ABOS-SOTS_COSTZ_20180801_SOFS_FV00_SOFS-7.5-2018-SBE37SMP-ODO-RS232-03715969-30m_END-20190327_C-20190606.nc  > data/variable.metadata.csv
#  from imos-deploy database
python3 python/getDBmetadata.py "SOFS%2018%"  > metadata/SOFS-2018.metadata.csv

# process a file
python3 python/sbeCNV2netCDF.py data/SBE37SMP-ODO-RS232_03715969_2019_03_27.cnv 
python3 python/starmon2netCDF.py data/5T4778.DAT

mv data/SBE37SMP-ODO-RS232_03715969_2019_03_27.cnv.nc data/tmp.nc

# add attributes
python3 python/addAttributes.py data/tmp.nc metadata/sofs-2018.metadata.csv metadata/variable.metadata.csv metadata/imos.metadata.csv metadata/sots.metadata.csv 
# name the file from its attributes and variables
python3 python/imosNetCDFfileName.py data/tmp.nc
