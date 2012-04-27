![atbr](https://s3.amazonaws.com/atbr/atbr_small.png)

### What is atbr?

large-scale in-memory key-value pair store for Python


### Why atbr?

    1) Modern boxes have 10-100s of Gigabytes of RAM

    2) GB+-size Python dictionaries are slow to fill

    3) GB+-size Python dictionaries are not fun to use

    4) GB+-size dictionaries are fun to use

    5) atbr is fast (in particular to load from file)

### install

Run the following to install atbr (including its dependencies)

    chmod +x ./INSTALL.sh && ./INSTALL.sh

which basically does this:

    $ sudo apt-get install libboost-dev python-setuptools swig* python-dev -y
    $ sudo pip install -r requirements.txt # or under virtualenv

    $ wget http://sparsehash.googlecode.com/files/sparsehash-2.0.2.tar.gz
    $ tar -zxvf sparsehash-2.0.2.tar.gz
    $ cd sparsehash-2.0.2
    $ ./configure && make && sudo make install

    $ sudo python setup.py install  # or under virtualenv

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

### benchmark (loading)    

Input for the benchmark was output from a small Hadoop (mapreduce) job
that generated key, value pairs where both the key and value were
json. The benchmark was done an Ubuntu-based Thinkpad x200 with SSD
drive.

     $ ls -al medium.tsv
     -rw-r--r-- 1 amund amund 117362571 2012-04-25 15:36 medium.tsv

     $ wc medium.tsv
     212969   5835001 117362571 medium.tsv
     
     $ python
     >>> import atbr
     >>> a = atbr.Atbr()
     >>> a.load("medium.tsv")
     Inserting took - 1.178468 seconds
     Num new key-value pairs = 212969
     Speed: 180716.807959 key-value pairs per second
     Throughput: 94.803214 MB per second

### atbr http and websocket server

atbr can also run as a server (default port is 8888), supporting both
http and websocket

Start server:

     $ python atbr_server.py


#### HTTP API

Load tsv-file data with http     

     $ curl http://localhost:8888/load/keyvaluedata.tsv

Get value for key = 'key1'

    $ curl http://localhost:8888/get/key/key1

Add key, value pair key='foo', value='bar'

    $ curl http://localhost:8888/put/key/foo/value/bar

#### Websocket API

Example that loads keyvaluedata.tsv using websocket load api

     python websocket_cmdline_client.py keyvaluedata.tsv

##### websocket client code

      import sys
      from websocket import create_connection

      ws = create_connection("ws://localhost:8888/loadws/")
      # e.g. sys.argv[1] could 'keyvaluedata.tsv'
      ws.send(sys.argv[1])
      result =  ws.recv()
      ws.close()
      print result

### What type of datastructure is used in atbr?

Currently Google's sparsehash library (a library for memory efficient
hashtables for C++ created by Craig Silverstein). Will probably
support other efficient C++-based datastructures in the future.



    






    
    

     

    



