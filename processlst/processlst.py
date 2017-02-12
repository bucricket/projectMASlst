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
from .processData import Landsat,RTTOV
from .utils import folders,untar


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
    rttovPath = os.path.join(condaPath,'share','rttov113')
    rttovCoefPath = os.path.join(rttovPath,'rtcoef_rttov11')
    if not os.path.exists(rttovCoefPath):
        base = os.getcwd()
        # ========download coefficents
        os.makedirs(rttovCoefPath) 
        shutil.copyfile("./rttov_coeff_download.sh",os.path.join(rttovCoefPath,"rttov_coeff_download.sh"))
        os.chdir(rttovCoefPath)
        subprocess(['rttov_coeff_download.sh'])
        # ========download and untar emis atlas    
        
        rttovEmisPath = os.path.join(rttovPath,'emis_data')
        downfile = urllib.URLopener()
        downfile.urlretrieve('http://nwpsaf.eu/downloads/emis_data/uw_ir_emis_atlas_rttov11_hdf5.tar', 
                             os.path.join(rttovEmisPath,'uw_ir_emis_atlas_rttov11_hdf5.tar'))
        os.chdir(rttovEmisPath)
        untar(os.path.join(rttovEmisPath,'uw_ir_emis_atlas_rttov11_hdf5.tar'),
              os.path.join(rttovEmisPath,'uw_ir_emis_atlas_rttov11_hdf5'))
    
        # =========download and untar BRDF atlas        
        rttovBRDFPath = os.path.join(rttovPath,'brdf_data')
        downfile = urllib.URLopener()
        downfile.urlretrieve('http://nwpsaf.eu/downloads/brdf_data/cms_brdf_atlas_hdf5.tar', 
                             os.path.join(rttovBRDFPath,'cms_brdf_atlas_hdf5.tar'))
        os.chdir(rttovBRDFPath)
        untar(os.path.join(rttovBRDFPath,'cms_brdf_atlas_hdf5.tar'),
        os.path.join(rttovBRDFPath,'cms_brdf_atlas_hdf5'))
        #change back to the base directory
        os.chdir(base)
        
    
    tirsRttov.FileCoef = '{}/{}'.format(rttovPath,
                                       "rtcoef_rttov11/rttov7pred54L/rtcoef_landsat_8_tirs.dat")
    
    #tirsRttov.EmisAtlasPath = os.path.join(base,'ALEXIdisALEXIfusion','rttov113','emis_data')
    tirsRttov.EmisAtlasPath = '{}/{}'.format(rttovPath, "emis_data")
    print "%s" % tirsRttov.EmisAtlasPath
    tirsRttov.BrdfAtlasPath = '{}/{}'.format(rttovPath, "brdf_data")
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

if __name__ == '__main__':
    
    base = os.getcwd()    
    Folders = folders(base)    
    landsatLST = Folders['landsatLST']
    landsatTemp = Folders['landsatTemp']    
    sceneIDlist = glob.glob(os.path.join(landsatTemp,'*toa*'))


    # ------------------------------------------------------------------------
    # Set up the profile data
    # ------------------------------------------------------------------------
    for i in xrange(len(sceneIDlist)):
        inFN = sceneIDlist[i]
        landsat = Landsat(inFN)
        rttov = RTTOV(inFN)
        lstFolder = os.path.join(landsatLST,landsat.scene)
        tifFile = os.path.join(lstFolder,'%s_lst.tiff'% landsat.sceneID)
        binFile = os.path.join(lstFolder,"lndsr."+landsat.sceneID+".cband6.bin")
        if os.path.exists(tifFile):
            profileDict = rttov.preparePROFILEdata()
            tiirsRttov = runRTTOV(profileDict)
            landsat.processLandsatLST(tiirsRttov,profileDict)

        
            
        subprocess.call(["gdal_translate","-of", "ENVI", "%s" % tifFile, "%s" % binFile])