# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import urllib2, base64
import os
from osgeo import gdal,osr

class earthDataHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
    

def getHTTPdata(url,outFN,auth):
    username = auth[0]
    password = auth[1]
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)  
    cookieprocessor = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(earthDataHTTPRedirectHandler, cookieprocessor)
    urllib2.install_opener(opener) 
    r = opener.open(request)
    result = r.read()
    
    with open(outFN, 'wb') as f:
        f.write(result)


def writeArray2Tiff(data,lats,lons,outfile):
    Projection = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    xres = lons[1] - lons[0]
    yres = lats[1] - lats[0]

    ysize = len(lats)
    xsize = len(lons)

    ulx = lons[0] #- (xres / 2.)
    uly = lats[0]# - (yres / 2.)
    driver = gdal.GetDriverByName('GTiff')
    ds = driver.Create(outfile, xsize, ysize, 1, gdal.GDT_Float32)
    
    srs = osr.SpatialReference()
    if isinstance(Projection, basestring):        
        srs.ImportFromProj4(Projection)
    else:
        srs.ImportFromEPSG(Projection)        
    ds.SetProjection(srs.ExportToWkt())
    
    gt = [ulx, xres, 0, uly, 0, yres ]
    ds.SetGeoTransform(gt)
    
    outband = ds.GetRasterBand(1)
    outband.WriteArray(data)    
    ds.FlushCache()  
    
    ds = None

def folders(base):
    inputDataBase = os.path.join(os.sep,'data','data123','chain','GETD_FINAL')
    dataBase = os.path.join(base,'data')
    landsatDataBase = os.path.join(dataBase,'Landsat-8')
    metBase = os.path.join(dataBase,'MET')
    if not os.path.exists(metBase):
        os.makedirs(metBase) 
    ALEXIbase = os.path.join(dataBase,'ALEXI')
    if not os.path.exists(ALEXIbase):
        os.makedirs(ALEXIbase) 
    resultsBase = os.path.join(base,'outputs')
    albedoBase = os.path.join(landsatDataBase,'albedo')
    if not os.path.exists(albedoBase):
        os.makedirs(albedoBase)   
    ndviBase = os.path.join(landsatDataBase,'ndvi')
    if not os.path.exists(ndviBase):
        os.makedirs(ndviBase)
    landsatSR = os.path.join(landsatDataBase,'SR')
    if not os.path.exists(landsatSR):
        os.makedirs(landsatSR)
    if not os.path.exists(resultsBase):
        os.makedirs(resultsBase)
    landsatBT = os.path.join(landsatDataBase,'BT')
    if not os.path.exists(landsatBT):
        os.makedirs(landsatBT)
    landsatLC = os.path.join(landsatDataBase,'LC')
    if not os.path.exists(landsatLC):
        os.makedirs(landsatLC)
    landsatLAI = os.path.join(landsatDataBase,'LAI')
    if not os.path.exists(landsatLAI):
        os.makedirs(landsatLAI)
    modisBase = os.path.join(base,'data','MODIS')
    if not os.path.exists(modisBase):
        os.mkdir(modisBase)
    out = {'dataBase':dataBase,'metBase':metBase,'inputDataBase':inputDataBase,
    'landsatBT':landsatBT,'ALEXIbase':ALEXIbase,'landsatDataBase':landsatDataBase,
    'resultsBase':resultsBase,'landsatLC':landsatLC,'albedoBase':albedoBase,
    'ndviBase':ndviBase,'landsatSR':landsatSR,'modisBase':modisBase,'landsatLAI':landsatLAI}
    return out

username = "mschull"
password = "sushmaMITCH12"
url = "https://e4ftl01.cr.usgs.gov/ASTT/AG100.003/2000.01.01/AG100.v003.-01.-037.0001.h5"    
auth = (username,password)
outFN = '/Users/mschull/umdGD/test3.h5'
getHTTPdata(url,outFN,auth)