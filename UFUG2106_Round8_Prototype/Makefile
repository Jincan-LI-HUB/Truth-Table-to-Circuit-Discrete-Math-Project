CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all generate clean
all: build/synth_round8 build/optimize_netlist build/verify_exhaustive
generate:
	python3 bootstrap_round8.py
src/synth_round8.cpp: bootstrap_round8.py ../UFUG2106_Round7_2_Delivery/src/synth_round72.cpp
	python3 bootstrap_round8.py
build:
	mkdir -p build
build/synth_round8: src/synth_round8.cpp src/r8_structural.hpp src/typed_netgraph.hpp src/polarity_mapper.hpp src/algebraic_mapper.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/synth_round8.cpp
build/optimize_netlist: src/optimize_netlist.cpp src/r8_structural.hpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/optimize_netlist.cpp
build/verify_exhaustive: tests/verify_exhaustive.cpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ tests/verify_exhaustive.cpp
clean:
	rm -rf build
