CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all clean
all: build/synth_round81 build/optimize_cut build/verify_exhaustive
build:
	mkdir -p build
build/synth_round81: src/synth_round81.cpp src/r81_cut.hpp src/r8_structural.hpp src/typed_netgraph.hpp src/polarity_mapper.hpp src/algebraic_mapper.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/synth_round81.cpp
build/optimize_cut: src/optimize_cut.cpp src/r81_cut.hpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/optimize_cut.cpp
build/verify_exhaustive: tests/verify_exhaustive.cpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ tests/verify_exhaustive.cpp
clean:
	rm -rf build
