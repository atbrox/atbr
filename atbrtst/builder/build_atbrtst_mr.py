from mrjob.job import MRJob

from atbr import atbr
import os
import sys
from Geohash import encode as ghencode
import json
#import traceback
import types
import logging
import os.path
import base64
from mrjob.protocol import RawValueProtocol

from patricia_tree import patricia

GH_RESOLUTION=5 # +- 2km

class MRBuildAtbrTst(MRJob):
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
            yield shard_key, (key, value)
        except Exception, e:
            self.increment_counter("mapper", str(e), 1)


    def reducer(self, shard_key, key_value_pairs):
        try:
            for key_value in key_value_pairs:
                _, value = key_value
                key, value = value.split("\t")
                if not self.patricia_tree.isWord(key):
                    self.patricia_tree.addWord(key)
                    self.keyvalue.put(key, value)
                    self.all_keys.append(key)
        except Exception, e:
            self.increment_counter("reducer", str(e)+debugval, 1)
        # TODO: need counters here

    def reducer_init(self):
        try:
            self.all_keys = []
            self.patricia_tree = patricia()
            self.keyvalue = atbr.Atbr()
        except Exception, e:
            self.increment_counter("reducer_init", str(e), 1)

    def reducer_final(self):
        try:
            for key in self.all_keys:
                self.patricia_tree.addVal(key, key[::-1])
            yield "finaltree", self.patricia_tree._data
        except Exception, e:
            self.increment_counter("reducer_final", str(e), 1)


    def steps(self):
        return [self.mr(mapper_init=self.mapper_init,
            mapper=self.mapper,
            mapper_final=self.mapper_final,
            reducer=self.reducer,
            reducer_init=self.reducer_init,
            reducer_final=self.reducer_final),]


if __name__ == '__main__':
    MRBuildAtbrTst.run()
