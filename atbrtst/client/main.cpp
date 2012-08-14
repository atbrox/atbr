#include "basicsearch.h"

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
    result = mymmapper.newsearch(query.c_str(), 0);
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
    
    string search_results = get_results(ranked_results);

    cerr << search_results << endl;
    
    delete ranked_results;
    
    cerr << "need to release memory?" << endl;
    
    
    // insert code here...
    return 0;
}
