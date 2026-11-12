CXX ?= g++
CXXFLAGS ?= -O2 -std=c++17 -pipe -DNDEBUG
.PHONY: all clean
all: build/synth_reference build/synth_round60 build/synth_round61 build/cut_postprocess61
build:
	mkdir -p build
build/synth_reference: src/synth_round51.cpp src/typed_netgraph.hpp src/polarity_mapper.hpp src/algebraic_mapper.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/synth_round51.cpp
build/synth_round60: src/synth_round60.cpp src/cut_rewriter.hpp src/typed_netgraph.hpp src/polarity_mapper.hpp src/algebraic_mapper.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/synth_round60.cpp
build/synth_round61: src/synth_round61.cpp src/cut_rewriter61.hpp src/typed_netgraph.hpp src/polarity_mapper.hpp src/algebraic_mapper.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/synth_round61.cpp
build/cut_postprocess61: src/cut_postprocess61.cpp src/cut_rewriter61.hpp src/typed_netgraph.hpp | build
	$(CXX) $(CXXFLAGS) -o $@ src/cut_postprocess61.cpp
clean:
	rm -rf build
