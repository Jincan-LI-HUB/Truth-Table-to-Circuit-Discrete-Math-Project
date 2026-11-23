CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
all: build/synth_round84 build/verify_exhaustive
build:
	mkdir -p build
build/synth_round84: src/synth_round84.cpp src/r84_cut.hpp src/r83_cut.hpp src/r82_cut.hpp src/r82_archive.hpp src/r821_resource.hpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/verify_exhaustive: tests/verify_exhaustive.cpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
.PHONY: all clean
clean:
	rm -rf build
