#CC=clang++ # or g++
CC=g++ # or g++
#MACARGS=-framework CoreServices
MACARGS=

all: atbr_lookup

atbr_lookup: disk_or_ssd_lookup.o mmapper.o
	$(CC) -O3 -I./include -o atbr_lookup disk_or_ssd_lookup.o mmapper.o $(MACARGS)

disk_or_ssd_lookup.o: disk_or_ssd_lookup.cpp *.h
	$(CC) -O3 -I./include -c disk_or_ssd_lookup.cpp

mmapper.o: mmapper.cpp mmapper.h
	$(CC) -O3 -I./include -c mmapper.cpp

clean:
	rm -f *.o atbr_disk_lookup
