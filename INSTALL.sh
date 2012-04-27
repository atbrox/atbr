#!/bin/bash

echo "step 1 (of 4) Installing prerequisite unix/python componentswith apt-get"
#sudo apt-get install libboost-dev python-setuptools swig* python-dev -y
sudo apt-get install python-setuptools swig* python-dev -y

echo "step 2 (of 4) Installing python library requirements with pip"
sudo pip install -r pip_requirements.txt # or under virtualenv

echo "step 3 (of 4) Installing google sparsehash"
wget http://sparsehash.googlecode.com/files/sparsehash-2.0.2.tar.gz
tar -zxvf sparsehash-2.0.2.tar.gz
./configure && make && sudo make install

echo "step 4 (of 4) Installing atbr"
sudo python setup.py install 

echo "Installation complete"
