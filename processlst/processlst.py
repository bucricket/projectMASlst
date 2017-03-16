#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 12 11:51:03 2017

@author: mschull
"""

import os
import glob
import subprocess
import sys
import pyrttov
import shutil
import urllib
import argparse
import pycurl
import keyring
import getpass
import wget
import ftplib
from .processData import Landsat,RTTOV
from .utils import folders,untar,getFile
from .lndlst_dms import getSharpenedLST


def runRTTOV(profileDict):
    nlevels = profileDict['P'].shape[1]
    nprofiles = profileDict['P'].shape[0]
    myProfiles = pyrttov.Profiles(nprofiles, nlevels)
    myProfiles.GasUnits = 2
    myProfiles.P = profileDict['P']
    myProfiles.T = profileDict['T']
    myProfiles.Q = profileDict['Q']
    myProfiles.Angles = profileDict['Angles']
    myProfiles.S2m = profileDict['S2m']
    myProfiles.Skin = profileDict['Skin']
    myProfiles.SurfType = profileDict['SurfType']
    myProfiles.SurfGeom =profileDict['SurfGeom']
    myProfiles.DateTimes = profileDict['Datetimes']
    month = profileDict['Datetimes'][0,1]

    # ------------------------------------------------------------------------
    # Set up Rttov instance
    # ------------------------------------------------------------------------

    # Create Rttov object for the TIRS instrument

    tirsRttov = pyrttov.Rttov()
    nchan_tirs = 1

    # Set the options for each Rttov instance:
    # - the path to the coefficient file must always be specified
    # - specify paths to the emissivity and BRDF atlas data in order to use
    #   the atlases (the BRDF atlas is only used for VIS/NIR channels so here
    #   it is unnecessary for HIRS or MHS)
    # - turn RTTOV interpolation on (because input pressure levels differ from
    #   coefficient file levels)
    # - set the verbose_wrapper flag to true so the wrapper provides more
    #   information
    # - enable solar simulations for SEVIRI
    # - enable CO2 simulations for HIRS (the CO2 profiles are ignored for
    #   the SEVIRI and MHS simulations)
    # - enable the store_trans wrapper option for MHS to provide access to
    #   RTTOV transmission structure
    p = subprocess.Popen(["conda", "info", "--root"],stdout=subprocess.PIPE)
    out = p.communicate()
    condaPath = out[0][:-1]
    s = pyrttov.__file__
    envPath = os.sep.join(s.split(os.sep)[:-6])
    #rttovPath = os.path.join(condaPath,'share','rttov113')
    rttovPath = os.path.join(envPath,'share')
    rttovCoeffPath = os.path.join(rttovPath,'rttov')
    rttovAtlasPath = os.path.join(rttovPath,'rttov_atlas')
#    rttovBRDFPath = os.path.join(rttovPath,'brdf_data')
#    base = os.getcwd()
    if not os.path.exists(rttovAtlasPath):
        ftp = ftplib.FTP("ftp.star.nesdis.noaa.gov")
        ftp.login("anonymous", "")
         
        ftp.cwd('/pub/smcd/emb/mschull/')         # change directory to /pub/
        getFile(ftp,'rttov_atlas.tar')
         
        ftp.quit()
        untar('rttov_atlas.tar',rttovPath)
#        print(" go to https://nwpsaf.eu/site/software/rttov/download/#Emissivity_BRDF_atlas_data")
#        print(" download and untar the emissivity and brdf data into %s" % rttovPath )
#        print(" Then run the script again")
#        os.makedirs(rttovEmisPath)
#        os.makedirs(rttovBRDFPath) 
##        sys.exit()
#        #======download, untar and move atlases and coefficients=======================
#        url ='https://nwpsaf.eu/downloads/emis_data/uw_ir_emis_atlas_hdf5.tar'
#        download_file(url)
##        attempts =0
##        while attempts < 10:
##            try:
##                wget.download('https://nwpsaf.eu/downloads/emis_data/uw_ir_emis_atlas_hdf5.tar')
##                break
##            except :
##                attempts += 1
#        untar('uw_ir_emis_atlas_hdf5.tar',rttovEmisPath)
##        source = os.listdir(base)
##        for files in source:
##            if files.endswith('.H5'):
##                shutil.move(os.path.join(base,files), os.path.join(rttovEmisPath,files))
#        url = 'https://nwpsaf.eu/downloads/emis_data/uw_ir_emis_atlas_covariances_hdf5.tar'     
#        download_file(url)
##        attempts =0
##        while attempts < 5:
##            try:        
##                wget.download('https://nwpsaf.eu/downloads/emis_data/uw_ir_emis_atlas_covariances_hdf5.tar')
##                break
##            except :
##                attempts += 1
#        untar('uw_ir_emis_atlas_covariances_hdf5.tar',rttovEmisPath)
##        source = os.listdir(base)
##        for files in source:
##            if files.endswith('.H5'):
##                shutil.move(os.path.join(base,files), os.path.join(rttovEmisPath,files))
#                
##        wget.download('https://nwpsaf.eu/downloads/emis_data/uw_ir_emis_atlas_angcorr_hdf5.tar')
#        url = 'https://nwpsaf.eu/downloads/emis_data/uw_ir_emis_atlas_angcorr_hdf5.tar'
#        download_file(url)
#        untar('uw_ir_emis_atlas_angcorr_hdf5.tar',rttovEmisPath)
##        source = os.listdir(base)
##        for files in source:
##            if files.endswith('.H5'):
##                shutil.move(os.path.join(base,files), os.path.join(rttovEmisPath,files))
#        #=========BRDF=================================================================
#        url = 'https://nwpsaf.eu/site/download/rttov_downloads/brdf_data/cms_brdf_atlas_hdf5.tar'
#        download_file(url)
##        attempts =0
##        while attempts < 5:
##            try:     
##                wget.download('https://nwpsaf.eu/site/download/rttov_downloads/brdf_data/cms_brdf_atlas_hdf5.tar')
##                break
##            except :
##                attempts += 1
#        untar('cms_brdf_atlas_hdf5.tar',rttovBRDFPath)
##        source = os.listdir(base)
##        for files in source:
##            if files.endswith('.H5'):
##                shutil.move(os.path.join(base,files), os.path.join(rttovBRDFPath,files))
            
    tirsRttov.FileCoef = '{}/{}'.format(rttovCoeffPath,"rtcoef_landsat_8_tirs.dat")
    
    #tirsRttov.EmisAtlasPath = os.path.join(base,'ALEXIdisALEXIfusion','rttov113','emis_data')
    tirsRttov.EmisAtlasPath = '{}/{}'.format(rttovAtlasPath, "emis_data")
    print "%s" % tirsRttov.EmisAtlasPath
    tirsRttov.BrdfAtlasPath = '{}/{}'.format(rttovAtlasPath, "brdf_data")
    #tirsRttov.BrdfAtlasPath = os.path.join(base,'ALEXIdisALEXIfusion','rttov113','brdf_data')

    tirsRttov.Options.AddInterp = True
    tirsRttov.Options.StoreTrans = True
    tirsRttov.Options.StoreRad2 = True
    tirsRttov.Options.VerboseWrapper = True


    # Load the instruments:

    try:
        tirsRttov.loadInst()
    except pyrttov.RttovError as e:
        sys.stderr.write("Error loading instrument(s): {!s}".format(e))
        sys.exit(1)

    # Associate the profiles with each Rttov instance
    tirsRttov.Profiles = myProfiles
    # ------------------------------------------------------------------------
    # Load the emissivity and BRDF atlases
    # ------------------------------------------------------------------------

    # Load the emissivity and BRDF atlases:
    # - load data for August (month=8)
    # - note that we only need to load the IR emissivity once and it is
    #   available for both SEVIRI and HIRS: we could use either the seviriRttov
    #   or hirsRttov object to do this
    # - for the BRDF atlas, since SEVIRI is the only VIS/NIR instrument we can
    #   use the single-instrument initialisation

    tirsRttov.irEmisAtlasSetup(month)
    # ------------------------------------------------------------------------
    # Call RTTOV
    # ------------------------------------------------------------------------

    # Since we want the emissivity/reflectance to be calculated, the
    # SurfEmisRefl attribute of the Rttov objects are left uninitialised:
    # That way they will be automatically initialise to -1 by the wrapper

    # Call the RTTOV direct model for each instrument:
    # no arguments are supplied to runDirect so all loaded channels are
    # simulated
    try:
        tirsRttov.runDirect()
    except pyrttov.RttovError as e:
        sys.stderr.write("Error running RTTOV direct model: {!s}".format(e))
        sys.exit(1)
        
    return tirsRttov

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("earthLoginUser", type=str, help="earthLoginUser")
    parser.add_argument("earthLoginPass", type=str, help="earthLoginPass")
    args = parser.parse_args()
    earthLoginUser = args.earthLoginUser
    earthLoginPass = args.earthLoginPass
         # =====earthData credentials===============
    if earthLoginUser == None:
        earthLoginUser = str(getpass.getpass(prompt="earth login username:"))
        if keyring.get_password("nasa",earthLoginUser)==None:
            earthLoginPass = str(getpass.getpass(prompt="earth login password:"))
            keyring.set_password("nasa",earthLoginUser,earthLoginPass)
        else:
            earthLoginPass = str(keyring.get_password("nasa",earthLoginUser)) 

    base = os.getcwd()    
    Folders = folders(base)    
    landsatLST = Folders['landsatLST']
    landsatTemp = Folders['landsatTemp']   
    landsatDataBase = Folders['landsatDataBase'] 
    sceneIDlist = glob.glob(os.path.join(landsatTemp,'*.xml'))


    # ------------------------------------------------------------------------
    # Set up the profile data
    # ------------------------------------------------------------------------
    for i in xrange(len(sceneIDlist)):
        inFN = sceneIDlist[i]
        landsat = Landsat(inFN,username = earthLoginUser,
                          password = earthLoginPass)
        rttov = RTTOV(inFN,username = earthLoginUser,
                          password = earthLoginPass)
        lstFolder = os.path.join(landsatLST,landsat.scene)
        tifFile = os.path.join(landsatTemp,'%s_lst.tiff'% landsat.sceneID)
        binFile = os.path.join(landsatTemp,"lndsr."+landsat.sceneID+".cband6.bin")
        if not os.path.exists(tifFile):
            profileDict = rttov.preparePROFILEdata()
            tiirsRttov = runRTTOV(profileDict)
            landsat.processLandsatLST(tiirsRttov,profileDict)

        
            
        subprocess.call(["gdal_translate","-of", "ENVI", "%s" % tifFile, "%s" % binFile])
        #subprocess.call(["GeoTiff2ENVI","%s" % tifFile, "%s" % binFile])
        #=====sharpen the corrected LST==========================================
        #subprocess.call(["lndlst_dms3_sa.csh","%s" % landsatTemp])
        landsat = Landsat(inFN,username = earthLoginUser,
                              password = earthLoginPass)
        getSharpenedLST(landsat.sceneID)
    
    #=====move files to their respective directories and remove temp
    for i in xrange(len(sceneIDlist)):
        inFN = sceneIDlist[i]
        landsat = Landsat(inFN,username = earthLoginUser,
                          password = earthLoginPass)
        sharpenedSceneDir = os.path.join(landsatDataBase,'LST',landsat.scene)
        if not os.path.exists(sharpenedSceneDir):
            os.mkdir(sharpenedSceneDir)
        binFN = os.path.join(landsatTemp,'%s.sharpened_band6.bin' % landsat.sceneID)
        tifFN = os.path.join(sharpenedSceneDir,'%s_lstSharp.tiff' % landsat.sceneID)
        subprocess.call(["gdal_translate", "-of","GTiff","%s" % binFN,"%s" % tifFN]) 


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, pycurl.error):
        exit('Received Ctrl + C... Exiting! Bye.', 1)   