CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all clean
all: build/synth_round100_frozen build/synth_round101 build/verify_exhaustive build/trial_submission build/frozen_submission
build:
	mkdir -p build
build/synth_round100_frozen: src/synth_round100_frozen.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/synth_round101: src/synth_round101.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/verify_exhaustive: tests/verify_exhaustive.cpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/trial_submission: trial_submission/synth.cpp $(wildcard trial_submission/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/frozen_submission: frozen_submission/synth.cpp $(wildcard frozen_submission/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
clean:
	rm -rf build
