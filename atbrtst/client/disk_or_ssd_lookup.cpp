//
//  main.cpp
//  mmapper
//
//  Created by Amund Tveit on 6/21/12.
//  Copyright (c) 2012 Atbrox. All rights reserved.
//

#include <iostream>
#include <string>
#include <sys/time.h>
#include <memory.h>
#include <unistd.h>

#include "mmapper.h"

#ifdef __APPLE__
#include <CoreServices/CoreServices.h>
#include <mach/mach.h>
#include <mach/mach_time.h>
#endif // __APPLE__

using std::string;
using std::endl;
using std::cerr;

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
    string result;

#ifdef __APPLE__
    start_t = mach_absolute_time();
#else
    gettimeofday(&start_time, NULL);
#endif // __APPLE__
    
    result = mymmapper.search(query, 0);
    
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

    std::cerr << "Query time in microseconds = " << elapsed_microsec << endl;
    // insert code here...
    return 0;
}

