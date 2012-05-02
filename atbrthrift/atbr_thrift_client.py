import logging
import sys
import traceback
from thrift import Thrift
import thrift.transport
import thrift.protocol
from thrift.transport import TSocket, TTransport # Socket og Transport
from thrift.protocol import TBinaryProtocol

sys.path.append("gen-py")
import atbrthrift.AtbrStorage

def connect_to_atbr_thrift_service(hostname, portnum):
    try:
        transport = TSocket.TSocket(hostname, portnum)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)

        atbr_thrift_service = atbrthrift.AtbrStorage.Client(protocol)
        transport.open()
        return atbr_thrift_service
    except Exception, e:
        logging.error(e)
        traceback.print_exc()
        
