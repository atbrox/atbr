//
//  Created by Amund Tveit on 6/21/12.
//  Copyright (c) 2012 Atbrox. All rights reserved.
//

#include "basicsearch.h"

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


RankPriorityQueue* query_and_merge(char* query, mmapper & index) {
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
	result = index.newsearch(it->c_str(), 0);
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


