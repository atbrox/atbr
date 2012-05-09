all: swigpy

swigpy:	atbr.h atbrpy.i
	swig -Wall -c++ -python atbrpy.i
	g++ -I/usr/include/python2.6  -std=gnu++0x -D_GLIBCXX_USE_NANOSLEEP -fpic -c atbrpy_wrap.cxx 
	g++ -shared -Wall -Weffc++ -fpic -Wwrite-strings -Woverloaded-virtual -lrt -std=gnu++0x -DSPARSE_MAP -D_GLIBCXX_USE_NANOSLEEP -fpic atbr.h atbrpy_wrap.o -o _atbr.so

swigpy2:	atbr_microshards.h atbrpy2.i
	swig -Wall -c++ -python atbrpy2.i
	#	g++ -I/usr/include/python2.6  -std=gnu++0x -D_GLIBCXX_USE_NANOSLEEP -fpic -c atbrpy_wrap.cxx 
	c++ -I/usr/include/python2.6  -std=c++0x -D_GLIBCXX_USE_NANOSLEEP -fpic -c atbrpy2_wrap.cxx 
#	g++ -shared -Wall -Weffc++ -fpic -Wwrite-strings -Woverloaded-virtual -lrt -std=gnu++0x -DSPARSE_MAP -D_GLIBCXX_USE_NANOSLEEP -fpic atbr_microshards.h atbrpy2_wrap.o -o _atbr.so
	g++ -shared -Wall -Weffc++ -fpic -Wwrite-strings -Woverloaded-virtual  -D_GLIBCXX_USE_NANOSLEEP -fpic atbr_microshards.h atbrpy2_wrap.o -o _atbr.so

clean:
	rm -f *~ *.cxx *.o *.pyc *.so atbr.py