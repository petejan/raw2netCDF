# raw2netCDF
convert RAW instrument files to netCDF file, adding IMOS (or OceanSites) attributes

Sea Bird cnv file example,

~~~
- create a netCDF file from a RAW file
python3 sbeCNV2netCDF.py SBE37SMP-ODO-RS232_03715969_2019_03_27.cnv 
- add attributes to the netCDF file
python3 addAttributes.py SBE37SMP-ODO-RS232_03715969_2019_03_27.cnv.metadata.csv SBE37SMP-ODO-RS232_03715969_2019_03_27.cnv.nc

- create a metadata input file from an existing netCDF file

python3 extractNetCDF.py IMOS_ABOS-SOTS_COSTZ_20180801_SOFS_FV00_SOFS-7.5-2018-SBE37SMP-ODO-RS232-03715969-30m_END-20190327_C-20190606.nc > SBE37SMP-ODO-RS232_03715969_2019_03_27.cnv.metadata
~~~
