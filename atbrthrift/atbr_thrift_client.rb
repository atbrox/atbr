$:.push('gen-rb')

require 'thrift'
require 'atbr_storage'

begin
  transport = Thrift::BufferedTransport.new(Thrift::Socket.new('localhost', 9090))
  protocol = Thrift::BinaryProtocol.new(transport)
  client = AtbrStorage::Client.new(protocol)
  transport.open()
  print "ping()\n"
  client.load("../atbrserver/keyvaluedata.tsv")
end  
