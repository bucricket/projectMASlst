#! /bin/csh -f

# Landsat DMS version 1.2
# revision history
# v1.0_HDF:  used in-house LEDAPS SR products (in HDF format)
# v1.1_ENVI: used USGS Landsat SR products (in GeoTIFF, ENVI or HDF format)
# v1.2_ENVI: enabled Landsat cloud mask (USGS Landsat fmask product)
# v1.2.1: do not process if # of samples < 15 in global model

# define the top data directory 
#set data_path = `pwd`

# defin three subdirectory under $data_path
#set ldata = $LANDSAT_DIR
#set lndlst = $LANDSAT_LST_DIR

if $#argv != 1 then
    echo "Usage: prepareDMS.csh <landsat directory>"
    echo "       <landsat directory> is the directory where the landsat sr and corrected lst files are located"
    exit
else
	set ldata = $argv[1]
    set inp = "dms.inp"
endif

if (! -e $lndlst) then
  mkdir $lndlst
  endif

# define DMS executable programs
set tsamples = "get_samples"
set predict = "predict_fineT"
set combine = "combine_models"
set prepare = "prepareDMS3_sa.csh"

# define cubist regression tree program
set cubist = "cubist"

#define maximum numbers of samples (1M)
set MAX_NSAMS = 1000000

cd $ldata
# find all lndsr file under Landsat directory
set landsat = `ls L*.xml`
echo "LANDSAT" $landsat
set landband6 = `ls lndsr*band6.bin`
echo "LANDBAND6" $landband6

#if $#argv != 1 then
#    echo "Usgae DMS.csh <lndsr_file>"
#    echo "      <lndsr_hdf_file> is the surface reflectance file from lndsr"
#    exit
#endif
#cd $data_path/INPUT/Surface/LST   

#cd $lndlst

@ i=1
# go through each Landsat scenes under the directory
while($i <= $#landsat)

  echo "Processing $landsat[$i] max 1M samples"

  # find band6 file associated with this .xml file
  set base = `basename $landsat[$i] .xml` 
#  echo $base
  @ j=1
  @ jf=-999
  while($j <= $#landband6)
    if ($landband6[$j] =~ lndsr.$base.cband6.bin) then
       @ jf = $j
    endif
    @ j++
  end
  if ($jf == -999) then
   echo "Band6 match not found for " $landsat[$i]
   echo "  Proceed to next file."
   echo " "
   @ i++
   continue
  endif
 
  # skip if output file exists
  set fstem = `echo $landsat[$i] | sed 's/.xml//'`
  set outf = "$fstem.sharpened_band6.bin"
  if (-e $outf) then
    echo "File $outf exists, skip sharpening"
    echo " "
    rm dms.inp
    @ i++
    continue
  endif
 
  # prepare files
  echo "IMAGE PAIR: $landsat[$i] $landband6[$jf]"
  $prepare $ldata $landsat[$i] $landband6[$jf]

  set input = "dms.inp"
  set cubistf = `grep "CUBIST_FILE_STEM = " $input | sed 's/CUBIST_FILE_STEM = //'`
  set outf = `grep "OUT_FILE = " $input | sed 's/OUT_FILE = //'`
  set nrows = `grep "SW_NROWS = " $input | sed 's/SW_NROWS = //'`
  set ncols = `grep "SW_NCOLS = " $input | sed 's/SW_NCOLS = //'`
  set spec_res = `grep "SW_PIXEL_SIZE = " $input | sed 's/SW_PIXEL_SIZE = //'` 
  set th_res = `grep "RES_TH_PIXEL_SIZE = " $input | sed 's/RES_TH_PIXEL_SIZE = //'`
  set log = "tree.log" 
  set scale = `echo $th_res $spec_res | awk '{print $1/$2}'`
  @ cnrows = $nrows / $scale
  @ cncols = $ncols / $scale

  echo ""
  echo "*** Doing Prediction with Global Model ***"
  # global model prediction
  $tsamples $input

  set nsams = `wc -l $cubistf.data | awk '{printf("%d", $1)}'`
  if ($nsams < 15) then 
    echo "no enough TIR-SR samples for sharpening process due to clouds etc., continue ..."
    rm dms.inp $cubistf.data
    @ i++
    continue
  endif
  
  set percent = `echo $MAX_NSAMS $nsams | awk '{printf("%d", $1/$2*100)}'`
  if($percent > 100) @ percent = 100
  if($percent < 0) @ percent = 1
  echo "   Running cubist..."
  $cubist -f $cubistf -r 30 -u > $log
  echo "   Generating prediction..."
  $predict $input 
  set global_out=`echo $outf| sed 's/.bin/.global/'`
  echo "global model results are saved in: " $global_out
  mv $outf $global_out
  cp $outf.hdr $global_out.hdr

  echo ""
  echo "*** Doing Prediction with Local Model ***"
  # local model prediction
  @ s_row = 0
  @ s_col = 0
  @ wsize1 = 200
  @ overlap1 = 20
  # use same size of sub-area as TM 
  set wsize = `echo $wsize1 $th_res | awk '{printf("%d", $1*120./$2)}'` 
  set overlap = `echo $overlap1 $th_res | awk '{printf("%d", $1*120./$2)}'` 
  echo $wsize $overlap   

  # window size is defined in coarse resolution thermal band coordinate
  # samples from 141 * 141 windows, but prediction for 100 * 100 windows
  # (100*100)/(141*141) = 50%
  # total 20000 samples, should be enough
  # change to 50*50 in about 5000 samples 

  while($s_row<$cnrows)
    while($s_col<$cncols) 
      @ e_row = $s_row + $wsize
      @ e_col = $s_col + $wsize
      echo ""
      echo "--- processing central  window" $s_row $s_col $e_row $e_col
      @ os_row = $s_row - $overlap
      @ os_col = $s_col - $overlap
      @ oe_row = $e_row + $overlap
      @ oe_col = $e_col + $overlap
      echo "    overlapped sampling window" $os_row $os_col $oe_row $oe_col
      $tsamples $input $os_row $os_col $oe_row $oe_col
      set nsamples = `wc -l $cubistf.data | awk '{print $1}'`
      if($nsamples != "0") then 
        # do cubist prediction
        $cubist -f $cubistf -u -r 15 >> $log
        $predict $input $s_row $s_col $e_row $e_col
        # cp $outf $outf.$s_row$s_col
      endif
      @ s_col += $wsize
    end
    @ s_col = 0
    @ s_row += $wsize
  end

  set local_out=`echo $outf| sed 's/.bin/.local/'`
  echo "local model results are saved in:" $local_out
  mv $outf $local_out
  cp $outf.hdr $local_out.hdr

  echo ""
  echo "*** Combining Local and Gloal Model ***"
  # replace global prediction with local prediction if errors are smaller
  echo "Combining" $global_out  "and"  $local_out  "to"  $outf
  $combine $input

  rm band?.bin fband6.bin dms.inp th_samples.* tmp.hdr *.global* *.local* tree.log

  echo " "

  @ i++
end



