CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra -Wpedantic
.PHONY: all baseline clean
all: build/synth
baseline: build/baseline
build/synth: src/synth.cpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) $< -o $@
build/baseline: src/baseline.cpp
	mkdir -p build
	$(CXX) $(CXXFLAGS) $< -o $@
clean:
	rm -f build/synth build/baseline
