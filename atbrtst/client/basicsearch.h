//
//  Created by Amund Tveit on 6/21/12.
//  Copyright (c) 2012 Atbrox. All rights reserved.
//

#ifndef basicsearch_h
#define basicsearch_h

#include <vector>
#include <iostream>
#include <string>
#include <sys/time.h>
#include <memory.h>
#include <string.h> // strtok
#include <unistd.h>
#include <queue>
//#include <tr1/unordered_map> // old way
#include <unordered_map>

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
//using std::tr1::unordered_map;
using std::unordered_map;
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
uint64_t GetPIDTimeInNanoseconds(void);
#endif // __APPLE__

vector<string>* tokenize_query(char* query);
void char_tokenize_result(char** result, UriToFreq & uri_to_frequency);
void tokenize_result(string & result, UriToFreq & uri_to_frequency);
RankPriorityQueue* query_and_merge(char* query, mmapper & index);
string get_results(RankPriorityQueue* ranked_results);
#endif // basicsearch_h
