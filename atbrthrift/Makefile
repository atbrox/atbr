#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

#BOOST_DIR = /usr/local/boost/include/boost-1_33_1/
BOOST_DIR = /usr/include/boost/
THRIFT_DIR = /usr/local/include/thrift
LIB_DIR = /usr/local/lib

all: thriftgen server

thriftgen: atbr.thrift
	thrift --gen cpp atbr.thrift

#GEN_SRC = gen-cpp/SharedService.cpp ../gen-cpp/shared_types.cpp ../gen-cpp/tutorial_types.cpp ../gen-cpp/Calculator.cpp
GEN_SRC = gen-cpp/AtbrStorage.cpp gen-cpp/atbr_types.cpp gen-cpp/atbr_constants.cpp 

#default: server client

server: AtbrStorage_server.cpp
	g++ -o AtbrStorage_server -I${THRIFT_DIR} -I${BOOST_DIR}  -Igen-cpp -L${LIB_DIR} -lthrift AtbrStorage_server.cpp ${GEN_SRC}

clean:
	$(RM) -r CppClient CppServer
