CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all clean
all: build/synth_round100 build/synth_round91_frozen build/synth_round90_frozen build/submission_synth build/verify_exhaustive
build:
	mkdir -p build
build/synth_round100: src/synth_round100.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/synth_round91_frozen: src/synth_round91_frozen.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/synth_round90_frozen: src/synth_round90_frozen.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/submission_synth: submission/synth.cpp $(wildcard submission/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/verify_exhaustive: tests/verify_exhaustive.cpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
clean:
	rm -rf build
