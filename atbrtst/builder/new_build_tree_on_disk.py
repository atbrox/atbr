#!/usr/bin/env python

import json
from patricia_tree import patricia
from operator import itemgetter
import time
import sys
import base64
import zlib
import math
from atbr import atbr
import os

ZEROVAL = u""

num_digits_to_represent_blocks = 9 # int(math.log10(max_num_blocks)+1)
global_block = 1  # need special first block
zeroblock = "".join([str(0) for x in range(num_digits_to_represent_blocks)])

def big_test(argv,file_encoding="latin-1"):
    filename = "../testdata/norwegian_words.txt"
    if len(argv) > 1:
        filename = argv[1]
    import codecs
    p2 = patricia()
    allwords = []
    for line in codecs.open(filename, encoding=file_encoding):
        #print sys.stderr, "line = ", [line]
        word = line.strip()#.lower()
        allwords.append(word)
        if not p2.isWord(word):
            p2.addWord(word)

    added = {}

    for word in allwords:
        if not added.has_key(word) and len(word) > 0:
            p2.addVal(word, word[::-1])
            #p2.addVal(word, word)
            added[word] = True
  
    return p2._data, allwords

def process_value(value):
    import array
    #print >> sys.stderr, type(value)
    v = array.array('I')
    values = [int(x) for x in value.split(",")]
    result = [values[0]]
    v.append(int(result[0]))
    for i in range(1,len(values)):
        result.append(values[i]-values[i-1])
        v.append(int(result[i]))

    r = str(result)
    r2 = ",".join([str(x).strip() for x in result])
    #print >> sys.stderr, r2
    #print >> sys.stderr, len(r), len(zlib.compress(r, 9)), len(zlib.compress(v.tostring())), len(v.tostring()), len(r2), len(zlib.compress(r2))
    return r2

def read_tsv(argv,file_encoding="latin-1"):
    filename = "../testdata/norwegian_words.txt"
    if len(argv) > 1:
        filename = argv[1]
    import codecs
    p2 = patricia()
    allwords = []

    key_value = {}

    for line in codecs.open(filename, encoding=file_encoding):
        #print sys.stderr, "line = ", [line]
        word, value = line.strip().split("\t")#.lower()
        word = json.loads(word.strip())
        value = json.loads(value.strip())
        nvalue = ",".join(value)
        allwords.append(word)
        if not p2.isWord(word):
            p2.addWord(word)
            key_value[word] = nvalue

    added = {}

    for word in allwords:
        if not added.has_key(word) and len(word) > 0:
            #p2.addVal(word, word[::-1])
            p2.addVal(word, key_value[word])
            #p2.addVal(word, word)
            added[word] = True

    return p2._data, allwords

def read_input(argv,file_encoding="latin-1"):
    if len(argv) != 3:
        print "usage: %s <key_file> <key_value_file>"
        sys.exit(1)
    filename = argv[1]
    key_value_filename = argv[2]

    import codecs
    p2 = patricia()
    allwords = []

    key_value = {}
    
    i = 0
    for line in codecs.open(filename, encoding=file_encoding):
        #print sys.stderr, "line = ", [line]
        #word, value = line.strip().split("\t")#.lower()wor
        word = json.loads(line.strip())
        #word = json.loads(word.strip())
        #value = json.loads(value.strip())
        #nvalue = ",".join(value)
        if not p2.isWord(word):
            allwords.append(word) # or above?
            p2.addWord(word)
            if i % 10000 == 0:
                print >> sys.stderr, "added key number ", i
            i += 1

    added = {}

    j = 0
    for word in allwords:
        if not added.has_key(word) and len(word) > 0:
            p2.addVal(word, word[::-1])
            added[word] = True
            if j % 10000 == 0:
                print >> sys.stderr, "added key number ", j
            j += 1
                


    return p2._data, allwords, key_value_filename


