#!/usr/bin/env python

"""
setup.py file for atbr
"""

# relevant doc for setuptools
# http://docs.python.org/distutils/setupscript.html
# http://docs.python.org/distutils/apiref.html

from distutils.core import setup, Extension
import os

os.environ['CC'] = 'g++'
os.environ['CXX'] = 'g++'
os.environ['CPP'] = 'g++'
os.environ['LDSHARED'] = 'g++'

setup( 
    name = "atbr",
    author = 'Amund Tveit', 
    author_email = 'amund@atbrox.com',
    version = "0.1", 
    ext_modules = [ 
        Extension( 
            "_atbr",
            #sources = ["atbrpy.i","atbrpy_wrap.cpp"],
            sources = ["atbrpy.i"],
            swig_opts=["-Wall","-c++"],
            libraries=['rt','python2.6'],
            include_dirs = ['/usr/include/python2.6'],
            extra_compile_args = ['-std=c++0x'],
            extra_link_args = ['-shared'],
            language=["c++"]
            ),
        ] 
    )
