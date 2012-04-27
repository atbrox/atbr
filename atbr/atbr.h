#ifndef ATBR_H
#define ATBR_H

#include <iostream>
#include <string>
#include <google/sparse_hash_map>
#include <google/dense_hash_map>

#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>

#include <cstdint>

using std::string;
using google::sparse_hash_map;
using google::dense_hash_map;

  class Atbr {
  public:
  Atbr() {
#ifndef SPARSE_MAP
    // only needed for dense_hash_map
      storage.set_empty_key("ATBROX_EMPTY_KEY"); 
#endif
    }

    virtual ~Atbr() {
      // TODO
    }

    const char* get(const char* key) {
      string skey = string(key);
      it = storage.find(skey);
      if(it!=storage.end()) {
	return it->second.c_str();
      }
      return (const char*) "";
    }
    
    void put(const char* key, const char* value) {
      string skey = string(key);
      string svalue = string(value);
      storage[key] = value;
    }
    
    bool exists(const char* key) {
      string skey = string(key);
      return storage.find(skey) != storage.end();
    }
    
    unsigned long size() {
      return storage.size();
    }
    
    void load(const char* filename) {

      unsigned long size_before = size();
      unsigned long totsize = 0;
      struct timespec start, stop;

      clock_gettime(CLOCK_MONOTONIC, &start);

      FILE* fp = fopen(filename, "r");
      if(fp)
	{
	  setvbuf(fp,0,_IOFBF,FILE_BUFFER_SIZE);
	  while( fgets(linebuffer, LINE_BUFFER_SIZE, fp) )
	    {
	      if(linebuffer[strlen(linebuffer)-1] == '\n') {

		linebuffer[strlen(linebuffer)-1] = 0;
	      }

	      totsize += strlen(linebuffer);

	      char *key = strtok(linebuffer,"\t");
	      char *value = strtok(NULL,"\t");
	      if(key != NULL && value != NULL) {
		string skey = string(key);
		string svalue = string(value);
		storage[skey] = svalue; 
	      }
	  }
	}
      fclose(fp);
      
      clock_gettime(CLOCK_MONOTONIC, &stop);

      unsigned long size_after = size();
      double second_diff = timeDiff(&stop,&start)/1000000000.0;

      printf("Inserting took - %f seconds\n", second_diff);
      printf("Num new key-value pairs = %ld\n", (size_after-size_before));
      printf("Speed: %f key-value pairs per second\n", (size_after-size_before)/second_diff);
      printf("Throughput: %f MB per second\n", (totsize/(1024*1024.0))/second_diff);
    }


  private:
    int64_t timeDiff(struct timespec *timeA_p, struct timespec *timeB_p) {
      return ((timeA_p->tv_sec * 1000000000) + timeA_p->tv_nsec) -
	((timeB_p->tv_sec * 1000000000) + timeB_p->tv_nsec);
    }
    const static unsigned int LINE_BUFFER_SIZE = 128*1024;
    char linebuffer[LINE_BUFFER_SIZE]; // 
    const static unsigned int FILE_BUFFER_SIZE = 128*1024;
#ifndef SPARSE_MAP
    dense_hash_map<string, string> storage;
    dense_hash_map<string, string>::iterator it;
    //const char* hash_type = "dense";
#else
    sparse_hash_map<string, string> storage;
    sparse_hash_map<string, string>::iterator it;
    //const char* hash_type = "sparse";
#endif
  };

#endif
