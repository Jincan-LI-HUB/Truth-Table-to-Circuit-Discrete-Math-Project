CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra
.PHONY: all clean
all: synth
synth: src/synth.cpp src/polarity_mapper.hpp src/algebraic_mapper.hpp
	$(CXX) $(CXXFLAGS) src/synth.cpp -o synth
clean:
	rm -f synth
