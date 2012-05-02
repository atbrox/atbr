from atbr_thrift_client import connect_to_atbr_thrift_service

service = connect_to_atbr_thrift_service("localhost", "9090")

print dir(service)
service.load("../atbrserver/keyvaluedata.tsv")
