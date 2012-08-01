#CC=clang++ # or g++
CC=g++ -std=gnu++0x

#CC=g++ # or g++
#EXTRAARGS=-framework CoreServices -Wc++11-extensions
EXTRAARGS=-std=gnu++0x
#MACARGS=

all: atbr_lookup Makefile

atbr_lookup: disk_or_ssd_lookup.o mmapper.o
	$(CC) -O3 -v -ftime-report -I./include -o atbr_lookup disk_or_ssd_lookup.o mmapper.o $(EXTRAARGS)

disk_or_ssd_lookup.o: disk_or_ssd_lookup.cpp *.h
	$(CC) -O3 -v -ftime-report -I./include -c disk_or_ssd_lookup.cpp

mmapper.o: mmapper.cpp mmapper.h
	$(CC) -O3 -v -ftime-report -I./include -c mmapper.cpp

stringperformancetest: stringperformancetest.cpp
	$(CC) stringperformancetest.cpp -o stringperformancetest

clean:
	rm -f *.o atbr_lookup
