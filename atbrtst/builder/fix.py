import json
import sys
from atbr import atbr

orig_start_address = 0
new_start_address = 0

kv = atbr.Atbr()
kv.load("/mnt/part-00000")
kv.load("/mnt/part-00001")
kv.load("/mnt/part-00002")
print >> sys.stderr, "finished loading part-00000"

#print "\t".join(["orig address", "new address", "orig line len", "new line len", "data"])

def format_address(address):
    format = "%%0%dd" % (9)
    return format % (address)

old_to_new_address = {}

lines = []

i = 0

for line in file('keyvaluefile'):
    line = line.strip()
    try:
        line_len = int(line.split("[")[0])
    except Exception, e:
        print >> sys.stderr, "line = ", [line]
        print >> sys.stderr, e
        print >> sys.stderr, line.split('[')
        sys.exit(1)
    data = json.loads(line[9:line_len])
    jdata = json.dumps(data)

    dlen_before = line_len
    dlen_after = dlen_before # assuming no value

    if data[0] != "":
        a = ""
        try:
            key = json.dumps(data[0])
            a = json.loads(kv.get(json.dumps(data[0])))
        except Exception, e:
            print >> sys.stderr, e
            print >> sys.stderr, "DATA = ", [data]
            print >> sys.stderr, "LINE = ", [line]
            print >> sys.stderr, data[0], json.dumps(data[0])
            sys.exit(1)
        #print >> sys.stderr, "a = ", a
        b = u",".join(a)
        c = b.replace(u"  ", u" ")
        dlen_before = line_len
        #data.append(a)
        key = data[0]
        data[0] = c
        #data.append(key) # FORDEBUGGING!!
        jdata = json.dumps(data)
        dlen_after = len(jdata) + 9

    if data[1] != "":
        c = data[1]
        #print >> sys.stderr, "c = ", c

    old_to_new_address[orig_start_address] = new_start_address

    if i % 10000 == 0:
        print >> sys.stderr, "1st iteration, i = ", i

    i += 1


    #print "\t".join([str(orig_start_address), str(new_start_address), str(dlen_before), str(dlen_after), jdata])
    #lines.append([orig_start_address,new_start_address,dlen_before,dlen_after,data])

    orig_start_address += dlen_before
    new_start_address += dlen_after

i = 0

orig_start_address = 0
new_start_address = 0

output_fh = file("output.dat", "wb")

mapped_to = {}

print >> sys.stderr, "2nd iteration"
for line in file('keyvaluefile'):
    orig_line_len = len(line)  #includes newline, should check against line_len
    line = line.strip()
    line_len = int(line.split("[")[0])
    data = json.loads(line[9:line_len])
    jdata = json.dumps(data)

    dlen_before = line_len
    dlen_after = dlen_before # assuming no value

    if data[1] != "":
        keys = 0
        for key in data[1]:
            old_address = data[1][key]
            # TODO: fix address format
            new_address = old_to_new_address[int(old_address)]
            data[1][key] = new_address
            mapped_to[int(old_address)]  = new_address
            keys += 1
        if i% 10000 == 0:
            print >> sys.stderr, "2nd: data[1] != blank", data[1], keys
      #print >> sys.stderr, "c = ", c
    if data[0] != "":
        a = ""
        try:
            a = json.loads(kv.get(json.dumps(data[0])))
        except Exception, e:
            print >> sys.stderr, e
            print >> sys.stderr, "LINE = ", [line]
            #print sys.stderr, data[0], data
            sys.exit(1)
            #print >> sys.stderr, "a = ", a
        b = u",".join(a)
        c = b.replace(u"  ", u" ")
        dlen_before = line_len
        #data.append(a)
        key = data[0]
        data[0] = c
        #data.append(key) # FORDEBUGGING!!
        jdata = json.dumps(data)
        dlen_after = len(jdata) + 9 + 1# newline and address

    if i% 10000 == 0:
        print >> sys.stderr, "2nd iteration, i = ", i

    i += 1

    # TODO: fix address format and print out
    output = "%s%s\n" % (format_address(new_start_address), jdata)

    output_fh.write(output)
    #print output

    orig_start_address += dlen_before
    new_start_address += dlen_after


output_fh.close()


    

