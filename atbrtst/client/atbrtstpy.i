%module atbrtst
%include "carrays.i"
%include "std_string.i"
%include "std_wstring.i"
%include "std_vector.i"

%{
#include "searchapi.h"
  %}

#using namespace std;

#include "searchapi.h"

class SearchAPI {
 public:
  SearchAPI(char* filename);
  char* lookup(char* query);
};



