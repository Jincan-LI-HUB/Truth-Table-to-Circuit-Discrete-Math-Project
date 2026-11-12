CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra
.PHONY: all clean
all: synth
synth: src/synth.cpp
	$(CXX) $(CXXFLAGS) $< -o $@
clean:
	rm -f synth
