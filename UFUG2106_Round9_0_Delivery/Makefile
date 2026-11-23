CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all clean
all: build/synth_round90 build/submission_synth build/synth_round86_frozen build/verify_exhaustive
build:
	mkdir -p build
build/synth_round90: src/synth_round90.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/submission_synth: submission/synth.cpp $(wildcard submission/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/synth_round86_frozen: src/synth_round86_frozen.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/verify_exhaustive: tests/verify_exhaustive.cpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
clean:
	rm -rf build
