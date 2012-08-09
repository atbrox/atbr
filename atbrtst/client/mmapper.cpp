//
//  mmapper.cpp
//  mmapper
//
//  Created by Amund Tveit on 6/21/12.
//  Copyright (c) 2012 Atbrox. All rights reserved.
//

#include <iostream>
#include "rapidjson/document.h"		// rapidjson's DOM-style API
#include "rapidjson/prettywriter.h"	// for stringify JSON
#include "rapidjson/filestream.h"	// wrapper of C stream for prettywriter as output
#include <cstdio>
#include <unistd.h>
#include <string>
extern "C" {
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/time.h>
#include <string.h>
}
#include "mmapper.h"

#ifdef __APPLE__
#include <CoreServices/CoreServices.h>
#include <mach/mach.h>
#include <mach/mach_time.h>
#endif // __APPLE__


using std::endl;
using std::cerr;
using namespace rapidjson;
using namespace std; // for string


const int64_t MAX_LINE_LENGTH=30000000;


/*
 std::uniform_int_distribution<int> distribution(0, 99);
 std::mt19937 engine; // Mersenne twister MT19937
 auto generator = std::bind(distribution, engine);
 int random = generator();  // Generate a uniform integral variate between 0 and 99.
 int random2 = distribution(engine); // Generate another sample directly using the distribution and the engine objects.
 */

mmapper::mmapper(string filename, int64_t cachesize, int64_t address_byte_len) {
    line_buffer = new char[MAX_LINE_LENGTH];
    address_buffer = new char[address_byte_len];
    mmap_fp = fopen(filename.c_str(), "rb");
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

mmapper::~mmapper() {
    delete [] line_buffer;
    delete [] address_buffer;
    //delete json_document;
    munmap(mmap_data, mmap_size);
}

char mmapper::get(int64_t pos) {
    if(pos >= mmap_size) {
        cerr << "mmapper::get(" << pos << ") is out of bounds!" << endl;
        return 0;
    }
    return mmap_data[pos];
}

char mmapper::get_random(){
    int64_t random_pos = rand() % mmap_size;
    //cerr << "random_pos = " << random_pos << endl;
    return mmap_data[random_pos];
}

string mmapper::search(string query, int64_t startpos, int64_t address_byte_len) {
  //printf(" ==> search(query='%s', startpos='%d', abl='%d'\n", query.c_str(), startpos, address_byte_len);
    int64_t rlength;// 64bit??
    //char buff[address_byte_len];
    memcpy(address_buffer, mmap_data + startpos, address_byte_len);
    rlength = atol(address_buffer);
    assert(rlength < MAX_LINE_LENGTH); 
    //cerr << "rlength, query = " << rlength << ", " << query << endl;
    memcpy(line_buffer, mmap_data+startpos, rlength);
    line_buffer[rlength] = '\0';
    
    string record = line_buffer;
    int64_t quote_start = address_byte_len + 1;
    int64_t quote_end = record.find('"', quote_start+1);

    if(query.size() == 0) {
        return record.substr(quote_start+1, (quote_end-quote_start)-1);        
    }
      
    int64_t curlybracketstart = quote_end + 3; // i.e. ", {

    if(curlybracketstart > 0 && curlybracketstart < rlength) {
        bool has_result = false;
        int64_t next_pos = -1;
        string subquery = "";
        int64_t query_length = query.size();
        string tmpquery;
        int64_t key_pos = -1;
        int64_t value_quote_pos_start = -1;
        int64_t value_quote_pos_stop = -1;
                        
        for(int64_t j=0; j<query_length; ++j) {
            tmpquery = '"' + query.substr(0,query_length-j) + '"';
            key_pos= record.find(tmpquery);
            if(key_pos != -1) {
                // find both quotes
                value_quote_pos_start = record.find('"', key_pos+tmpquery.size()+1);
                value_quote_pos_stop = record.find('"', value_quote_pos_start+1);
                next_pos = atol(record.substr(value_quote_pos_start+1, value_quote_pos_stop-value_quote_pos_start).c_str());
                subquery = query.substr(query_length-j,query_length-tmpquery.size()+2);
                has_result = true;
                break;

            }
        }
        
        if(has_result) {
            return search(subquery, next_pos, address_byte_len);
        } else {
            return string("<empty>");
        }

    }
    
    return string("<empty>");
}



char* mmapper::newsearch(const char* query, int64_t startpos, int64_t address_byte_len) {
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
            return newsearch(next_query, next_pos, address_byte_len);
        } else {
            return "<empty>";
            //return string("<empty>");
        }
        
    }
    
    return "<empty>";

}





