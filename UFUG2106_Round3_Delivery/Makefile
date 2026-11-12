CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra
.PHONY: all clean
all: synth synth_core
synth: src/synth.cpp
	$(CXX) $(CXXFLAGS) $< -o $@
synth_core: src/synth_core.cpp
	$(CXX) $(CXXFLAGS) $< -o $@
clean:
	rm -f synth synth_core