def partition(input, level=0,parent=zeroblock, mapping={}, aggregate={}, parent_val=u"", numcalls=0):
    """recursive method that unwraps a patricia tree datastructure in
    a way suitable to represent in for low latency disk lookup
    (typically ssd)
    """
    #print >> sys.stderr, "partition, level, parent_val = ", level, parent_val
    global global_block

    #if numcalls % 1000 == 0:
    #print >> sys.stderr, "numcalls = ", numcalls

    assert type(input) == dict
    for key in input:
        # each val should be an array
        val = input[key]
        #print type(val), type(key)
        assert type(val) == list
        assert len(val) == 2 or len(val) == 3
        #print type(val[0]), type(val[1])
        #print val
        #print val[0]
        #print len(val), val[1]
        assert type(val[0]) == str or type(val[0]) == unicode
        assert type(val[1]) == dict
        #print len(val)
        # 2 cases, len 2 or 3
        #print len(val)
        value = None
        if(len(val)) == 3:
            (infix, nested, value) = val
        else:
            (infix, nested) = val

        full_val = u"%s%s%s" % (parent_val, key, infix)

        data =  {"key":key+infix, "p_id":parent, "full_val":full_val}
        if value != None:
            data["value"] = value

        if not (key == "" and infix == ""):
            format = "%%0%dd" % (num_digits_to_represent_blocks)
            data["id"] = format % (global_block)
            if not mapping.has_key(data["p_id"]):
                mapping[data["p_id"]] = {}
            mapping[data["p_id"]][data["key"]] = data["id"]
            if not aggregate.has_key(data["id"]):
                aggregate[data["id"]] = data
            global_block += 1

        format = "%%0%dd" % (num_digits_to_represent_blocks)
        partition(nested, level=level+1, parent=data.get("id", zeroblock),
            mapping=mapping,aggregate=aggregate, parent_val=full_val,numcalls=numcalls+1)

def sort_words(words):
    """sort first due to length and then due to alphanumerical
    in order to make sure that a prefix come before words that uses
    the prefix"""

    len_word_tuples = [(len(w), w) for w in words]
    #sorted_words = sorted(len_word_tuples, key=itemgetter(0,1))
    sorted_words = sorted(len_word_tuples, key=itemgetter(1,0))
    only_sorted_words = [w[1] for w in sorted_words]
    return only_sorted_words

# THE CODE BELOW SERIOUSLY NEEDS REFACTORING AND CLEANUP
def partition_patricia_tree(data, t0):
    delta0 = time.time() - t0
    print >> sys.stderr, "DELTA = ", delta0
    mapping = {}
    aggregate = {}
    t1 = time.time()
    partition(data, mapping=mapping, aggregate=aggregate)
    delta1 = time.time() - t1
    print >> sys.stderr, "partitioning finished"
    print >> sys.stderr, os.system("date")
    return aggregate, delta0, delta1, mapping


def first_pass_ordering(aggregate, mapping, slimmed, keyvalues):
    print >> sys.stderr, "first pass"
    print >> sys.stderr, os.system("date")
    pos = 0
    mapped_pos = {}
    all_words = []
    ordering_info = {}
    t2 = time.time()
    format = "%%0%dd" % (9)
    fatval = [str(x) for x in range(100)]

    i = 0 

    for key in sorted(aggregate):
        slim = ["", ""]
        if mapping.has_key(key):
            aggregate[key]["c"] = mapping[key]
            slim[1] = mapping[key]
        if aggregate[key].has_key("value"):
            slim[0] = aggregate[key]["value"]

        ordering_info[key] = (slim, aggregate[key]["full_val"])
        all_words.append(aggregate[key]["full_val"])
        mapped_pos[key] = format % (pos)
        #print >> sys.stderr, "mapped_pos[key] = ", key, mapped_pos[key]
        data = "%s\n" % (json.dumps(slim))

        if i % 1000 == 0:
            print >> sys.stderr, "i = ", i, key, slim

        i+=1

        #print >> sys.stderr, "DATA = ", data
        # TODO: need to create placeholder data_len here, for actual record
        # and then later retrieve data when it is to be written to disk
        # seems to need a few assert wrt. balance of byte alignments..

        # MAKING ROOM FOR BIGGER VALUE, BUT NOT ACTUALLY STORING IT
        # NOTE: COULD DO PADDING HERE?
        #print >> sys.stderr, "##KEY = ", key

        data_len = len(data)

        if slim[0] != "": # LOOKUP!
            #print >> sys.stderr, "NADA..", slim
            k = json.dumps(slim[0][::-1])
            yoda = keyvalues.get(k) # MAY NEED TO RECALCULATE HERE..
            d2 = """["", "%s"]\n""" % (slim[1])

            #print >> sys.stderr, "d2 = ", d2
            #print >> sys.stderr, "YDPA = ", yoda, k, d2, len(d2), data_len, data
            #print >> sys.stderr, [d2, data]
            data_len = len(d2) + len(yoda)

        #data_len = len(fatval)
        record_len = "%09d" % (data_len + 9) # itself!
        pos += len(record_len) + data_len
        slimmed[key] = (record_len, slim)
    print >> sys.stderr, "first pass finished"
    print >> sys.stderr, os.system("date")
    return all_words, mapped_pos, ordering_info, t2


