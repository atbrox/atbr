// This autogenerated skeleton file illustrates how to build a server.
// You should copy it to another filename to avoid overwriting it.

#include "../atbr/atbr.h"

#include "AtbrStorage.h"
#include <protocol/TBinaryProtocol.h>
#include <server/TSimpleServer.h>
#include <transport/TServerSocket.h>
#include <transport/TBufferTransports.h>

using namespace ::apache::thrift;
using namespace ::apache::thrift::protocol;
using namespace ::apache::thrift::transport;
using namespace ::apache::thrift::server;

using boost::shared_ptr;
using namespace com::atbrox::atbr;

class AtbrStorageHandler : virtual public AtbrStorageIf {
 public:
  AtbrStorageHandler() {
    // Your initialization goes here
  }

  void get(std::string& _return, const std::string& key) {
    // Your implementation goes here
    if(storage.exists(key.c_str())) {
      _return = string(storage.get(key.c_str()));
      }
  }

  void load(const std::string& filename) {
    // Your implementation goes here
    printf("load\n");
    storage.load(filename.c_str());
  }

  private:
      Atbr storage;
};

int main(int argc, char **argv) {
  int port = 9090;
  shared_ptr<AtbrStorageHandler> handler(new AtbrStorageHandler());
  shared_ptr<TProcessor> processor(new AtbrStorageProcessor(handler));
  shared_ptr<TServerTransport> serverTransport(new TServerSocket(port));
  shared_ptr<TTransportFactory> transportFactory(new TBufferedTransportFactory());
  shared_ptr<TProtocolFactory> protocolFactory(new TBinaryProtocolFactory());

  TSimpleServer server(processor, serverTransport, transportFactory, protocolFactory);
  server.serve();
  return 0;
}

