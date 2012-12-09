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

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

python_version = 2.6
os.environ['CC'] = 'g++'
os.environ['CXX'] = 'g++'
os.environ['CPP'] = 'g++'
os.environ['LDSHARED'] = 'g++'
extra_compile_args = ['-std=c++0x','-DSPARSE_MAP']
extra_link_args = ['-shared', '-lrt']

#print os.uname()

if "Darwin" in os.uname()[0]:
    python_version = "2.7"
    os.environ['CC'] = 'c++'
    os.environ['CXX'] = 'c++'
    os.environ['CPP'] = 'c++'
    os.environ['LDSHARED'] = 'c++'
    extra_compile_args = ['-std=c++0x']
    extra_link_args = ['-shared']
    

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
    long_description=read('FEATURES'),
    version = "0.31", 
    license = "Apache License 2.0",
    url = "http://atbr.atbrox.com",
    ext_modules = [ 
        Extension( 
            "atbr._atbr",
            sources = ["atbr/atbrpy.i"],
            swig_opts=["-Wall","-c++"],
            libraries=['python%s' % (python_version)],
            include_dirs = ['/usr/include/python%s' % (python_version)],
    #        extra_compile_args = ['-std=c++0x','-Wself-assign','-Wunused-variable'],
            extra_compile_args = extra_compile_args,
            extra_link_args = extra_link_args,
            language=["c++"]
            ),
        ],
    packages=['atbr'] # , 'atbrserver', 'atbrthrift','atbrtst','atbrtst.builder','atbrtst.client']
    )
