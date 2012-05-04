namespace py atbrthrift
namespace cpp com.atbrox.atbr

service AtbrStorage {
        string get(1: string key),
	void load(2: string filename)
}