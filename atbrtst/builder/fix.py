import ujson as json
import sys
from atbr import atbr
import traceback

orig_start_address = 0
new_start_address = 0

kv = atbr.Atbr()
kv.load("/mnt/part-00000")
kv.load("/mnt/part-00001")
kv.load("/mnt/part-00002")
print >> sys.stderr, "finished loading part-00000"

#print "\t".join(["orig address", "new address", "orig line len", "new line len", "data"])

def format_address(address):
    #if address > 999999999:
    #    print >> sys.stderr, "UNSUPPORTED ADDRESS:", address, len(str(address))
    #    sys.exit(1)
    format = "%%0%dd" % (11)
    #result = "%09d" %(address)
    return format % (address)

old_to_new_address = {}

lines = []
line_len = 0

i = 0

data = ""

for line in file('kv.main'):
    orig_len = len(line)
    line = line.strip()
    try:
        line_len = int(line.split("[")[0])
    except Exception, e:
        print >> sys.stderr, "line = ", [line]
        print >> sys.stderr, e
        print >> sys.stderr, line.split('[')
        sys.exit(1)

    try:
        data = json.loads(line[11:line_len])
    except Exception, e:
        print >> sys.stderr, e
        traceback.print_exc()
        print >> sys.stderr, "line, line[11:] = ", [line, line[11:line_len]]
    jdata = ""

    dlen_before = line_len
    dlen_after = 0 # assuming no value

    if data[0] != "":
        a = ""
        try:
            key = json.dumps(data[0])
            a = json.loads(kv.get(json.dumps(data[0])))
        except Exception, e:
            print >> sys.stderr, e
            print >> sys.stderr, "DATA = ", [data]
            print >> sys.stderr, "LINE = ", [line]
            print >> sys.stderr, " a= ", [i, a]
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

        #foo = "%s%s\n" % ()

    if data[1] != "":
        pass
        #c = data[1]
        #print >> sys.stderr, "c = ", c

    jdata = json.dumps(data)
    dlen_after = len(jdata) + 11 +1  # +1?

    old_to_new_address[orig_start_address] = new_start_address

    if i % 10000 == 0:
        print >> sys.stderr, "1st iteration, i = ", i
        print >> sys.stderr, ">>", [dlen_after, orig_len, line_len, len(jdata)]
        print >> sys.stderr, "okDATA = ", [data,jdata, len(jdata),len(line)]
        print >> sys.stderr, "okLINE = ", [line, repr(line), repr(jdata)]
        #sys.exit(1)

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
for line in file('kv.main'):
    orig_line_len = len(line)  #includes newline, should check against line_len
    line = line.strip()
    line_len = int(line.split("[")[0])
    data = json.loads(line[11:line_len])
    #jdata = json.dumps(data)
    jdata = ""

    dlen_before = line_len
    dlen_after = 0 # assuming no value

    if data[1] != "":
        keys = 0
        for key in data[1]:
            old_address = data[1][key]
            # TODO: fix address format
            new_address = old_to_new_address[int(old_address)]
            data[1][key] = format_address(new_address)
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
        #dlen_before = line_len
        #data.append(a)
        key = data[0]
        data[0] = c
        #data.append(key) # FORDEBUGGING!!
        #jdata = json.dumps(data)
        #dlen_after = len(jdata) + 11# newline and address

    # need to do this after any changes to data..
    jdata = json.dumps(data)
    dlen_after = len(jdata) + 11  +1


    # TODO: fix address format and print out
    output = "%s%s\n" % (format_address(dlen_after), jdata)

    assert dlen_after == len(output)

    if i% 10000 == 0:
        print >> sys.stderr, "### len(jdata), len(output), dlen_after, dlen_before = ", len(jdata), len(output), dlen_after, dlen_before
        print >> sys.stderr, "2nd iteration, i = ", i, len(output)-len(jdata),len(format_address(new_start_address)),len("\n"), len(jdata)

    i += 1


    output_fh.write(output)
    #print output

    orig_start_address += dlen_before
    new_start_address += dlen_after


output_fh.close()


    