def second_pass_ordering(all_words, mapped_pos, ordering_info, slimmed, t2, keyvalues):
    print >> sys.stderr, "second pass starting"
    print >> sys.stderr, os.system("date")

    delta2 = time.time() - t2
    t3 = time.time()
    sorted_words = sort_words(all_words)
    delta3 = time.time() - t3
    word_to_order = {}
    for i, word in enumerate(sorted_words):
        word_to_order[word] = i
    t4 = time.time()
    new_records = []
    slim_sorted = sorted(slimmed)

    i = 0
    print >> sys.stderr, "LEN = ", len(slim_sorted)

    address = 0
    for i, key in enumerate(slim_sorted):
        slim = slimmed[key][1]
        #print >>sys.stderr, ".. slim = ", slim
        for k in slim[1]:
            slimmed[key][1][1][k] = mapped_pos[slim[1][k]]

        # NOTE: can always skip slim[0] since not using
        # may need to recalculate

        slim = slimmed[key][1]

        if i%10000 == 0:
            print >> sys.stderr, "2nd pass, i = ", i, slim

        i += 1

        jslim = json.dumps(slim) # this has been done above.., should look up in atbr instead
        value = "%s%s\n" % (slimmed[key][0], jslim)
        val_len = len(value) # this value should be known already (above)?? keys are fixed size

        #print >> sys.stderr, "jslim = ", key, jslim

        if slim[0] != "": # just indirect pointer
            #jslim = json.dumps()
            k = json.dumps(slim[0][::-1])
            yoda = keyvalues.get(k) # MAY NEED TO RECALCULATE HERE..
            d3 = """["", "%s"]\n""" % (slim[1])
            jslim2 = json.dumps(d3)
            jslim = jslim2
            wal = "%s%s\n" % (slimmed[key][0], jslim2)
            new_val_len = len(wal) + len(yoda) # OR CALCULATED VALUE BASED ON IT
            #print >> sys.stderr, new_val_len
            val_len = new_val_len

        #print >> sys.stderr, "BUILTSLIM = ", slim

        order_info = ordering_info[key]
        order = word_to_order[order_info[1]]
        # probably don't need to keep everything in new_records, can look up later
        # can skip jslim and slim and put elsewhere, some dup info as well here
        new_records.append((order, i, address, order_info[1], val_len, slimmed[key][0], jslim, slim))
        address += val_len # need to add '\n'

    print >> sys.stderr, "second pass finishing"
    print >> sys.stderr, os.system("date")
    return delta2, delta3, new_records, t4


