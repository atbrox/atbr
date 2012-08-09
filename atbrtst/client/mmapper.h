//
//  mmapper.h
//  mmapper
//
//  Created by Amund Tveit on 6/21/12.
//  Copyright (c) 2012 Atbrox. All rights reserved.
//

#ifndef mmapper_mmapper_h
#define mmapper_mmapper_h

#include "rapidjson/document.h"		// rapidjson's DOM-style API
#include "rapidjson/prettywriter.h"	// for stringify JSON
#include "rapidjson/filestream.h"	// wrapper of C stream for prettywriter as output
#include <cstdio>

using namespace rapidjson;


using std::string;

class mmapper {
public:
    mmapper(string filename, int64_t cachesize=0, int64_t address_byte_len=11);
    virtual ~mmapper(); 
    inline char get(int64_t pos);
    char get_random();
    string search(string query, int64_t startpos, int64_t address_byte_len=11);
    char* newsearch(const char* query, int64_t startpos, int64_t address_byte_len=11);

 protected:
    FILE* get_fh() {  return mmap_fp; }
    char* get_mmap() { return mmap_data; }
    
private:
    mmapper() {}
    FILE* mmap_fp;
    int64_t mmap_size;
    int mmap_fd;
    char* mmap_data;
    char* line_buffer;
    char* address_buffer;
    rapidjson::Document* json_document;
};

#endif
