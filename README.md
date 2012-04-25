### What is atbr

large-scale in-memory key-value pair store for Python (so far..)

In reality: a thin SWIG-wrapper around Google's sparsehash library (a
library for memory efficient hashtables for C++ created by Craig
Silverstein).

### motivation
1) Modern boxes have 10-100s of Gigabytes of RAM

2) GB+-size Python dictionaries are slow to fill

3) GB+-size Python dictionaries are not fun to use

4) GB+-size dictionaries are fun to use

5) atbr is fast (in particular to load from file)

### prerequisites:
a) install google sparsehash (and densehash)

   wget http://sparsehash.googlecode.com/files/sparsehash-2.0.2.tar.gz

   tar -zxvf sparsehash-2.0.2.tar.gz

   cd sparsehash-2.0.2

   ./configure && make && make install

b) install swig

### install

    make swigpy # creates atbr.py and _atbr.so importable from python

### python-api example

    import atbr

    # Create storage
    mystore = atbr.Atbr()

    # Load data
    mystore.load("keyvaluedata.tsv")

    # Number of key value pairs
    print mystore.size()

    # Get value corresponding to key
    print mystore.get("key1")
    
    # Return true if a key exists
    print mystore.exists("key1")
    
    



