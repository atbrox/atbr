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

#include "base64.h"
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

typedef priority_queue<pair<int, string>, vector<pair<int, string> >, RankPairComparator<int,string> > RankPriorityQueue;
typedef unordered_map<string, int> UriToFreq;

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
    
    delete [] tofree;
    return query_terms;
}

vector<char*>* tokenize_result(char** result, UriToFreq & uri_to_frequency) {
  vector<char*>* results = new vector<char*>();
    char* token, *resultcopy, *tofree;
    UriToFreq::iterator it;
    //int uri;
    string uri;

    while((token = strsep(result, ",")) != NULL) {
      //uri = atoi(token);
      //uri = string(token);
      size_t len;
      uri = base64_decode(token, strlen(token), &len);
      //cerr << "token = " << token << endl;


      string r = base64_decode(token, strlen(token), &len);

      cerr << "decoded token = " << r << endl;

      
        // update map counter
      
      it = uri_to_frequency.find(uri);
        if(it == uri_to_frequency.end()) {
            uri_to_frequency[uri] = 0;
        } // TODO: break off when enough unique terms with > N results.
        ++uri_to_frequency[uri];
    }
    
    delete [] tofree;
    return results;
}

RankPriorityQueue* rank_results(vector<char*>& results) {
    
    RankPriorityQueue* ranked_results = new RankPriorityQueue();
    UriToFreq uri_to_frequency;
    
    // iterate and tokenize each result, and
    vector<char*>::iterator it;

    char* result;

    //for(char* result: results) {
    for(it=results.begin();it!=results.end(); ++it) {
      result = *it;
      cerr << "result = " << result << endl;
      tokenize_result(&result, uri_to_frequency);
        // TODO: break off
    }
    
    //for(std::pair<const int,int> it: uri_to_frequency) {
    UriToFreq::iterator map_it;

    for(map_it = uri_to_frequency.begin(); 
	map_it != uri_to_frequency.end();
	++map_it) {
      //cerr << "uri = " << map_it->first << ", " << map_it->second << endl;
      if(map_it->second > 1) {
	  ranked_results->push(make_pair(map_it->second, map_it->first));
        }
    }
    
    // TODO: update priority queue, or do it incrementally in loop above.
    
       return ranked_results;
}



RankPriorityQueue* query_and_merge(char* query, mmapper & index) {
  cerr << "query and merge.." << endl;
    vector<string>* query_terms = tokenize_query(query);
    cerr << "tokenized query.." << endl;
    vector<char*> results;
    
    char* result;
    //for(string query_term: *query_terms) {
    vector<string>::iterator it;

    for(it = query_terms->begin(); 
	it != query_terms->end();
	++it) {
        result = index.newsearch(it->c_str(), 0);
	cerr << it->c_str() << ", res = " << result << endl;
	if(strcmp(result, "<empty>") != 0 ){
	  cerr << "pushing back" << result << endl;
	    results.push_back(result);
	  }
    }

    cerr << results.size() << endl;
    
    RankPriorityQueue* ranked_results = rank_results(results);
    //cerr << "--->>>> Ranked results" << endl;
    
    //while(!ranked_results->empty()) {
        //cerr << "uri = " << ranked_results->top().second << ", freq = " << ranked_results->top().first << endl;
    //    ranked_results->pop();
    //}
    
    

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
    ranked_results = query_and_merge("Justin 10", mymmapper);

    
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
    
    while(!ranked_results->empty()) {
        cerr << "uri = " << ranked_results->top().second << ", freq = " << ranked_results->top().first << endl;
        ranked_results->pop();
    }

    
    // insert code here...
    return 0;
}

