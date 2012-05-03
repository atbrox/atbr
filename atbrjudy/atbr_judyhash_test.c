// compilation within ccan
// gcc -static -o foo foo.c jmap.c -I. -L.  -lJudy
#include <string.h>
#include <stdio.h>
#include <ccan/jmap/jmap.h>

struct atbr_map {
  // TODO: does this work with c++ string?
  JMAP_MEMBERS(char*, char *);
};

int main(int argc, char *argv[])
{
     int i;
     struct atbr_map *atbr = jmap_new(struct atbr_map);
     // Note: this is not correct for real parsing!
     for (i = 1; i < argc; i++) {
	     jmap_add(atbr, argv[i], argv[i]);
     }

     printf("Found %lu options:\n", jmap_count(atbr));

     printf("looping through atbr");
     char* foo;
     char* bar;
     for (foo = jmap_first(atbr); foo; foo = jmap_next(atbr,foo)) {
           bar = jmap_get(atbr, foo);
	   printf("key = '%s', value='%s'\n", foo, bar);
     }

     jmap_free(atbr);
     return 0;
}
