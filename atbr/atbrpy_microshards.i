%module atbr
%include "carrays.i"
%include "std_string.i"
%include "std_wstring.i"
%include "std_vector.i"

%{
  #include "atbr_microshards.h"
  %}

#using namespace std;

#include "atbr_microshards.h"

class Atbr {
 public:
  Atbr();
  unsigned long size();
  const char* get(const char* key);
  bool put(const char* key, const char* value);
  bool exists(const char* key); // wstring key?
  void load(const char* filename);
  unsigned long save(const char* filename);
};



