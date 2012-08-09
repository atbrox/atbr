//
//  main.cpp
//  mmapper
//
//  Created by Amund Tveit on 6/21/12.
//  Copyright (c) 2012 Atbrox. All rights reserved.
//

#include <vector>
#include <iostream>
#include <string>
#include <sys/time.h>
#include <memory.h>
#include <string.h> // strtok
#include <unistd.h>
#include <queue>
#include <tr1/unordered_map>

//#include "base64.h" // note: remember to free up tables correctly
#include "mmapper.h"

#ifdef __APPLE__
#include <CoreServices/CoreServices.h>
#include <mach/mach.h>
#include <mach/mach_time.h>
#endif // __APPLE__

using std::priority_queue;
using std::string;
using std::vector;
using std::tr1::unordered_map;
using std::endl;
using std::cerr;
using namespace std;

template< typename FirstType, typename SecondType >
struct RankPairComparator {
    bool operator()( const pair<FirstType, SecondType>& p1, const pair<FirstType, SecondType>& p2 ) const
    {  if( p1.first < p2.first ) return true;
        if( p2.first < p1.first ) return false;
        //if(p2.first == p1.first) return (p2.second < p1.second); // lower URI id should be higher rank if same freq.
        // TODO: strcmp here..
    }
};

typedef priority_queue<pair<int64_t, string>, vector<pair<int64_t, string> >, RankPairComparator<int64_t,string> > RankPriorityQueue;
typedef unordered_map<string, int64_t> UriToFreq;

#ifdef __APPLE__
uint64_t GetPIDTimeInNanoseconds(void)
{
    uint64_t        start;
    uint64_t        end;
    uint64_t        elapsed;
    Nanoseconds     elapsedNano;
    
    // Start the clock.
    
    start = mach_absolute_time();
    
    // Call getpid. This will produce inaccurate results because
    // we're only making a single system call. For more accurate
    // results you should call getpid multiple times and average
    // the results.
    
    (void) getpid();
    
    // Stop the clock.
    
    end = mach_absolute_time();
    
    // Calculate the duration.
    
    elapsed = end - start;
    
    // Convert to nanoseconds.
    
    // Have to do some pointer fun because AbsoluteToNanoseconds
    // works in terms of UnsignedWide, which is a structure rather
    // than a proper 64-bit integer.
    
    elapsedNano = AbsoluteToNanoseconds( *(AbsoluteTime *) &elapsed );
    
    return * (uint64_t *) &elapsedNano;
}
#endif // __APPLE__

vector<string>* tokenize_query(char* query) {
    assert(query != NULL);
    vector<string>* query_terms = new vector<string>();
    char* token, *querycopy, *tofree;
    
    tofree = querycopy = strdup(query);
    while ((token = strsep(&querycopy, " ")) != NULL) {
        query_terms->push_back(string(token));
    }
    return query_terms;
}

void char_tokenize_result(char** result, UriToFreq & uri_to_frequency) {
  char* token, *resultcopy, *tofree;
  UriToFreq::iterator it;
  //int uri;
  string uri;
  size_t len;

  while((token = strsep(result, ",")) != NULL) {
    uri = token; //base64_decode(token, strlen(token), &len);
    it = uri_to_frequency.find(uri);
    if(it == uri_to_frequency.end()) {
      uri_to_frequency[uri] = 0;
    } // TODO: break off when enough unique terms with > N results.
    ++uri_to_frequency[uri];
  }
    
  delete [] tofree;
}

void tokenize_result(string & result, UriToFreq & uri_to_frequency) {
  size_t start_pos = 0;
  size_t result_len = result.size();
  size_t last_comma_pos = -1;
  size_t current_comma_pos = result.find_first_of(',', last_comma_pos+1);

  if(current_comma_pos == string::npos) {
    //cerr << "AT THE END" << endl;
    return;
  }

  UriToFreq::iterator it;
  string uri;

  while(current_comma_pos < result_len-1) {
    uri = result.substr(last_comma_pos+1, (current_comma_pos-last_comma_pos-2));

    //cerr << "uri = " << uri << endl;
    last_comma_pos = current_comma_pos;

    if((current_comma_pos >= 0) && (current_comma_pos < result_len)) {
      it = uri_to_frequency.find(uri);
      if(it == uri_to_frequency.end()) {
	uri_to_frequency[uri] = 0;
	
      } // TODO: break off when enough unique terms with > N results.
      uri_to_frequency[uri] = uri_to_frequency[uri]+1;
    } else {
      break;
    }

    current_comma_pos = result.find_first_of(',', last_comma_pos+1);
    if(current_comma_pos == string::npos) {
      break;
    }
  }

  // need to copy last result
  if(result_len-last_comma_pos > 1) {
    uri = result.substr(last_comma_pos+1, result_len-last_comma_pos-1);
    it = uri_to_frequency.find(uri);
    if(it == uri_to_frequency.end()) {
      uri_to_frequency[uri] = 0;
	
    } // TODO: break off when enough unique terms with > N results.
    //++uri_to_frequency[uri];
    uri_to_frequency[uri] = uri_to_frequency[uri]+1;
  }
}


