import json
import zlib

all_tokens = []
num_kept = 0
uncompressed_lengths = [] 
compressed_lengths = [] 
num_tokens_per_tweet = [] 
num_unique_tokens_per_tweet = []
num_kept_tweets = 0
all_tokens = []

for line in file('yourfilename'):
    # skip non-json lines returned by APIs (lengths)
    if not line.startswith("{"):
        continue

    jline = json.loads(line)

    text = jline.get("text", " ").lower()

    # skips - for simplicity - tweets that can't be space-tokenized
    if not " " in text: 
        continue

    # tweets with metadata
    uncompressed_lengths.append(len(line))
    compressed_lengths.append(len(zlib.compress(line)))
    
    # token calculations
    tokens = text.split(" ")
    num_tokens_per_tweet.append(len(tokens))
    num_unique_tokens_per_tweet.append(len(set(tokens)))
    token_lengths = [len(token) for token in tokens]
    all_tokens.extend(token_lengths)

    num_kept_tweets += 1

avg_uncompressed_length = (sum(uncompressed_lengths)+0.0)/num_kept_tweets
avg_compressed_length = (sum(compressed_lengths)+0.0)/num_kept_tweets
avg_num_tokens = (sum(num_tokens_per_tweet)+0.0)/num_kept_tweets
avg_num_unique_tokens = (sum(num_unique_tokens_per_tweet)+0.0)/num_kept_tweets
avg_token_length = (sum(all_tokens)+0.0)/len(all_tokens)

print "average uncompressed length = ", avg_uncompressed_length
print "average compressed length = ", avg_compressed_length
print "average num tokens = ", avg_num_tokens
print "average num unique tokens = ", avg_num_unique_tokens
print "average token length = ", avg_token_length
print "number of tweets = ", num_kept_tweets

num_tweets_per_day = 340000000
one_gigabyte = 1024*1024*1024
keysize = 64/8 # 64 bit keys

hash_overhead = 2.0/8 # 2 bit overhead

storage_per_day_in_gigabytes = num_tweets_per_day*avg_compressed_length/one_gigabyte + num_tweets_per_day*(keysize+hash_overhead)/one_gigabyte

ram_cost_kUSD_per_petabyte_month = 1197
ram_cost_kUSD_per_terabyte_month = ram_cost_kUSD_per_petabyte_month/1000.0
ram_cost_USD_per_terabyte_day = 1000*ram_cost_kUSD_per_terabyte_month/31

storage_per_day_in_terabytes = storage_per_day_in_gigabytes/1024.0
storage_per_week_in_terabytes = 7*storage_per_day_in_terabytes
storage_per_month_in_terabytes = 31*storage_per_day_in_terabytes
storage_per_year_in_terabytes = 365*storage_per_day_in_terabytes

print "storage per day in terabytes = %f - RAM-cost (per day) %f USD" % (storage_per_day_in_terabytes, storage_per_day_in_terabytes*ram_cost_USD_per_terabyte_day)
print "storage per week in terabytes = %d - RAM-cost (per day) %f kUSD" % (storage_per_week_in_terabytes, 7*storage_per_day_in_terabytes*ram_cost_USD_per_terabyte_day/1000)
print "storage per month in terabytes = %d - RAM-cost (per day) %f kUSD - RAM-cost (per year) %f Million USD" % (storage_per_month_in_terabytes, storage_per_month_in_terabytes*ram_cost_USD_per_terabyte_day/1000, 365*storage_per_month_in_terabytes*ram_cost_USD_per_terabyte_day/(1000*1000))
print "storage per year in terabytes = %d - RAM cost (per day) %f kUSD - RAM cost (per year) %f Million USD" % (storage_per_year_in_terabytes, storage_per_year_in_terabytes*ram_cost_USD_per_terabyte_day/1000, storage_per_year_in_terabytes*ram_cost_USD_per_terabyte_day/(1000*1000)*365)

# index calculations (likely upper bound)

# (extremely naive/stupid/easy-to-estimate-with) assumptions:
# 1) all the unique terms of all single tweets does not occur in other tweets
# 2) there are now new terms from one day to another
#    i.e. the posting list per term increases in average by 1 (64 bit tweet id) every day)
# 3) the posting lists are not compressed, i.e. storing 64 bit per list entry
# 4) token themselves are keys
# 5) no ranking/metadata/ngrams etc. for the index

token_key_overhead = 2.0/8
num_tokens_in_index = num_tweets_per_day*avg_num_unique_tokens

# each tweet provides an update to avg_num_unique_tokens entries in index

key_contribution = num_tokens_in_index*(avg_token_length + token_key_overhead)

index_size_per_day = key_contribution + num_tweets_per_day*avg_num_unique_tokens*64/8
index_size_per_week = key_contribution + num_tweets_per_day*avg_num_unique_tokens*7*64/8
index_size_per_month = key_contribution + num_tweets_per_day*avg_num_unique_tokens*31*64/8
index_size_per_year = key_contribution + num_tweets_per_day*avg_num_unique_tokens*365*64/8

index_size_per_day_in_terabytes = index_size_per_day/(1024*1024*1024)
index_size_per_week_in_terabytes = index_size_per_week/(1024*1024*1024)
index_size_per_month_in_terabytes = index_size_per_month/(1024*1024*1024)
index_size_per_year_in_terabytes = index_size_per_year/(1024*1024*1024)

# assuming slightly better encoding of posting lists, e.g. average of 1 byte per entry would give
better_encoded = index_size_per_year_in_terabytes/8

print "index size per week in terabytes = %f - RAM-cost (per day) %f kUSD" % (index_size_per_week_in_terabytes, index_size_per_week_in_terabytes*ram_cost_USD_per_terabyte_day/1000)
print "index size per month in terabytes = %f - RAM-cost (per day) %f kUSD" % (index_size_per_month_in_terabytes, index_size_per_month_in_terabytes*ram_cost_USD_per_terabyte_day/1000)
print "index size per year in terabytes = %f - RAM-cost (per day) %f kUSD" % (index_size_per_year_in_terabytes, index_size_per_year_in_terabytes*ram_cost_USD_per_terabyte_day/1000)

print "index size per year in terabytes (better encoding) = %f - RAM-cost (per day) %f kUSD" % (better_encoded, better_encoded*ram_cost_USD_per_terabyte_day/1000)








