import sys

# minor change to Justin Peel's Patricia tree, by adding
# support to add values for all keys
# note: this needs to be done in the following way (2 passes) when using it:
# 1) add all keys - multiple addWord(key) calls
# 2) add values for the same keys - multiple addVal(key,val) calls.
# this is ok for many use cases where you have static prefix data

class patricia():
    def __init__(self):
        self._data = {}

    def addWord(self, word):
        data = self._data
        i = 0
        while 1:
            try:
                node = data[word[i:i+1]]
                #print " 1) setting node = ", node

            except KeyError:
                if data:
                    data[word[i:i+1]] = [word[i+1:],{}]
                    #print " 2) setting data[word[i:i+1]] = ",  data[word[i:i+1]]
                else:
                    if word[i:i+1] == '':
                        #print " 3) returning"
                        return
                    else:
                        if i != 0:
                            data[''] = ['',{}]
                            #print " 4) blanking data['']"
                        data[word[i:i+1]] = [word[i+1:],{}]
                        #print " 5) data[word[i:i+1]=", data[word[i:i+1]], word[i:i+1]
                return

            i += 1
            if word.startswith(node[0],i):
                if len(word[i:]) == len(node[0]):
                    if node[1]:
                        try:
                            node[1]['']
                        except KeyError:
                            data = node[1]
                            data[''] = ['',{}]
                    return
                else:
                    i += len(node[0])
                    data = node[1]
            else:
                ii = i
                j = 0
                while ii != len(word) and j != len(node[0]) and\
                      word[ii:ii+1] == node[0][j:j+1]:
                    ii += 1
                    j += 1
                tmpdata = {}
                tmpdata[node[0][j:j+1]] = [node[0][j+1:],node[1]]
                #print " 6) tmpdata = ", tmpdata
                tmpdata[word[ii:ii+1]] = [word[ii+1:],{}]
                #print " 7) tmpdata = ", tmpdata
                data[word[i-1:i]] = [node[0][:j],tmpdata]
                #print " 8) data[word[i-1:i]] = ",  data[word[i-1:i]]
                return

    def getValue(self,word):
        data = self._data
        i = 0
        while 1:
            try:
                node = data[word[i:i+1]]
                #print "a) node = ", node
            except KeyError:
                return None
            i += 1
            if word.startswith(node[0],i):
                if len(word[i:]) == len(node[0]):
                    #print "node0 = ", node[0]
                    #print "node = ", node
                    if node[1]:
                        try:
                            node[1]['']
                        except KeyError:
                            return None
                    #print word[i:], i, "####", node[1], word[i:], i
                    #print "NODE1 = ", node[1], node[1].keys()
                    if len(node) == 3:
                        return node[2]
                    else:
                        return node[1][''][2]
                        #return node[1]
                else:
                    i += len(node[0])
                    data = node[1]
            else:
                return None


    def addVal(self,word, val):
        data = self._data
        i = 0
        while 1:
            try:
                node = data[word[i:i+1]]
                #print "a) node = ", node
            except KeyError:
                return False
            i += 1
            if word.startswith(node[0],i):
                if len(word[i:]) == len(node[0]):
                    #print "b node0 = ", node[0]
                    #print "c node = ", node
                    if node[1]:
                        try:
                            node[1]['']
                        except KeyError:
                            return False
                    #if word == "john":
                    #print word, val, node
                    node.append(val)
                    return True
                else:
                    i += len(node[0])
                    data = node[1]
            else:
                return False

    def isWord(self,word):
        data = self._data
        i = 0
        while 1:
            try:
                node = data[word[i:i+1]]
                #print "a) node = ", node
            except KeyError:
                return False
            i += 1
            if word.startswith(node[0],i):
                if len(word[i:]) == len(node[0]):
                    #print "b node0 = ", node[0]
                    #print "c node = ", node
                    if node[1]:
                        try:
                            node[1]['']
                        except KeyError:
                            return False
                    return True
                else:
                    i += len(node[0])
                    data = node[1]
            else:
                return False

    def isPrefix(self,word):
        data = self._data
        i = 0
        wordlen = len(word)
        while 1:
            try:
                node = data[word[i:i+1]]
            except KeyError:
                return False
            i += 1
            if word.startswith(node[0][:wordlen-i],i):
                if wordlen - i > len(node[0]):
                    i += len(node[0])
                    data = node[1]
                else:
                    return True
            else:
                return False

    def removeWord(self,word):
        data = self._data
        i = 0
        while 1:
            try:
                node = data[word[i:i+1]]
            except KeyError:
                print "Word is not in trie."
                return
            i += 1
            if word.startswith(node[0],i):
                if len(word[i:]) == len(node[0]):
                    if node[1]:
                        try:
                            node[1]['']
                            node[1].pop('')
                        except KeyError:
                            print "Word is not in trie."
                        return
                    data.pop(word[i-1:i])
                    return
                else:
                    i += len(node[0])
                    data = node[1]
            else:
                print "Word is not in trie."
                return


    __getitem__ = isWord

def print_tree(input, spacing=0):
    for k in input:
        print k.encode("utf-8")
        (left, right) = input[k] # should be array
        print "".join([' ' for x in range(spacing+1)]), left.encode("utf-8")
        print_tree(right, spacing+1)


def big_sample_test():
    p2 = patricia()
    import codecs

    allwords = []
    for line in codecs.open('words.txt', encoding="utf-8"):
        word = line.strip()#.lower()
        allwords.append(word)
        if not p2.isWord(word):
            p2.addWord(word)
    #allsorted = sorted(allwords, key=lambda word: len(word))
    #print allsorted
    #for word in allsorted:
        #p2.addWordVal(word)

    added = {}

    for word in allwords:
        if not added.has_key(word) and len(word) > 0:
            p2.addVal(word, word[::-1])
            added[word] = True
        else:
            print >> sys.stderr, "skipping:", [word,len(word)]
    print "getval"
    
    for word in added:
        print "word = ", word.encode("utf-8"), len(word)
        print p2.getValue(word).encode("utf-8")
        assert word[::-1] == p2.getValue(word)
        #assert p2.getValue(word) == word[::-1]
    
    #print p2.getValue("john")

def small_test():
    import json
    p = patricia()
    print "------------------"

    print "@@@@@@@@@@@@@@@@@@@@@@@@@"

    p.addWord("amund")
    p.addWord("amanda")
    p.addWord("amadeus")
    p.addWord("amafelius")
    p.removeWord("amafelius")
    p.addWord("am")
    p.addWord("a")

    p.addWord("beliz")
    p.addWord("belizabeth")

    p.addVal("am", "SECONDVAL")
    p.addVal("a", "yosan233")
    p.addVal("amadeus", "yosan")
    p.addVal("amund", "doodod")
    p.addVal("beliz", "trip")




    print p._data

    fh = file('dump.json', 'wb')
    json.dump(p._data, fh)
    fh.close()

def new_test():
    import json
    p = patricia()
    p.addWord("amund")
    p.addWord("amanda")
    p.addWord("beliz")
    p.addWord("belizabeth")
    p.addVal("amund", "tveit")
    p.addVal("amanda", "mrs")

    fh = file('dump1.json', 'wb')
    json.dump(p._data, fh)
    fh.close()



if __name__ == "__main__":
    #small_test()
    #big_sample_test()
    new_test()