def third_pass_ordering(new_records, t4):
    print >> sys.stderr, "third pass starting"
    print >> sys.stderr, os.system("date")
    delta4 = time.time() - t4
    # REORDERING RECORDS ACCORDING TO SORTED ENTRIES
    t5 = time.time()
    ordered_new_records = sorted(new_records, key=itemgetter(0))
    delta5 = time.time() - t5
    t6 = time.time()
    address = 0
    new_map = {}

    i = 0

    print >> sys.stderr, "LLEN = ", len(ordered_new_records)

    for record in ordered_new_records:
        new_record = (address, record) # unused??
        # value is not needed here, but a key to lookup is?
        #value = "%s%s\n" % (record[5], record[6])
        #assert len(value) == record[4] # DEBUG ONLY!!
        if i%10000 == 0:
            print >> sys.stderr, "3rd pass i = ", i

        i += 1

        old_address = record[2]
        new_map[old_address] = (address, record[3])

        # TODO: need to get this somehow!!
        address += record[4]
    delta6 = time.time() - t6
    print >> sys.stderr, "third pass finishing"
    print >> sys.stderr, os.system("date")
    return delta4, delta5, delta6, new_map, ordered_new_records


def fourth_pass_ordering(delta0, delta1, delta2, delta3, delta4, delta5, delta6, new_map, ordered_new_records,keyvalues):
    t7 = time.time()
    # UPDATE TO NEW ADDRESS REFERENCES
    acc_address = 0

    i = 0

    for record in ordered_new_records:
        slim = record[7]
        #print >> sys.stderr, "RECORD = ", record
        #print >> sys.stderr, "B.slim = ", slim
        #print >> sys.stderr, "acc_address = ", acc_address

        if type(slim[1]) == dict:
            for key in slim[1]:
                #print >> sys.stderr, "slim[1] = ", slim[1], key
                #print >> sys.stderr, "new_map = ", new_map.keys()
                #new_address_info = new_map[int(slim[1][key])]
                new_address_info = new_map[acc_address]
                #print >> sys.stderr, "new_address_ifnfo = ", new_address_info   , acc_address
                (new_address, _) = new_address_info
                format = "%%0%dd" % (9) # HARDCODED!
                formatted_new_address = format % (new_address)
                #slim[1][key] = formatted_new_address
                #print >>sys.stderr, "slim1 after", slim[1]
            # THIS is where to look up the value from atbr
        if slim[0] != "":
            # lookup and insert value
            k = json.dumps(slim[0][::-1])
            yoda = keyvalues.get(k) # MAY NEED TO RECALCULATE HERE..
            data = [yoda, slim[1]]
            #print >> sys.stderr, "data = ", data
            d3 = json.dumps(data)
            slim = d3
        else:
            slim = json.dumps(slim)

        if i%10000 == 0:
            print "4th pass, i = ", i

        i += 1

        value = "%s%s" % (record[5], str(slim))
        acc_address += record[4]
        print value
    delta7 = time.time() - t7
    print >> sys.stderr, "deltas = ", [delta0, delta1, delta2, delta3, delta4, delta5, delta6, delta7]

if __name__ == "__main__":
    t0 = time.time()
    data, allwords, key_value_filename = read_input(sys.argv)



    key_value_store= atbr.Atbr()
    key_value_store.load(key_value_filename)
    print >> sys.stderr, "SIZE = ", key_value_store.size()
    #key_value_store.put(json.dumps("amund"),"trondheim2012")
    #key_value_store.put(json.dumps("abra"), "sahara2011")

    aggregate, delta0, delta1, mapping = partition_patricia_tree(data, t0)

    #print >> sys.stderr, "... mapping = ", mapping
    #print >> sys.stderr, "... aggregate = ", aggregate

    # create special zeroblock entry
    slimmed = {}
    aggregate[zeroblock] = {'id':zeroblock, "c":mapping[zeroblock],
                            "full_val": ZEROVAL}

    all_words, mapped_pos, ordering_info, t2 = first_pass_ordering(aggregate, mapping, slimmed, key_value_store)

    #print >> sys.stderr, "SLIMMED = ", slimmed

    delta2, delta3, new_records, t4 = second_pass_ordering(all_words, mapped_pos, ordering_info, slimmed, t2, key_value_store)

    #print >> sys.stderr, "NEW RECORDS = ", new_records

    delta4, delta5, delta6, new_map, ordered_new_records = third_pass_ordering(new_records, t4)

    fourth_pass_ordering(delta0, delta1, delta2, delta3, delta4, delta5, delta6, new_map, ordered_new_records, key_value_store)

