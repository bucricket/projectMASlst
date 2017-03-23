#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 14:03:53 2017

@author: mschull
"""
import os
from osgeo import gdal
import numpy as np
from sklearn.tree import DecisionTreeRegressor
import pandas as pd
from .utils import folders,writeArray2Envi,clean
from .landsatTools import landsat_metadata, GeoTIFF
import subprocess
from joblib import Parallel, delayed
import shutil

base = os.getcwd()
Folders = folders(base)   
landsatSR = Folders['landsatSR']
landsatTemp = Folders['landsatTemp']
landsatLST = Folders['landsatLST']
# global prediction


def perpareDMSinp(sceneID,s_row,s_col,locglob,ext):
    blue = os.path.join(landsatTemp,"%s_sr_band2.blue.dat" % sceneID)
    green = os.path.join(landsatTemp,"%s_sr_band3.green.dat" % sceneID)
    red = os.path.join(landsatTemp,"%s_sr_band4.red.dat" % sceneID)
    nir = os.path.join(landsatTemp,"%s_sr_band5.nir.dat" % sceneID)
    swir1 = os.path.join(landsatTemp,"%s_sr_band6.swir1.dat" % sceneID)
    swir2 = os.path.join(landsatTemp,"%s_sr_band7.swir2.dat" % sceneID)
    cloud = os.path.join(landsatTemp,"%s_cfmask.cloud.dat" % sceneID)
    meta = landsat_metadata(os.path.join(landsatTemp,'%s_MTL.txt' % sceneID))
    sw_res = meta.GRID_CELL_SIZE_REFLECTIVE
    ulx = meta.CORNER_UL_PROJECTION_X_PRODUCT-(sw_res*0.5)
    uly = meta.CORNER_UL_PROJECTION_Y_PRODUCT+(sw_res*0.5)
    if sceneID[2]=="5":
        native_Thres = 120
    elif sceneID[2]=="7":
        native_Thres = 60
    else:
        native_Thres = 90
        
    nrows = meta.REFLECTIVE_LINES
    ncols = meta.REFLECTIVE_SAMPLES
    zone = meta.UTM_ZONE
    #filestem = os.path.join(landsatLAI,"lndsr_modlai_samples.combined_%s-%s" %(startDate,endDate))
    lstFN = os.path.join(landsatTemp,"lndsr.%s.cband6.bin" % sceneID)
    sharpendFN = os.path.join(landsatTemp,"%s.%s_sharpened_%d_%d.%s" % (sceneID,locglob,s_row,s_col,ext))
    #fn = os.path.join(landsatTemp,"dms_%d_%d.inp" % (s_row,s_col))
    fn = "dms_%d_%d.inp" % (s_row,s_col)
    file = open(fn, "w")
    file.write("# input file for Data Mining Sharpener\n")
    file.write("NFILES = 6\n")
    file.write("SW_FILE_NAME = %s %s %s %s %s %s\n" % (blue,green,red,nir,swir1,swir2))
    file.write("SW_CLOUD_MASK = %s\n" % cloud)
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

def finalDMSinp(sceneID,ext):
    blue = os.path.join(landsatTemp,"%s_sr_band2.blue.dat" % sceneID)
    green = os.path.join(landsatTemp,"%s_sr_band3.green.dat" % sceneID)
    red = os.path.join(landsatTemp,"%s_sr_band4.red.dat" % sceneID)
    nir = os.path.join(landsatTemp,"%s_sr_band5.nir.dat" % sceneID)
    swir1 = os.path.join(landsatTemp,"%s_sr_band6.swir1.dat" % sceneID)
    swir2 = os.path.join(landsatTemp,"%s_sr_band7.swir2.dat" % sceneID)
    cloud = os.path.join(landsatTemp,"%s_cfmask.cloud.dat" % sceneID)
    meta = landsat_metadata(os.path.join(landsatTemp,'%s_MTL.txt' % sceneID))
    sw_res = meta.GRID_CELL_SIZE_REFLECTIVE
    ulx = meta.CORNER_UL_PROJECTION_X_PRODUCT-(sw_res*0.5)
    uly = meta.CORNER_UL_PROJECTION_Y_PRODUCT+(sw_res*0.5)
    nrows = meta.REFLECTIVE_LINES
    ncols = meta.REFLECTIVE_SAMPLES
    zone = meta.UTM_ZONE
    if sceneID[2]=="5":
        native_Thres = 120
    elif sceneID[2]=="7":
        native_Thres = 60
    else:
        native_Thres = 90
    #filestem = os.path.join(landsatLAI,"lndsr_modlai_samples.combined_%s-%s" %(startDate,endDate))
    lstFN = os.path.join(landsatTemp,"lndsr.%s.cband6.bin" % sceneID)
    sharpendFN = os.path.join(landsatTemp,"%s.sharpened_band6.%s" % (sceneID,ext))
    fn = os.path.join(landsatTemp,"dms.inp")
    fn = "dms.inp"
    file = open(fn, "w")
    file.write("# input file for Data Mining Sharpener\n")
    file.write("NFILES = 6\n")
    file.write("SW_FILE_NAME = %s %s %s %s %s %s\n" % (blue,green,red,nir,swir1,swir2))
    file.write("SW_CLOUD_MASK = %s\n" % cloud)
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
    file.write("CUBIST_FILE_STEM = th_samples\n")
    file.write("OUT_FILE = %s\n" % sharpendFN)
    file.write("end")
    file.close()    
def localPred(sceneID,th_res,s_row,s_col):

    wsize1 = 200
    overlap1 = 20
    
    wsize = int((wsize1*120)/th_res)
    overlap = int((overlap1*120)/th_res)
    
    e_row = s_row+wsize
    e_col = s_col+wsize
    os_row = s_row - overlap
    os_col = s_col - overlap
    oe_row = e_row +overlap
    oe_col = e_col + overlap
    perpareDMSinp(sceneID,s_row,s_col,"local","bin")
    #dmsfn = os.path.join(landsatTemp,"dms_%d_%d.inp" % (s_row,s_col))
    dmsfn = "dms_%d_%d.inp" % (s_row,s_col)
    # do cubist prediction
    subprocess.call(["get_samples","%s" % dmsfn,"%d" % os_row,"%d" % os_col,
    "%d" % oe_row,"%d" % oe_col])
    subprocess.call(["cubist","-f", "th_samples_%d_%d" % (s_row,s_col),"-u","-r","15"])
    subprocess.call(["predict_fineT","%s" % dmsfn,"%d" % s_row, "%d" % s_col, 
    "%d" % e_row, "%d" % e_col])
    
def globalPredSK(sceneID):
    base = os.getcwd()
    regr_1 = DecisionTreeRegressor(max_depth=30)
    fn = os.path.join(base,'th_samples.data')
    df = pd.read_csv(fn)
    X = np.array(df.iloc[:,3:-4])
    y = np.array(df.iloc[:,-2])
    regr_1.fit(X,y)
    blue = os.path.join(landsatTemp,"%s_sr_band2.tif" % sceneID)
    green = os.path.join(landsatTemp,"%s_sr_band3.tif" % sceneID)
    red = os.path.join(landsatTemp,"%s_sr_band4.tif" % sceneID)
    nir = os.path.join(landsatTemp,"%s_sr_band5.tif" % sceneID)
    swir1 = os.path.join(landsatTemp,"%s_sr_band6.tif" % sceneID)
    swir2 = os.path.join(landsatTemp,"%s_sr_band7.tif" % sceneID)
    # open files and assepble them into 2-d numpy array
    
    Gblue = gdal.Open(blue)
    blueData = Gblue.ReadAsArray()
    blueVec = np.reshape(blueData,[blueData.shape[0]*blueData.shape[1]])
    Ggreen = gdal.Open(green)
    greenData = Ggreen.ReadAsArray()
    greenVec = np.reshape(greenData,[greenData.shape[0]*greenData.shape[1]])
    Gnir = gdal.Open(nir)
    nirData = Gnir.ReadAsArray()
    nirVec = np.reshape(nirData,[nirData.shape[0]*nirData.shape[1]])
    Gred = gdal.Open(red)
    redData = Gred.ReadAsArray()
    redVec = np.reshape(redData,[redData.shape[0]*redData.shape[1]])
    Gswir1 = gdal.Open(swir1)
    swir1Data = Gswir1.ReadAsArray()
    swir1Vec = np.reshape(swir1Data,[swir1Data.shape[0]*swir1Data.shape[1]])
    Gswir2 = gdal.Open(swir2)
    swir2Data = Gswir2.ReadAsArray()
    swir2Vec = np.reshape(swir2Data,[swir2Data.shape[0]*swir2Data.shape[1]])

    xNew = np.stack((greenVec,redVec,nirVec,swir1Vec,swir2Vec), axis=-1)
    outData = regr_1.predict(xNew)
    
    return np.reshape(outData,[blueData.shape[0],blueData.shape[1]])

def localPredSK(sceneID,th_res,s_row,s_col):

    wsize1 = 200
    overlap1 = 20
    
    wsize = int((wsize1*120)/th_res)
    overlap = int((overlap1*120)/th_res)
    
    e_row = s_row+wsize
    e_col = s_col+wsize
    os_row = s_row - overlap
    os_col = s_col - overlap
    oe_row = e_row +overlap
    oe_col = e_col + overlap
    perpareDMSinp(sceneID,s_row,s_col,"local","bin")
    #dmsfn = os.path.join(landsatTemp,"dms_%d_%d.inp" % (s_row,s_col))
    dmsfn = "dms_%d_%d.inp" % (s_row,s_col)
    # do cubist prediction
    subprocess.call(["get_samples","%s" % dmsfn,"%d" % os_row,"%d" % os_col,
    "%d" % oe_row,"%d" % oe_col])
    localPred = globalPredSK(sceneID)
    subprocess.call(["cubist","-f", "th_samples_%d_%d" % (s_row,s_col),"-u","-r","15"])
    subprocess.call(["predict_fineT","%s" % dmsfn,"%d" % s_row, "%d" % s_col, 
    "%d" % e_row, "%d" % e_col])
    return localPred
    
def getSharpenedLST(sceneID):
    meta = landsat_metadata(os.path.join(landsatTemp,'%s_MTL.txt' % sceneID))
    sw_res = meta.GRID_CELL_SIZE_REFLECTIVE
    ulx = meta.CORNER_UL_PROJECTION_X_PRODUCT-(sw_res*0.5)
    uly = meta.CORNER_UL_PROJECTION_Y_PRODUCT+(sw_res*0.5)
    xres = meta.GRID_CELL_SIZE_REFLECTIVE
    yres = meta.GRID_CELL_SIZE_REFLECTIVE   
    ls = GeoTIFF(os.path.join(landsatTemp,'%s_sr_band1.tif' % sceneID))
    th_res = meta.GRID_CELL_SIZE_THERMAL
    if sceneID[2]=="5":
        th_res = 120
    elif sceneID[2]=="7":
        th_res = 60
    else:
        th_res = 90
    scale = int(th_res/meta.GRID_CELL_SIZE_REFLECTIVE)
    nrows = int(meta.REFLECTIVE_LINES/scale)
    ncols = int(meta.REFLECTIVE_SAMPLES/scale)
    #dmsfn = os.path.join(landsatTemp,"dms_0_0.inp")
    dmsfn = "dms.inp"
    # create dms.inp
    print("========GLOBAL PREDICTION===========")
    finalDMSinp(sceneID,"global")  
    # do global prediction
    subprocess.call(["get_samples","%s" % dmsfn])
    #subprocess.call(["cubist","-f", "th_samples","-u","-r","30"])
    #subprocess.call(["predict_fineT","%s" % dmsfn])
    #===========EXPERIMENTAL===========
    globFN = os.path.join(landsatTemp,"%s.sharpened_band6.global" % sceneID)
    globalData = globalPredSK(sceneID)
    writeArray2Envi(globalData,ulx,uly,xres,yres,ls.proj4,globFN)
    # do local prediction
    print("========LOCAL PREDICTION===========")
    njobs = -1
    wsize1 = 200
    wsize = int((wsize1*120)/th_res)
    # process local parts in parallel
    Parallel(n_jobs=njobs, verbose=5)(delayed(localPred)(sceneID,th_res,s_row,s_col) for s_col in range(0,int(ncols/wsize)*wsize,wsize) for s_row in range(0,int(nrows/wsize)*wsize,wsize))
    # put the parts back together
    finalFile = os.path.join(landsatTemp,'%s.sharpened_band6.local' % sceneID)
    tifFile = os.path.join(landsatTemp,'%s_lstSharp.tiff' % sceneID)
    globFN = os.path.join(landsatTemp,"%s.sharpened_band6.global" % sceneID)
    Gg = gdal.Open(globFN)
    globalData = Gg.ReadAsArray()
    for s_col in range(0,int(ncols/wsize)*wsize,wsize): 
        for s_row in range(0,int(nrows/wsize)*wsize,wsize):
            fn = os.path.join(landsatTemp,"%s.local_sharpened_%d_%d.bin" %(sceneID,s_row,s_col))
            if os.path.exists(fn):
                Lg = gdal.Open(fn)
                globalData[0,s_row*scale:s_row*scale+wsize*scale+1,s_col*scale:s_col*scale+wsize*scale+1] = Lg.ReadAsArray(s_col*scale,s_row*scale,wsize*scale+1,wsize*scale+1)[0]
    writeArray2Envi(globalData,ulx,uly,xres,yres,ls.proj4,finalFile)
      
    #subprocess.call(["gdal_merge.py", "-o", "%s" % finalFile , "%s" % os.path.join(landsatTemp,'%s.local*' % sceneID)])
    # combine the the local and global images
    finalDMSinp(sceneID,"bin")
    subprocess.call(["combine_models","dms.inp"])
    # convert from ENVI to geoTIFF
    fn = os.path.join(landsatTemp,"%s.sharpened_band6.bin" % sceneID)
    g = gdal.Open(fn)
    data = g.ReadAsArray()[1]
    ls.clone(tifFile,data)
    
    # copy files to their proper places
    scenePath = os.path.join(landsatLST,sceneID[3:9])
    if not os.path.exists(scenePath):
        os.mkdir(scenePath)
    shutil.copyfile(tifFile ,os.path.join(scenePath,tifFile.split(os.sep)[-1]))
    
    # cleaning up    
    clean(landsatTemp,"%s.local_sharpened" % sceneID)
    clean(landsatTemp,"%s.sharpened" % sceneID)
    clean(base,"th_samples")
    clean(base,"dms")
    
    
    
    
 