// Program used to compare performance of C++ strings vs using C char*
// source: http://stackoverflow.com/questions/3989111/char-vs-string-speed-in-c
/* result on Amund Tveit's Macbook Air 2011 version with 4GB ram and SSD disk (osx 
$$ ./stringperformancetest 
Empty loop = 0.358404
char* loop = 0.432666
std::string = 6.77236
slowdown = 86.3693

i.e. std::string is 86 times slower than using char*
 */

#include <string>
#include <iostream>
#include <time.h>

using std::cout;

void stop()
{
}

int main(int argc, char* argv[])
{
    #define LIMIT 100000000
    clock_t start;
    std::string foo1 = "Hello there buddy";
    std::string foo2 = "Hello there buddy, yeah you too";
    std::string f;
    start = clock();
    for (int i=0; i < LIMIT; i++) {
        stop();
        f = foo1;
        foo1 = foo2;
        foo2 = f;
    }
    double stl = double(clock() - start) / CLOCKS_PER_SEC;

    start = clock();
    for (int i=0; i < LIMIT; i++) {
        stop();
    }
    double emptyLoop = double(clock() - start) / CLOCKS_PER_SEC;

    char* goo1 = "Hello there buddy";
    char* goo2 = "Hello there buddy, yeah you too";
    char *g;
    start = clock();
    for (int i=0; i < LIMIT; i++) {
        stop();
        g = goo1;
        goo1 = goo2;
        goo2 = g;
    }
    double charLoop = double(clock() - start) / CLOCKS_PER_SEC;
    cout << "Empty loop = " << emptyLoop << "\n";
    cout << "char* loop = " << charLoop << "\n";
    cout << "std::string = " << stl << "\n";
    cout << "slowdown = " << (stl - emptyLoop) / (charLoop - emptyLoop) << "\n";
    std::string wait;
    std::cin >> wait;
    return 0;
}
