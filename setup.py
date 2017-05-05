#!/usr/bin/env python

from __future__ import print_function
import subprocess
import os, stat
import shutil

# set project base directory structure
base = os.getcwd()
    
try:
    from setuptools import setup
    setup_kwargs = {'entry_points': {'console_scripts':['processlst=processlst.processlst:main']}}
except ImportError:
    from distutils.core import setup
    setup_kwargs = {'scripts': ['bin/processlst']}
    
from processlst import __version__

#=====build DMS binaries===============================
# get Anaconda root location
p = subprocess.Popen(["conda", "info", "--root"],stdout=subprocess.PIPE)
out = p.communicate()
condaPath = out[0][:-1]

prefix  = os.environ.get('PREFIX')
processDi = os.path.abspath(os.path.join(prefix,os.pardir))
processDir = os.path.join(processDi,'work')
srcDir = os.path.join(processDir,'source')

#shutil.copyfile(os.path.join(srcDir,'prepareDMS3_sa.csh'),os.path.join(prefix,'bin','prepareDMS3_sa.csh'))
#shutil.copyfile(os.path.join(srcDir,'lndlst_dms3_sa.csh'),os.path.join(prefix,'bin','lndlst_dms3_sa.csh'))
#os.chmod(os.path.join(prefix,'bin','prepareDMS3_sa.csh'), stat.S_IREAD | stat.S_IEXEC)
#os.chmod(os.path.join(prefix,'bin','lndlst_dms3_sa.csh'), stat.S_IREAD | stat.S_IEXEC)
#=============setup the python scripts============================



setup(
    name="projectmaslst",
    version=__version__,
    description="prepare LST data for input to pyDisALEXI",
    author="Mitchell Schull",
    author_email="mitch.schull@noaa.gov",
    url="https://github.com/bucricket/projectMASlst.git",
    py_modules=['processlst.processlst','processlst.utils',
            'processlst.lnd_dms','processlst.landsatTools',
            'processlst.processData'],
#    packages= ['processlst'],
    platforms='Posix; MacOS X; Windows',
    license='BSD 3-Clause',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        # Uses dictionary comprehensions ==> 2.7 only
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: GIS',
    ],  
    **setup_kwargs
)

