CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra
.PHONY: all clean
all: build/synth_strict build/synth_balanced build/synth_fast
build/synth_%: src/synth_%.cpp src/polarity_mapper.hpp src/algebraic_mapper.hpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) $< -o $@
clean:
	rm -rf build
