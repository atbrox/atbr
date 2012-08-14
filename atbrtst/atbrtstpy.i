%module atbrtst
%include "carrays.i"
%include "std_string.i"
%include "std_wstring.i"
%include "std_vector.i"

%{
#include "searchapi.h"
  %}

#include "searchapi.h"

class SearchAPI {
 public:
  SearchAPI(char* filename);
  char* search(char* query);
  char* lookup(char* query);
};