RankPriorityQueue* query_and_merge(char* query, mmapper & index) {
    //cerr << "query and merge.." << query << endl;
    vector<string>* query_terms = tokenize_query(query);
    vector<string>::iterator it;
    UriToFreq uri_to_frequency;
    
    string res;
    char *result;
    
    for(it = query_terms->begin();
        it != query_terms->end();
        ++it) {
        //cerr << "before result" << endl;
      cerr << "######^^^^^^^^ query = " << it->c_str() << endl;

      //if(strcmp(it->c_str(), "Ave") != 0) {
      //cerr << "Q = " << *it << endl;
	result = index.newsearch(it->c_str(), 0);
	//cerr << "res = " << res << endl;
      //res = index.newsearch(it->c_str(), 0);
	//cerr << "res = " << res  << endl;
        //tokenize_result(res, uri_to_frequency);
	//cerr << "result=" << result << endl;

      char_tokenize_result(&result, uri_to_frequency);
      //}
	//cerr << "^^^^^^^^ query = " << it->c_str() << endl;
	//cerr << "######################################" << endl;
    }

    RankPriorityQueue* ranked_results = new RankPriorityQueue();


    UriToFreq::iterator map_it;
    
    for(map_it = uri_to_frequency.begin();
        map_it != uri_to_frequency.end();
        ++map_it) {
      if(map_it->second >= 1) { // too loose with only one term match?
            ranked_results->push(make_pair(map_it->second, map_it->first));
        }
    }
    
    delete query_terms;
    return ranked_results;
}

int main(int argc, const char * argv[])
{
    if(argc != 3) {
      cerr << "usage: " << argv[0] << " <filename> <query>" << endl;
        exit(1);
    }
    
    double elapsed_microsec;
    
#ifdef __APPLE__
    uint64_t start_t;
    uint64_t stop_t;
    uint64_t delta_t;
    uint64_t elapsed_nano;
    Nanoseconds elapsedNano;
#else
    struct timeval start_time;
    struct timeval stop_time;
    long start_microsec;
    long stop_microsec;
#endif // __APPLE__
    
    string filename = argv[1];
    mmapper mymmapper(filename);
    
    
    string query = argv[2];
    char *q = strdup(argv[2]);
    cerr << "query = " << query << endl;
    char* result = "";
    string res;
    
    RankPriorityQueue* ranked_results;
    
#ifdef __APPLE__
    start_t = mach_absolute_time();
#else
    gettimeofday(&start_time, NULL);
#endif // __APPLE__
    
    //res = mymmapper.search(query, 0);
    //cerr << "r = " << result << endl;
    //result = mymmapper.newsearch(query.c_str(), 0);
    //cerr << "r2 = " << res << endl;
    
    //ranked_results = query_and_merge("foo atbr nasse amund", mymmapper);
    //ranked_results = query_and_merge("B Aughinbaugh", mymmapper);
    //ranked_results = query_and_merge("Justin Cir,", mymmapper);
    ranked_results = query_and_merge(q, mymmapper);
    
    
#ifdef __APPLE__
    stop_t = mach_absolute_time();
    delta_t = stop_t - start_t;
    elapsedNano = AbsoluteToNanoseconds( *(AbsoluteTime *) &delta_t );
    elapsed_nano = * (uint64_t *) &elapsedNano;
    elapsed_microsec = elapsed_nano/1000.0;
#else
    gettimeofday(&stop_time, NULL);
    stop_microsec = (stop_time.tv_sec*1000000) + (stop_time.tv_usec);
    start_microsec = (start_time.tv_sec*1000000) + (start_time.tv_usec);
    elapsed_microsec = stop_microsec-start_microsec;
#endif // __APPLE__
    
    cerr << "result = " << result << endl;
    
    // TODO: use strtok, and then merge using hash_map or something
    
    cerr << "res = " << res << endl;
    
    std::cerr << "Query time in microseconds = " << elapsed_microsec << endl;
    
    cerr << "--->>>> Ranked results" << endl;
    
    size_t len;
    
    string uri;
    string duri;

    int res_counter = 0;
    
    while(!ranked_results->empty()) {
        //cerr << "before uri" << endl;
        uri = ranked_results->top().second;
        //cerr << "afer uri" << endl;
        
        //cerr << uri << endl;
        //uri = base64_decode(uri.c_str(), uri.size(), &len);
        
        cerr << "uri = " << uri << ", freq = " << ranked_results->top().first << endl;
        
        //duri = base64_decode(uri.c_str(), uri.size(), &len);
        //cerr << "duri = " << duri << endl;
        
        //cerr << "before pop" << endl;
        ranked_results->pop();
        //cerr << "afer pop" << endl;

	if(res_counter > 10) {
	  break;
	}

	++res_counter;
    }
    
    cerr << "loop.." << endl;
    
    delete ranked_results;
    
    cerr << "need to release memory?" << endl;
    
    
    // insert code here...
    return 0;
}

