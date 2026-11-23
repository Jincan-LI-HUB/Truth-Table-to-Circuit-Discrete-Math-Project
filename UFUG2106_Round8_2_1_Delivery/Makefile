CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
all: build/synth_round821 build/verify_exhaustive build/peak_runner
build:
	mkdir -p build
build/synth_round821: src/synth_round821.cpp src/r821_resource.hpp src/r82_cut.hpp src/r82_archive.hpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/peak_runner: tools/peak_runner.cpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/verify_exhaustive: tests/verify_exhaustive.cpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
clean:
	rm -rf build
.PHONY: all clean
