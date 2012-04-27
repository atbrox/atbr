import atbr

# Create storage
mystore = atbr.Atbr()

# Load data
mystore.load("keyvaluedata.tsv")
 
# Number of key value pairs
print mystore.size()
 
# Get value corresponding to key
print mystore.get("key1")
 
# Return true if a key exists
print mystore.exists("key1")

