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

#os.environ['CC'] = 'g++'
os.environ['CC'] = 'c++'
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
    version = "0.31", 
    ext_modules = [ 
        Extension( 
            "atbr._atbr",
            sources = ["atbr/atbrpy.i"],
            swig_opts=["-Wall","-c++"],
            libraries=['python2.7'],
            include_dirs = ['/usr/include/python2.7'],
            extra_compile_args = ['-std=c++0x','-Wself-assign','-Wunused-variable'],
            extra_link_args = ['-shared'],
            language=["c++"]
            ),
        Extension( 
            "atbrtst._atbrtst",
            sources = ["atbrtst/atbrtstpy.i"],
            swig_opts=["-Wall","-c++"],
            libraries=['python2.7'],
            include_dirs = ['/usr/include/python2.7'],
            #extra_compile_args = ['--std=c++11','-Wself-assign','-Wunused-variable','-Wc++11-extensions','--stdlib=libc++'],
            extra_compile_args = ['-std=c++0x','-Wself-assign','-Wunused-variable'],
            extra_link_args = ['-shared'],
            language=["c++"]
            ),
        ],
    packages=['atbr', 'atbrserver', 'atbrtst']
    )
