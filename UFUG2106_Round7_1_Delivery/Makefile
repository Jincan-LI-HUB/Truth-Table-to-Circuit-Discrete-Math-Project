CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all clean
all: build/synth_round71
src/synth_round71.cpp: bootstrap_round71.py bootstrap_round7.py ../UFUG2106_Round5.1_Delivery/src/synth_round51.cpp
	python3 bootstrap_round71.py
build/synth_round71: src/synth_round71.cpp src/typed_netgraph.hpp src/polarity_mapper.hpp src/algebraic_mapper.hpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) -o $@ src/synth_round71.cpp
clean:
	rm -rf build src/synth_round71.cpp src/*.hpp SOURCE_MANIFEST.json
