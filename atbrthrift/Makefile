BOOST_DIR = /usr/include/boost/
THRIFT_DIR = /usr/local/include/thrift
LIB_DIR = /usr/local/lib

all: thriftgen atbr_thrift_server

thriftgen: atbr.thrift
	thrift --gen cpp atbr.thrift
	thrift --gen py atbr.thrift
	thrift --gen rb atbr.thrift

GEN_SRC = gen-cpp/AtbrStorage.cpp gen-cpp/atbr_types.cpp gen-cpp/atbr_constants.cpp 

atbr_thrift_server: atbr_thrift_server.cc
	g++ -o atbr_thrift_server -I${THRIFT_DIR} -I${BOOST_DIR}  -Igen-cpp -L${LIB_DIR} -lthrift atbr_thrift_server.cc ${GEN_SRC}

clean:
	$(RM) -r atbr_thrift_server
