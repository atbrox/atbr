#ifndef ATBR_H
#define ATBR_H

#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>
#ifdef __APPLE__
#include <sys/time.h>
#endif
#ifndef __APPLE__
#include <cstring>
#endif
//#include <cstdint>
#include <iostream>
#include <string>
using std::string;
using std::endl;
using std::cerr;

#ifdef SPARSE_MAP
#include <google/sparse_hash_map>
using google::sparse_hash_map;
typedef sparse_hash_map<string, string> AtbrMapType;
#elif DENSE_MAP
#include <google/dense_hash_map>
using google::dense_hash_map;
typedef dense_hash_map<string, string> AtbrMapType;
#else
#include <tr1/unordered_map>
using std::tr1::unordered_map;
typedef unordered_map<string, string> AtbrMapType;
#endif


  class Atbr {
  public:
  Atbr() {
#ifdef DENSE_MAP
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
    
    bool put(const char* key, const char* value) {
      string skey = string(key);
      string svalue = string(value);
      storage[key] = value;
      // do a lookup and compare to check that it was stored
      return svalue.compare(storage[key]) == 0;
    }
    
    bool exists(const char* key) {
      string skey = string(key);
      return storage.find(skey) != storage.end();
    }
    
    unsigned long size() {
      return storage.size();
    }

    unsigned long save(const char* filename) {
      FILE* fp = fopen(filename, "w");
      unsigned long i = 0;
      if(fp) {
#ifdef __APPLE__
	for(auto& kv: storage) {
	  snprintf(linebuffer, LINE_BUFFER_SIZE, "%s\t%s\n", 
		   kv.first.c_str(), kv.second.c_str());
#else
	  for(it = storage.begin(); it != storage.end(); ++it) {
	    snprintf(linebuffer, LINE_BUFFER_SIZE, "%s\t%s\n", 
		     it->first.c_str(), it->second.c_str());
#endif
	  ++i;
	  fputs(linebuffer, fp);
	}
	fclose(fp);
      }
      return i;
    }
    
    void load(const char* filename) {
      long micro_start=0;
      long micro_stop=0;

      cerr << "Starting to load " << filename << endl;

      unsigned long size_before = size();
      unsigned long totsize = 0;

#ifndef __APPLE__
      struct timespec start, stop;
      clock_gettime(CLOCK_MONOTONIC, &start);
#else
      struct timeval start_time;
      gettimeofday(&start_time, NULL);
      micro_start = (start_time.tv_sec * 1000000) + (start_time.tv_usec);
#endif

      FILE* fp = fopen(filename, "r");
      unsigned int line_len;
      if(fp)
	{
	  setvbuf(fp,0,_IOFBF,FILE_BUFFER_SIZE);
	  while( fgets(linebuffer, LINE_BUFFER_SIZE, fp) )
	    {
	      if(linebuffer[strlen(linebuffer)-1] == '\n') {

		linebuffer[strlen(linebuffer)-1] = 0;
	      }

	      line_len = strlen(linebuffer);
	      if(line_len >= LINE_BUFFER_SIZE-1) {
		cerr << "long line, len = " << line_len << endl;
	      }

	      assert(line_len < LINE_BUFFER_SIZE);

	      totsize += line_len;

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

#ifndef __APPLE__      
      clock_gettime(CLOCK_MONOTONIC, &stop);
      double second_diff = timeDiff(&stop,&start)/1000000000.0;
#else
      struct timeval stop_time;
      gettimeofday(&stop_time, NULL);
      micro_stop = (stop_time.tv_sec * 1000) + (stop_time.tv_usec / 1000);
      double second_diff = (micro_stop-micro_start)/1000000.0;
#endif
      unsigned long size_after = size();

      fprintf(stderr, "Inserting took - %f seconds\n", second_diff);
      fprintf(stderr, "Num new key-value pairs = %ld\n", (size_after-size_before));
      fprintf(stderr, "Speed: %f key-value pairs per second\n", (size_after-size_before)/second_diff);
      fprintf(stderr, "Throughput: %f MB per second\n", (totsize/(1024*1024.0))/second_diff);

    }


  private:
    int64_t timeDiff(struct timespec *timeA_p, struct timespec *timeB_p) {
      return ((timeA_p->tv_sec * 1000000000) + timeA_p->tv_nsec) -
	((timeB_p->tv_sec * 1000000000) + timeB_p->tv_nsec);
    }
    const static unsigned int LINE_BUFFER_SIZE = 30*1024*1024;
    char linebuffer[LINE_BUFFER_SIZE]; // 
    const static unsigned int FILE_BUFFER_SIZE = 30*1024*1024;
    AtbrMapType storage;
    AtbrMapType::iterator it;
  };

#endif
