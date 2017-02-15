#!/bin/csh -f

# Landsat DMS version 1.2
# revision history
# v1.0_HDF:  used in-house LEDAPS SR products (in HDF format)
# v1.1_ENVI: used USGS Landsat SR products (in GeoTIFF, ENVI or HDF format)
# v1.2_ENVI: enabled Landsat cloud mask (USGS Landsat fmask product)

#set convert = "th_intC2floatK.exe"
#set ldata = $LANDSAT_DIR
set bands = ("blue" "green" "red" "nir" "swir1" "swir2" "tir")
# create input files for LST sharpening
if $#argv != 3 then
    echo "Usage: prepareDMS.csh <landsat directory>, <lndsr_file>, <thermal_file>"
    echo "       <landsat directory> is the directory where the landsat surface reflectance is located"
    echo "       <lndsr_file> is the surface reflectance file from lndsr"
    exit
else
	set ldata = $argv[1]
    set lndsr = $argv[2]
    set fband6 = $argv[3]
    set inp = "dms.inp"
endif

set fstem = `echo $lndsr | sed 's/.xml//'`
echo $fstem

set scene = $fstem
set file = `ls $ldata/$fstem*.$bands[1].dat.hdr`
set nrows = `grep lines $file | awk '{print $3}'`
set ncols = `grep samples $file | awk '{print $3}'`
set res = `grep "map info" $file | awk '{print $9}' | sed 's/,//'`
set ul = `grep "map info" $file | awk '{print $7, $8}' | sed 's/,//g'`
set zone = `grep "map info" $file | awk '{print $11}' | sed 's/,//'`

# get date in yyyy-mm-dd
set date = `grep "<acquisition_date>" $ldata/$lndsr | sed 's/>/ /' | sed 's/<\// /' | awk '{print $2}'`
set instrument = `grep "<satellite>" $ldata/$lndsr | sed 's/>/ /' | sed 's/<\// /' | awk '{print $2}'`

set outf = "$scene.sharpened_band6.bin"

# determine resolution for original thermal band
if ($instrument == "LANDSAT_5") then
  set th_res = "120.0"
else if($instrument == "LANDSAT_7") then
  set th_res = "60.0"
else if($instrument == "LANDSAT_8") then
  set th_res = "90.0"
else
  echo "Wrong Satellite Setting $instrument"
  exit
endif
#echo norws=$nrows ncols=$ncols res=$res ul=$ul lr=$lr zone=$zone date=$date scene=$scene instrument=$instrument th_res=$th_res
set sbands=""
# skip if output file exists
if (-e $outf) then
   echo "File $outf exists, skip data preparation"
else
  # prepare inputs (binary) from lndsr
  @ bi = 1
  while ($bi <= 6)
    set sds = band$bi
    set sds = `ls $ldata/$fstem*.$bands[$bi].dat`
	echo $sds
    set sbands = ($sbands $sds)
    @ bi++
  end

  set cmask = `ls $ldata/$fstem*cfmask.cloud.dat`
  # convert thermal data from Celsius degree (DN*0.01)to Kelvin for DMS processing
 # $convert band6.bin fband6.bin
 #set fband6.bin = $fband6
echo "# input file for Data Mining Sharpener" > $inp
echo "NFILES = 6" >> $inp
echo "SW_FILE_NAME = $sbands" >> $inp
echo "SW_CLOUD_MASK = $cmask" >> $inp
echo "SW_FILE_TYPE = binary" >> $inp
echo "SW_CLOUD_TYPE = binary" >> $inp
echo "SW_NROWS = $nrows" >> $inp
echo "SW_NCOLS = $ncols" >> $inp
echo "SW_PIXEL_SIZE = $res" >> $inp
echo "SW_FILL_VALUE = -9999" >> $inp
echo "SW_CLOUD_CODE = 1" >> $inp
echo "SW_DATA_RANGE = -2000, 16000" >> $inp
echo "SW_UPPER_LEFT_CORNER = $ul" >> $inp
echo "SW_PROJECTION_CODE = 1" >> $inp
echo "SW_PROJECTION_PARAMETERS = 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0" >> $inp
echo "SW_PROJECTION_ZONE = $zone" >> $inp
echo "SW_PROJECTION_UNIT = 1" >> $inp
echo "SW_PROJECTION_DATUM = 12" >> $inp
 
echo "ORG_TH_FILE_NAME = $ldata/$fband6" >> $inp
echo "ORG_TH_FILE_TYPE = BINARY" >> $inp
echo "ORG_TH_DATA_RANGE = 230., 370." >> $inp
echo "ORG_TH_PIXEL_SIZE = $res" >> $inp
echo "ORG_NROWS = $nrows" >> $inp
echo "ORG_NCOLS = $ncols" >> $inp

echo "RES_TH_PIXEL_SIZE = $th_res " >> $inp

echo "PURE_CV_TH = 0.1" >> $inp
echo "ZONE_SIZE = 240" >> $inp
echo "SMOOTH_FLAG = 1" >> $inp
echo "CUBIST_FILE_STEM = th_samples" >> $inp
echo "OUT_FILE = $outf" >> $inp
echo "end" >> $inp
endif 

