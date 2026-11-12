CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all clean
all: build/synth_reference build/synth_round51
build:
	mkdir -p build
build/synth_reference: src/synth_round5.cpp src/polarity_mapper.hpp src/algebraic_mapper.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/synth_round5.cpp
build/synth_round51: src/synth_round51.cpp src/typed_netgraph.hpp src/polarity_mapper.hpp src/algebraic_mapper.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/synth_round51.cpp
clean:
	rm -rf build
