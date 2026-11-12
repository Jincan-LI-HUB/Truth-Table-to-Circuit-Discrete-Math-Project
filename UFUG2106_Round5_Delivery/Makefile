CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra
.PHONY: all clean
all: build/synth_round5 build/synth_reference
build/synth_round5: src/synth_round5.cpp src/polarity_mapper.hpp src/algebraic_mapper.hpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) -DROUND5_CACHE=1 $< -o $@
build/synth_reference: src/synth_balanced.cpp src/polarity_mapper.hpp src/algebraic_mapper.hpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) $< -o $@
clean:
	rm -rf build
