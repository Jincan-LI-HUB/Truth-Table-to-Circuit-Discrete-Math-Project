CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
UPSTREAM := ../UFUG2106_Round5.1_Delivery/src
HEADERS := src/typed_netgraph.hpp src/polarity_mapper.hpp src/algebraic_mapper.hpp
.PHONY: all materialize clean
all: build/synth_round7
materialize: src/synth_round7.cpp
src/synth_round7.cpp: bootstrap_round7.py $(UPSTREAM)/synth_round51.cpp $(UPSTREAM)/typed_netgraph.hpp $(UPSTREAM)/polarity_mapper.hpp $(UPSTREAM)/algebraic_mapper.hpp
	python3 bootstrap_round7.py
build:
	mkdir -p build
$(HEADERS): src/synth_round7.cpp
	test -f $@
build/synth_round7: src/synth_round7.cpp $(HEADERS) | build
	$(CXX) $(CXXFLAGS) -o $@ src/synth_round7.cpp
clean:
	rm -rf build
