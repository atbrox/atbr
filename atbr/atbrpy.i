%module atbr
%include "carrays.i"
%include "std_string.i"
%include "std_wstring.i"
%include "std_vector.i"

%{
  #include "atbr.h"
  %}

#using namespace std;

#include "atbr.h"

class Atbr {
 public:
  Atbr();
  unsigned long size();
  const char* get(const char* key);
  void put(const char* key, const char* value);
  bool exists(const char* key); // wstring key?
  void load(const char* filename);
};



