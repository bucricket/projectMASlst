#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 14:03:53 2017

@author: mschull
"""
import os
from .utils import folders
from .landsatTools import landsat_metadata
import glob
import subprocess
from joblib import Parallel, delayed
import shutil

base = os.getcwd()
Folders = folders(base)   
landsatSR = Folders['landsatSR']
landsatTemp = Folders['landsatTemp']
# global prediction


def perpareDMSinp(sceneID,s_row,s_col,locglob,ext):
    bands = glob.glob(os.path.join(landsatTemp,"*.dat"))
    meta = landsat_metadata(os.path.join(landsatTemp,'%s_MTL.txt' % sceneID))
    ulx = meta.CORNER_UL_PROJECTION_X_PRODUCT
    uly = meta.CORNER_UL_PROJECTION_Y_PRODUCT
    sw_res = meta.GRID_CELL_SIZE_REFLECTIVE
    th_res = meta.GRID_CELL_SIZE_THERMAL
    native_Thres = 90.
    nrows = meta.REFLECTIVE_LINES
    ncols = meta.REFLECTIVE_SAMPLES
    zone = meta.UTM_ZONE
    #filestem = os.path.join(landsatLAI,"lndsr_modlai_samples.combined_%s-%s" %(startDate,endDate))
    lstFN = os.path.join(landsatTemp,"lndsr.%s.band6.bin" % sceneID)
    sharpendFN = os.path.join(landsatTemp,"%s.%s_sharpened_%d_%d.%s" % (sceneID,locglob,s_row,s_col,ext))
    fn = os.path.join(landsatTemp,"dms_%d_%d.inp" % (s_row,s_col))
    file = open(fn, "w")
    file.write("# input file for Data Mining Sharpener\n")
    file.write("NFILES = 6\n")
    file.write("SW_FILE_NAME = %s %s %s %s %s %s\n" % (bands[1],bands[2],bands[3],bands[4],bands[5],bands[6]))
    file.write("SW_CLOUD_MASK = %s\n" % bands[0])
    file.write("SW_FILE_TYPE = binary\n")
    file.write("SW_CLOUD_TYPE = binary\n")
    file.write("SW_NROWS = %d\n" % nrows)
    file.write("SW_NCOLS = %d\n" % ncols)
    file.write("SW_PIXEL_SIZE = %f\n" % sw_res)
    file.write("SW_FILL_VALUE = -9999\n")
    file.write("SW_CLOUD_CODE = 1\n")
    file.write("SW_DATA_RANGE = -2000, 16000\n")
    file.write("SW_UPPER_LEFT_CORNER = %f %f\n" % (ulx,uly))
    file.write("SW_PROJECTION_CODE = 1\n")
    file.write("SW_PROJECTION_PARAMETERS = 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
    file.write("SW_PROJECTION_ZONE = %d\n" % zone)
    file.write("SW_PROJECTION_UNIT = 1\n")
    file.write("SW_PROJECTION_DATUM = 12\n")
     
    file.write("ORG_TH_FILE_NAME = %s\n" % lstFN)
    file.write("ORG_TH_FILE_TYPE = BINARY\n")
    file.write("ORG_TH_DATA_RANGE = 230., 370.\n")
    file.write("ORG_TH_PIXEL_SIZE = %f\n" % sw_res)
    file.write("ORG_NROWS = %d\n" % nrows)
    file.write("ORG_NCOLS = %d\n" % ncols)
    
    file.write("RES_TH_PIXEL_SIZE = %f \n" % native_Thres)
    
    file.write("PURE_CV_TH = 0.1\n")
    file.write("ZONE_SIZE = 240\n")
    file.write("SMOOTH_FLAG = 1\n")
    file.write("CUBIST_FILE_STEM = th_samples_%d_%d\n" % (s_row,s_col))
    file.write("OUT_FILE = %s\n" % sharpendFN)
    file.write("end")
    file.close()

def finalDMSinp(sceneID):
    bands = glob.glob(os.path.join(landsatTemp,"*.dat"))
    meta = landsat_metadata(os.path.join(landsatTemp,'%s_MTL.txt' % sceneID))
    ulx = meta.CORNER_UL_PROJECTION_X_PRODUCT
    uly = meta.CORNER_UL_PROJECTION_Y_PRODUCT
    sw_res = meta.GRID_CELL_SIZE_REFLECTIVE
    th_res = meta.GRID_CELL_SIZE_THERMAL
    nrows = meta.REFLECTIVE_LINES
    ncols = meta.REFLECTIVE_SAMPLES
    zone = meta.UTM_ZONE
    native_Thres = 90.
    #filestem = os.path.join(landsatLAI,"lndsr_modlai_samples.combined_%s-%s" %(startDate,endDate))
    lstFN = os.path.join(landsatTemp,"lndsr.%s.band6.bin" % sceneID)
    sharpendFN = os.path.join(landsatTemp,"%s.sharpened_band6.bin" % (sceneID))
    fn = os.path.join(landsatTemp,"dms.inp")
    file = open(fn, "w")
    file.write("# input file for Data Mining Sharpener")
    file.write("NFILES = 6")
    file.write("SW_FILE_NAME = %s %s %s %s %s %s" % (bands[1],bands[2],bands[3],bands[4],bands[5],bands[6]))
    file.write("SW_CLOUD_MASK = %s" % bands[0])
    file.write("SW_FILE_TYPE = binary")
    file.write("SW_CLOUD_TYPE = binary")
    file.write("SW_NROWS = %d" % nrows)
    file.write("SW_NCOLS = %d" % ncols)
    file.write("SW_PIXEL_SIZE = %f" % sw_res)
    file.write("SW_FILL_VALUE = -9999")
    file.write("SW_CLOUD_CODE = 1")
    file.write("SW_DATA_RANGE = -2000, 16000")
    file.write("SW_UPPER_LEFT_CORNER = %f %f" (ulx,uly))
    file.write("SW_PROJECTION_CODE = 1")
    file.write("SW_PROJECTION_PARAMETERS = 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0")
    file.write("SW_PROJECTION_ZONE = %d" % zone)
    file.write("SW_PROJECTION_UNIT = 1")
    file.write("SW_PROJECTION_DATUM = 12")
     
    file.write("ORG_TH_FILE_NAME = %s" % lstFN)
    file.write("ORG_TH_FILE_TYPE = BINARY")
    file.write("ORG_TH_DATA_RANGE = 230., 370.")
    file.write("ORG_TH_PIXEL_SIZE = %f" % sw_res)
    file.write("ORG_NROWS = %d" % nrows)
    file.write("ORG_NCOLS = %d" % ncols)
    
    file.write("RES_TH_PIXEL_SIZE = %f " % native_Thres)
    
    file.write("PURE_CV_TH = 0.1")
    file.write("ZONE_SIZE = 240")
    file.write("SMOOTH_FLAG = 1")
    file.write("CUBIST_FILE_STEM = th_samples")
    file.write("OUT_FILE = %s" % sharpendFN)
    file.write("end")
    file.close()    
def localPred(sceneID,th_res,s_row,s_col):

    wsize1 = 200
    overlap1 = 20
    
    wsize = int(wsize1*120/th_res)
    overlap = int(overlap1*120/th_res)
    
    e_row = s_row+wsize
    e_col = s_col+wsize
    os_row = s_row - overlap
    os_col = s_col - overlap
    oe_row = e_row +overlap
    oe_col = e_col + overlap
    perpareDMSinp(sceneID,s_row,s_col,"local","bin")
    dmsfn = os.path.join(landsatTemp,"dms_%d_%d.inp" % (s_row,s_col))
    # do cubist prediction
    subprocess.call(["get_samples","%s" % dmsfn,"%d" % os_row,"%d" % os_col,
    "%d" % oe_row,"%d" % oe_col])
    subprocess.call(["cubist","-f", "th_samples_%d_%d" % (s_row,s_col),"-u","-r","15"])
    subprocess.call(["predict_fineT","%s" % dmsfn,"%d" % s_row, "%d" % s_col, 
    "%d" % e_row, "%d" % e_col])

def getSharpenedLST(sceneID):
    meta = landsat_metadata(os.path.join(landsatTemp,'%s_MTL.txt' % sceneID))
    th_res = meta.GRID_CELL_SIZE_THERMAL
    nrows = meta.REFLECTIVE_LINES
    ncols = meta.REFLECTIVE_SAMPLES
    dmsfn = os.path.join(landsatTemp,"dms_0_0.inp")
    # create dms.inp
    perpareDMSinp(sceneID,0,0,"global","global")  
    # do global prediction
    subprocess.call(["get_samples","%s" % dmsfn])
    subprocess.call(["cubist","-f", "th_samples","-u","-r","30"])
    subprocess.call(["predict_fineT","%s" % dmsfn])
    # do local prediction
    njobs = -1
    wsize1 = 200
    wsize = int(wsize1*120/th_res)
    # process local parts in parallel
    Parallel(n_jobs=njobs, verbose=5)(delayed(localPred)(sceneID,th_res,s_row,s_col) for s_col in range(0,int(ncols/wsize),wsize) for s_row in range(0,int(nrows/wsize),wsize))
    # put the parts back together
    finalFile = os.path.join(landsatTemp,'%s.sharpened_band6.local' % sceneID)
    subprocess.call(["gdal_merge.py", "-o", "%s" % finalFile , "%s" % os.path.join(landsatTemp,'%s.local*' % sceneID)])
    shutil.copyfile(os.path.join(landsatTemp,'%s.sharpened_band6.global.hdr' % sceneID),os.path.join(landsatTemp,
    '%s.sharpened_band6.local.hdr' % sceneID))
    # combine the the local and global images
    finalDMSinp(sceneID)
    subprocess.call(["combine_models","dms.inp"])
    
    
 