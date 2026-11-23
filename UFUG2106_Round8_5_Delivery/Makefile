CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all clean
all: build/synth_round85 build/synth_round84_frozen build/verify_exhaustive build/test_budget_ledger
build:
	mkdir -p build
build/synth_round85: src/synth_round85.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/synth_round84_frozen: src/synth_round84_frozen.cpp $(wildcard src/*.hpp) | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/verify_exhaustive: tests/verify_exhaustive.cpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
build/test_budget_ledger: tests/test_budget_ledger.cpp integration/budget_ledger.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<
clean:
	rm -rf build
