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


  char* search(char* query) {
    // assuming query contains space separated query terms
    RankPriorityQueue* ranked_results = query_and_merge(query);
    string results = get_results(ranked_results);
    return strdup(results.c_str()); // strdup?
  }


  char* lookup(char* query) {
    return fetch( (const char*) query);
  }

 private:
  char* fetch(const char* query, int64_t startpos=0, int64_t address_byte_len=11) {
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
            return fetch(next_query, next_pos, address_byte_len);
        } else {
            return "<empty>";
            //return string("<empty>");
        }
        
    }
    return "<empty>";
  }

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


 RankPriorityQueue* query_and_merge(char* query) {
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
     result = fetch(it->c_str(), 0);
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


 string get_results(RankPriorityQueue* ranked_results) {
   assert(ranked_results != NULL);

   string result = "";
   string uri;
   int res_counter = 0;
   int64_t freq = 0;
   char buff[500];
   
   while(!ranked_results->empty()) {
     //cerr << "before uri" << endl;
     uri = ranked_results->top().second;
     freq = ranked_results->top().first;
     
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
     
     sprintf(buff, "%s (%lld)\n", uri.c_str(), freq);
     result.append(buff);
   }
   
   return result;
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
