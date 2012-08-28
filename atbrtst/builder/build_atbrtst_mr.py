from operator import itemgetter
from mrjob.job import MRJob

from operator import itemgetter

#from atbr import atbr
import os
import sys
#from Geohash import encode as ghencode
#import json
import json # json without spacing
import traceback
import types
import logging
import os.path
import base64
from mrjob.protocol import *
import time

from patricia_tree import patricia

GH_RESOLUTION = 5 # +- 2km

class MRBuildAtbrTst(MRJob):
    #OUTPUT_PROTOCOL = RawValueProtocol
    #INPUT_PROTOCOL = RawProtocol
    OUTPUT_PROTOCOL = RawValueProtocol

    def mapper_init(self):
        pass

    def mapper_final(self):
        pass

    def mapper(self, key, value):
        try:
            # only send further to reducer
            # perhaps later shard on word prefix (or hash(uri) if a document is input)
            shard_key = "1"
            #key = key.decode("latin-1").encode("utf-8")
            #value = value.decode("latin-1").encode("utf-8")

        #key = unicode(key.decode("latin-1"))
             #value = unicode(value.decode("latin-1"))
            yield shard_key, (key, value)
        except Exception, e:
            self.increment_counter("mapper", str(e), 1)

#    def combiner_init(self):
#        pass
#
#    def combiner(self):
#        pass

    def sort_words(self,words):
        """sort first due to length and then due to alphanumerical
       in order to make sure that a prefix come before words that uses
       the prefix"""
        len_word_tuples = [(len(w), w) for w in words]
        #sorted_words = sorted(len_word_tuples, key=itemgetter(0,1))
        sorted_words = sorted(len_word_tuples, key=itemgetter(1,0))
        only_sorted_words = [w[1] for w in sorted_words]
        return only_sorted_words

    def reducer(self, shard_key, key_value_pairs):
        debugval = ""
        try:
            for key_value in key_value_pairs:
                _, value = key_value
                key, value = value.split("\t")
                okey = json.loads(key)
                debugval = value
                if not self.patricia_tree.isWord(okey):
                    self.patricia_tree.addWord(okey)
                    self.keyvalue[key] = value
                    self.all_keys.append(okey)
        except Exception, e:
            self.increment_counter("reducer", str(e) + debugval, 1)
            # TODO: need counters here

    def reducer_init(self):
        try:
            self.all_keys = []
            self.patricia_tree = patricia()
            self.keyvalue = {} #atbr.Atbr()

        except Exception, e:
                self.increment_counter("reducer_init", str(e), 1)

    def step_1(self, aggregate, mapping):
        self.increment_counter("reducer_final", "step1 starting", 1)
        t0 = time.time()
        pos = 0
        mapped_pos = {}
        self.all_words = []
        self.ordering_info = {}
        t2 = time.time()
        format = "%%0%dd" % (11)
        for key in sorted(aggregate):
            slim = ["", ""]
            if mapping.has_key(key):
                aggregate[key]["c"] = mapping[key]
                slim[1] = mapping[key]
            if aggregate[key].has_key("value"):
                slim[0] = aggregate[key]["value"]

            self.ordering_info[key] = (slim, aggregate[key]["full_val"])
            self.all_words.append(aggregate[key]["full_val"])
            mapped_pos[key] = format % (pos)
            data = "%s\n" % (json.dumps(slim))
            data_len = len(data)
            record_len = "%011d" % (data_len + 11) # itself!
            pos += len(record_len) + data_len
            self.slimmed[key] = (record_len, slim)
        delta = time.time() - t0
        self.increment_counter("reducer_final", "step1 took " + str(delta) + "s", 1)
        return mapped_pos, aggregate

    def step_2(self, all_words):
        self.increment_counter("reducer_final", "step2 starting", 1)

        t0 = time.time()
        sorted_words = self.sort_words(all_words)
        word_to_order = {}
        for i, word in enumerate(sorted_words):
            word_to_order[word] = i
        #t4 = time.time()
        #print >> sys.stderr, "3. finished", delta3
        delta = time.time() - t0
        self.increment_counter("reducer_final", "step2 took " + str(delta) + "s", 1)

        return word_to_order

    def step_3(self, mapped_pos, word_to_order):
        self.increment_counter("reducer_final", "step3 starting", 1)
        t0 = time.time()

        new_records = []
        slim_sorted = sorted(self.slimmed)
        address = 0
        slim = ""
        for i, key in enumerate(slim_sorted):
            slim = self.slimmed[key][1]
            for k in slim[1]:
                self.slimmed[key][1][1][k] = mapped_pos[slim[1][k]]
            slim = self.slimmed[key][1]
            jslim = json.dumps(slim)
            value = "%s%s\n" % (self.slimmed[key][0], jslim)
            val_len = len(value)
            order_info = self.ordering_info[key]
            order = word_to_order[order_info[1]]
            new_records.append((order, i, address, order_info[1], val_len,
                                self.slimmed[key][0], jslim, slim))
            address += val_len # need to add '\n'
        #delta4 = time.time() - t4
        #print >> sys.stderr, "4. finished", delta4
        delta = time.time() - t0
        self.increment_counter("reducer_final", "step3 took " + str(delta) + "s", 1)
        return new_records

    def step_4(self, new_records):
        self.increment_counter("reducer_final", "step4 starting", 1)
        t0 = time.time()

        self.ordered_new_records = None
        self.new_map = {}

        try:
            # REORDERING RECORDS ACCORDING TO SORTED ENTRIES
            t5 = time.time()
            self.ordered_new_records = sorted(new_records, key=itemgetter(0))
            delta5 = time.time() - t5
            t6 = time.time()
            address = 0
            self.increment_counter("reducer_final", "step 4 HERE",1)
            for record in self.ordered_new_records:
                new_record = (address, record)
                #self.increment_counter("reducer_final", "step 4 HERE2",1)
                value = "%s%s\n" % (record[5], record[6])
                #self.increment_counter("reducer_final", "step 4 HERE3:" + value,1)
                assert len(value) == record[4]
                old_address = record[2]
                self.new_map[old_address] = (address, record[3])
                address += record[4]
            #delta6 = time.time() - t6
            #return ordered_new_records, new_map

            delta = time.time() - t0
            self.increment_counter("reducer_final", "step4 took " + str(delta) + "s", 1)

        except Exception, e:
            self.increment_counter("reducer_final", "step4 FAILED:" + str(e), 1)
            #yield "step4failed", new_records


    def step_5(self, new_map, ordered_new_records):
        try:
            t0 = time.time()
            values = []
            #yield "BEFC", new_map
            self.increment_counter("reducer_final", "step5 starting", 1)

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
                values.append(value)
                #yield "FOOBAR", value
                #print value
            delta7 = time.time() - t7
            #return values
            delta = time.time() - t0

            self.increment_counter("reducer_final", "step5 took " + str(delta) + "s", 1)

            return values

        except Exception, e:
            self.increment_counter("reducer_final", "step5 FAILED:" + str(e), 1)

            #print >> sys.stderr, "deltas = ", [delta0, delta1, delta2, delta3, delta4, delta5, delta6, delta7]

    def reducer_final(self):
        try:
            # use key as value for easy replacement
            for key in self.all_keys:
                self.patricia_tree.addVal(key, key)

            self.global_block = 1
            self.num_digits_to_represent_blocks = 11 # int(math.log10(max_num_blocks)+1)
            self.zeroblock = "".join([str(0) for x in range(self.num_digits_to_represent_blocks)])
            #yield "finaltree", self.patricia_tree._data

            mapping = {}
            aggregate = {}
            self.partition_tree(self.patricia_tree._data,
                parent=self.zeroblock,
                mapping=mapping,
                aggregate=aggregate)
            self.ZEROVAL = u""

            aggregate[self.zeroblock] = {'id':self.zeroblock,
                                              "c":mapping[self.zeroblock],
                                              "full_val": self.ZEROVAL}

            #yield "aggregate", aggregate
            #yield "mapping", mapping

            self.slimmed = {}

            mapped_pos, aggregate = self.step_1(aggregate, mapping)
            #yield "mappedpos", mapped_pos
            #yield "aggregate2", aggregate
            word_to_order = self.step_2(self.all_words)
            #yield "wto", word_to_order
            new_records = self.step_3(mapped_pos, word_to_order)
            #yield "nrc", new_records

            # produces self.ordered_new_records, self.new_map
            self.step_4(new_records)
            #ordered_new_records, new_map = self.step_4(new_records)
            #yield "ordered_new_records", ordered_new_records
            #yield "new_map", new_map

            #self.increment_counter("reducer_final", "after step4 ", 1)



            #print >> sys.stderr, "2. finished", delta2

            values = self.step_5(self.new_map, self.ordered_new_records)
            for value in values:
                yield "", value

            self.step_6(values)
            self.step_7(values)

            for value in self.final_values:
                yield "", value.strip()
            #yield "values", values
        except Exception, e:
            self.increment_counter("reducer_final", str(e), 1)



    def partition_tree(self, input, parent,level=0,
                  mapping={},
                  aggregate={},
                  parent_val=u""):
        """recursive method that unwraps a patricia tree datastructure in
        a way suitable to represent in for low latency disk lookup
            (typically ssd)
            """

        #global global_block

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

            data = {"key": key + infix, "p_id": parent, "full_val": full_val}
            if value != None:
                data["value"] = value

            if not (key == "" and infix == ""):
                format = "%%0%dd" % (self.num_digits_to_represent_blocks)
                data["id"] = format % (self.global_block)
                if not mapping.has_key(data["p_id"]):
                    mapping[data["p_id"]] = {}
                mapping[data["p_id"]][data["key"]] = data["id"]
                if not aggregate.has_key(data["id"]):
                    aggregate[data["id"]] = data
                self.global_block += 1

            format = "%%0%dd" % (self.num_digits_to_represent_blocks)
            self.partition_tree(nested, level=level + 1, parent=data.get("id", self.zeroblock),
                mapping=mapping, aggregate=aggregate, parent_val=full_val)

    def step_6(self, values):
        self.increment_counter("reducer_final", "step6 starting", 1)

        t0 = time.time()

        new_start_address = 0
        orig_start_address = 0
        i = 0
        self.old_to_new_address = {}
        lines = []
        line_len = 0
        data = ""

        for line in values:
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
                #traceback.print_exc()
                print >> sys.stderr, "line, line[11:] = ", [line, line[11:line_len]]
            jdata = ""

            dlen_before = line_len
            dlen_after = 0 # assuming no value

            if data[0] != "":
                a = ""
                try:
                    key = json.dumps(data[0])
                    a = json.loads(self.keyvalue.get(json.dumps(data[0])))
                except Exception, e:
                    print >> sys.stderr, e
                    print >> sys.stderr, "DATA = ", [data]
                    print >> sys.stderr, "LINE = ", [line]
                    print >> sys.stderr, " a= ", [i, a]
                    print >> sys.stderr, data[0], json.dumps(data[0])
                    sys.exit(1)
                    #print >> sys.stderr, "a = ", a
                #b = u",".join(a)
                #c = b.replace(u"  ", u" ")
                dlen_before = line_len
                #data.append(a)
                key = data[0]
                data[0] = a # c
                #data.append(key) # FORDEBUGGING!!

                #foo = "%s%s\n" % ()

            if data[1] != "":
                pass
                #c = data[1]
                #print >> sys.stderr, "c = ", c

            jdata = json.dumps(data)
            dlen_after = len(jdata) + 11 +1  # +1?

            self.old_to_new_address[orig_start_address] = new_start_address
            print >> sys.stderr, "!@@", self.old_to_new_address

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

        delta = time.time()-t0
        self.increment_counter("reducer_final", "step6 took " + str(delta) + "s", 1)

    def step_7(self, values):
        try:
            self.increment_counter("reducer_final", "step7 starting", 1)
            t0 = time.time()

            self.final_values = []

            t0 = time.time()

            new_start_address = 0
            orig_start_address = 0
            i = 0
            lines = []
            line_len = 0
            data = ""

            for line in values:
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
                        print >> sys.stderr, "##", self.old_to_new_address
                        new_address = self.old_to_new_address[int(old_address)]
                        data[1][key] = self.format_address(new_address)
                        #mapped_to[int(old_address)]  = new_address
                        keys += 1
                    if i% 10000 == 0:
                        print >> sys.stderr, "2nd: data[1] != blank", data[1], keys
                        #print >> sys.stderr, "c = ", c
                if data[0] != "":
                    a = ""
                    try:
                        print >> sys.stderr, "TRYING HERE:", data[0]
                        a = json.loads(self.keyvalue.get(json.dumps(data[0])))
                    except Exception, e:
                        print >> sys.stderr, e
                        print >> sys.stderr, "LINE = ", [line]
                        #print sys.stderr, data[0], data
                        sys.exit(1)
                        #print >> sys.stderr, "a = ", a
                    #b = u",".join(a)
                    #c = b.replace(u"  ", u" ")
                    #dlen_before = line_len
                    #data.append(a)
                    key = data[0]
                    data[0] = a
                    #data.append(key) # FORDEBUGGING!!
                    #jdata = json.dumps(data)
                    #dlen_after = len(jdata) + 11# newline and address

                # need to do this after any changes to data..
                jdata = json.dumps(data)
                dlen_after = len(jdata) + 11  +1


                # TODO: fix address format and print out
                output = "%s%s\n" % (self.format_address(dlen_after), jdata)

                self.final_values.append(output)

                assert dlen_after == len(output)

                if i% 10000 == 0:
                    print >> sys.stderr, "### len(jdata), len(output), dlen_after, dlen_before = ", len(jdata), len(output), dlen_after, dlen_before
                    print >> sys.stderr, "2nd iteration, i = ", i, len(output)-len(jdata),len(self.format_address(new_start_address)),len("\n"), len(jdata)

                i += 1


                #output_fh.write(output)
                #print output

                orig_start_address += dlen_before
                new_start_address += dlen_after

            delta = time.time()-t0
            self.increment_counter("reducer_final", "step7 took " + str(delta) + "s", 1)
        except Exception, e:
            self.increment_counter("reducer_final", "step7 FAILED:" + str(e), 1)
            traceback.print_exc()




    def format_address(self,address):
        format = "%%0%dd" % (11)
        return format % (address)



    def steps(self):
        return [self.mr(mapper_init=self.mapper_init,
            mapper=self.mapper,
            mapper_final=self.mapper_final,
            reducer=self.reducer,
            reducer_init=self.reducer_init,
            reducer_final=self.reducer_final), ]


if __name__ == '__main__':
    MRBuildAtbrTst.run()
