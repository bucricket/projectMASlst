#!/usr/bin/env python

from __future__ import print_function
import subprocess
import os

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


#=============setup the python scripts============================



setup(
    name="projectmaslst",
    version=__version__,
    description="prepare LST data for input to pyDisALEXI",
    author="Mitchell Schull",
    author_email="mitch.schull@noaa.gov",
    url="https://github.com/bucricket/projectMASlst.git",
    packages= ['processlst'],
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

