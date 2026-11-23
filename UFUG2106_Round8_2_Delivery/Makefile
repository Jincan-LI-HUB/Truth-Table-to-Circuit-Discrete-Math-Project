CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all clean
all: build/synth_round82 build/verify_exhaustive build/optimize_cut build/test_objectives
build:
	mkdir -p build
build/synth_round82: src/synth_round82.cpp src/r82_archive.hpp src/r82_cut.hpp src/r81_cut.hpp src/r8_structural.hpp src/typed_netgraph.hpp src/algebraic_mapper.hpp src/polarity_mapper.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/optimize_cut: src/optimize_cut.cpp src/r82_cut.hpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/test_objectives: tests/test_objectives.cpp src/r82_archive.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/verify_exhaustive: tests/verify_exhaustive.cpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
clean:
	rm -f build/synth_round82 build/verify_exhaustive build/optimize_cut build/test_objectives
