#!/usr/bin/env python

"""
setup.py file for atbr
"""

# relevant doc for setuptools
# http://docs.python.org/distutils/setupscript.html
# http://docs.python.org/distutils/apiref.html

from distutils.core import setup, Extension
from distutils.sysconfig import get_config_vars
import os

python_version = "2.6"

os.environ['CC'] = 'g++'
#os.environ['CC'] = 'c++'
os.environ['CXX'] = 'g++'
os.environ['CPP'] = 'g++'
os.environ['LDSHARED'] = 'g++'

#print os.environ.keys()
#print os.environ.values()

# remove erranous default parameter Wstrict-prototypes
(opt,) = get_config_vars('OPT')
os.environ['OPT'] = " ".join(
    flag for flag in opt.split() if flag != '-Wstrict-prototypes'
)

setup( 
    name = "atbr",
    author = 'Amund Tveit', 
    author_email = 'amund@atbrox.com',
    description = ("low-latency and memory-efficient key-value store"),
    version = "0.22", 
    licence = "Apache",
    url = "http://atbr.atbrox.com",
    ext_modules = [ 
        Extension( 
            "atbr._atbr",
            sources = ["atbr/atbrpy.i"],
            swig_opts=["-Wall","-c++"],
            libraries=['python%s' % (python_version)],
            include_dirs = ['/usr/include/python%s' % (python_version)],
    #        extra_compile_args = ['-std=c++0x','-Wself-assign','-Wunused-variable'],
            extra_compile_args = ['-std=c++0x','-DSPARSE_MAP'],
            extra_link_args = ['-shared', '-lrt'],
            language=["c++"]
            ),
        ],
    packages=['atbr', 'atbrserver']
    )
