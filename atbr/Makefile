all: swigpy

swigpy:	atbr.h atbrpy.i
	swig -Wall -c++ -python atbrpy.i
	g++ -I/usr/include/python2.6  -std=gnu++0x -D_GLIBCXX_USE_NANOSLEEP -fpic -c atbrpy_wrap.cxx 
	g++ -shared -Wall -Weffc++ -fpic -Wwrite-strings -Woverloaded-virtual -lrt -std=gnu++0x -DSPARSE_MAP -D_GLIBCXX_USE_NANOSLEEP -fpic atbr.h atbrpy_wrap.o -o _atbr.so

clean:
	rm -f *~ *.cxx *.o *.pyc *.so atbr.py