#!/usr/bin/env python

#import json
from patricia_tree import patricia
from operator import itemgetter
import time
import sys
import base64
import zlib
import math
import ujson as json

ZEROVAL = u""

num_digits_to_represent_blocks = 11 # int(math.log10(max_num_blocks)+1)
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
    print >> sys.stderr, type(value)
    v = array.array('I')
    values = [int(x) for x in value.split(",")]
    result = [values[0]]
    v.append(int(result[0]))
    for i in range(1,len(values)):
        result.append(values[i]-values[i-1])
        v.append(int(result[i]))

    r = str(result)
    r2 = ",".join([str(x).strip() for x in result])
    print >> sys.stderr, r2
    print >> sys.stderr, len(r), len(zlib.compress(r, 9)), len(zlib.compress(v.tostring())), len(v.tostring()), len(r2), len(zlib.compress(r2))
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
    filename = "../testdata/norwegian_words.txt"
    if len(argv) > 1:
        filename = argv[1]
    import codecs
    p2 = patricia()
    allwords = []

    key_value = {}

    for line in codecs.open(filename, encoding=file_encoding):
        #print sys.stderr, "line = ", [line]
        #word, value = line.strip().split("\t")#.lower()wor
        word = json.loads(line.strip())

        if '/' in word:
            print >> sys.stderr, "Skipping word:", [word]
            continue
        #word = json.loads(word.strip())
        #value = json.loads(value.strip())
        #nvalue = ",".join(value)
        if not p2.isWord(word):
            allwords.append(word) # or above?
            p2.addWord(word)

    added = {}

    for word in allwords:
        if not added.has_key(word) and len(word) > 0:
            p2.addVal(word, word)
            added[word] = True

    return p2._data, allwords


def partition(input, level=0,parent=zeroblock, mapping={}, aggregate={}, parent_val=u""):
    """recursive method that unwraps a patricia tree datastructure in
    a way suitable to represent in for low latency disk lookup
    (typically ssd)
    """
    global global_block

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
            mapping=mapping,aggregate=aggregate, parent_val=full_val)

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
if __name__ == "__main__":
    t0 = time.time()
    data, allwords = read_input(sys.argv)
    delta0 = time.time()-t0
    print >> sys.stderr, "DELTA = ", delta0

    print >> sys.stderr, "0. finished reading data:", delta0

    mapping = {}
    aggregate = {}
    t1 = time.time()
    partition(data, mapping=mapping, aggregate=aggregate)
    delta1 = time.time()-t1

    print >> sys.stderr, "0. finished partitioning data:", delta1

# create special zeroblock entry
    slimmed = {}
    aggregate[zeroblock] = {'id':zeroblock, "c":mapping[zeroblock],
                            "full_val": ZEROVAL}

    pos = 0
    mapped_pos = {}
    all_words = []
    ordering_info = {}
    t2 = time.time()
    format = "%%0%dd" % (11)

    for key in sorted(aggregate):
        slim = ["",""]
        if mapping.has_key(key):
            aggregate[key]["c"] = mapping[key]
            slim[1] = mapping[key]
        if aggregate[key].has_key("value"):
            slim[0] = aggregate[key]["value"]

        ordering_info[key] = (slim, aggregate[key]["full_val"])
        all_words.append(aggregate[key]["full_val"])
        mapped_pos[key] = format % (pos)
        data = "%s\n" % (json.dumps(slim))
        data_len = len(data)
        record_len = "%011d" % (data_len+11) # itself!
        pos += len(record_len) + data_len
        slimmed[key] = (record_len, slim)

    delta2 = time.time()-t2

    print >> sys.stderr, "2. finished", delta2

    t3 = time.time()
    sorted_words = sort_words(all_words)
    delta3 = time.time()-t3

    word_to_order = {}
    for i, word in enumerate(sorted_words):
        word_to_order[word] = i

    t4 = time.time()

    print >> sys.stderr, "3. finished", delta3


    new_records = []

    slim_sorted = sorted(slimmed)

    address = 0
    for i, key in enumerate(slim_sorted):
        slim = slimmed[key][1]
        for k in slim[1]:
            slimmed[key][1][1][k] = mapped_pos[slim[1][k]]
        slim = slimmed[key][1]
        jslim = json.dumps(slim)
        value = "%s%s\n" % (slimmed[key][0], jslim)
        val_len = len(value)
        order_info = ordering_info[key]
        order = word_to_order[order_info[1]]
        new_records.append((order, i, address, order_info[1], val_len, slimmed[key][0], jslim, slim))
        address += val_len # need to add '\n'

    delta4 = time.time()-t4

    print >> sys.stderr, "4. finished", delta4


# REORDERING RECORDS ACCORDING TO SORTED ENTRIES
    t5 = time.time()
    ordered_new_records = sorted(new_records, key=itemgetter(0))
    delta5 = time.time()-t5
    t6 = time.time()
    address = 0
    new_map = {}

    for record in ordered_new_records:
        new_record = (address, record)
        value = "%s%s\n" % (record[5], record[6])
        assert len(value) == record[4]
        old_address = record[2]
        new_map[old_address] = (address, record[3])
        address += record[4]

    delta6 = time.time()-t6

    print >> sys.stderr, "5. finished", delta6


    t7 = time.time()

    # UPDATE TO NEW ADDRESS REFERENCES
    for record in ordered_new_records:
        slim = record[7]
        if type(slim[1]) == dict:
            for key in slim[1]:
                new_address_info = new_map[int(slim[1][key])]
                (new_address, _) = new_address_info
                format = "%%0%dd" % (11) # HARDCODED!
                formatted_new_address = format % (new_address)
                slim[1][key] = formatted_new_address
        value = "%s%s" % (record[5], json.dumps(slim))
        print value

    delta7 = time.time()-t7

    print >> sys.stderr, "deltas = ", [delta0, delta1, delta2, delta3, delta4, delta5, delta6, delta7]

