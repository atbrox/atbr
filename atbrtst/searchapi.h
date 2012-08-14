#ifndef search_api_h
#define search_api_h

#include <iostream>
//#include "rapidjson/document.h"		// rapidjson's DOM-style API
//#include "rapidjson/prettywriter.h"	// for stringify JSON
//#include "rapidjson/filestream.h"	// wrapper of C stream for prettywriter as output
#include <cstdio>
#include <unistd.h>
#include <string>
#include <queue>
#include <tr1/unordered_map> // old way
//#include <unordered_map>

extern "C" {
#include <memory.h>
#include <string.h> // strtok
#include <unistd.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/time.h>
#include <string.h>
}

using std::endl;
using std::cerr;
using std::priority_queue;
using std::string;
using std::vector;
using std::tr1::unordered_map;
//using std::unordered_map;
using std::endl;
using std::cerr;
using std::pair;
using namespace std;

const int64_t MAX_LINE_LENGTH=30000000;

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


class SearchAPI {
 public:
  SearchAPI(char* filename, int address_byte_len=11) {
    line_buffer = new char[MAX_LINE_LENGTH];
    address_buffer = new char[address_byte_len];
    mmap_fp = fopen(filename, "rb");
    assert(mmap_fp != NULL);
    mmap_fd = fileno(mmap_fp);
    cerr << "mmap_fd = " << mmap_fd << endl;
    fseek(mmap_fp,0, SEEK_END);
    mmap_size = ftell(mmap_fp);
    cerr << "mmap_size = " << mmap_size << endl;
    assert(mmap_size >= 0);
    int64_t mmap_start_offset = 0;
    mmap_data = (char*) mmap(NULL, mmap_size, PROT_READ, MAP_SHARED, mmap_fd, mmap_start_offset);
    fclose(mmap_fp);
    cerr << "filename = " << filename << ", size = " << mmap_size << endl;
    srand ( time(NULL) );
    //json_document = new rapidjson::Document();
    if(cachesize > 0) {
        // read data from filename
        // and input into hashmap
        // and when searching, first search in hashmap, and then if results
        // on disk. note: if doing a DFS creation of the index
        // and caching of first line, one could reduce the number of seeks
        // to 1 perhaps.
    }
  }



  virtual ~SearchAPI() {
    delete [] line_buffer;
    delete [] address_buffer;
    //delete json_document;
    munmap(mmap_data, mmap_size);
  }

  /*
  char* lookup(const char* query, int64_t startpos, int64_t address_byte_len=11) {
    // assuming query is a regular key lookup
    assert(mymmapper != NULL);
    return mymmapper->newsearch(query, startpos, address_byte_len);
  }
  */

  /*
  char* search(char* query) {
    // assuming query contains space separated query terms
    RankPriorityQueue* ranked_results = query_and_merge(query, *mymmapper);
    string results = get_results(ranked_results);
    return strdup(results.c_str()); // strdup?
  }
  */

  char* lookup(char* query) {
    return search( (const char*) query);
  }

 private:
  char* search(const char* query, int64_t startpos=0, int64_t address_byte_len=11) {
    //const char* cquery = query.c_str(); // strdup?

  //printf(" ==> newsearch(query='%s', startpos='%d', abl='%d'\n", query, startpos, address_byte_len);
    int64_t query_length = strlen(query); // query.size();    
    memcpy(address_buffer, mmap_data + startpos, address_byte_len);
    int64_t rlength = atol(address_buffer); // atol??
    assert(rlength < MAX_LINE_LENGTH); 
    //cerr << "rlength, query = " << rlength << ", " << query << endl;
    memcpy(line_buffer, mmap_data+startpos, rlength);
    line_buffer[rlength] = '\0';
    char* crecord = line_buffer;
    int64_t quote_start = address_byte_len + 1;
    int64_t quote_end = index(crecord + quote_start+1, '"') - crecord;
        
    if(query_length == 0) {
        return strndup(crecord + quote_start+1, (quote_end-quote_start)-1);
    }
    
    int64_t curlybracketstart = quote_end + 3; // i.e. ", {
    
    if(curlybracketstart > 0 && curlybracketstart < rlength) {
        bool has_result = false;
        int64_t next_pos = -1;
        
        char* strstr_result = NULL;
        char ctmpquery[100];
        char next_query[100];
        int64_t key_pos = -1;
        int64_t value_quote_pos_start = -1;
        int64_t value_quote_pos_stop = -1;
        
        for(int64_t j=0; j<query_length; ++j) {            
            ctmpquery[0] = '"';
            ctmpquery[query_length-j+1] = '"';
            ctmpquery[query_length-j+2] = '\0';
            memcpy( ctmpquery+1, query, query_length-j);
            strstr_result= strstr(crecord, ctmpquery);
            if(strstr_result != NULL) {
                key_pos = strstr_result-crecord;
                // find both quotes
                value_quote_pos_start = index(crecord + key_pos + query_length-j+2 + 1, '"') - crecord; // not needing strlen
                value_quote_pos_stop = index(crecord+value_quote_pos_start+1, '"' ) - crecord;
                next_pos = atol( strncpy(next_query, crecord + value_quote_pos_start + 1, value_quote_pos_stop-value_quote_pos_start) );
                strncpy(next_query, query+query_length-j, query_length-(query_length-j+2)+2);
                next_query[query_length-(query_length-j+2)+2] = '\0';
                has_result = true;
                break;
            }
        }
        
        if(has_result) {
            return search(next_query, next_pos, address_byte_len);
        } else {
            return "<empty>";
            //return string("<empty>");
        }
        
    }
    return "<empty>";
  }
  FILE* mmap_fp;
  int64_t mmap_size;
  int64_t cachesize;
  int mmap_fd;
  char* mmap_data;
  char* line_buffer;
  char* address_buffer;
  //  rapidjson::Document* json_document;
};

#endif // search_api_h
