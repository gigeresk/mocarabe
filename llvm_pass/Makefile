LLVM_CONFIG ?= llvm-config-18
CXX         ?= clang++-18

CXXFLAGS := $(shell $(LLVM_CONFIG) --cxxflags) -fPIC -fno-rtti
LDFLAGS  := $(shell $(LLVM_CONFIG) --ldflags)

.PHONY: all clean

all: dfg_to_hgr.so

dfg_to_hgr.so: dfg_to_hgr.cpp
	$(CXX) $(CXXFLAGS) -shared -o $@ $< $(LDFLAGS)

clean:
	rm -f dfg_to_hgr.so *.o
