// Standalone randomized property checks against frozen Round 5.1 typed DAG.
// This program does NOT depend on the instructor evaluator and does not modify the frozen source.
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <vector>
#include "typed_netgraph.hpp"
using namespace r51;
static std::vector<int> eval(const Graph& g, int bits) {
  std::vector<int> values(g.nodes.size());
  for (int i=1;i<=g.n;++i) values[i]=(bits>>(g.n-i))&1;
  for (int i=g.n+1;i<(int)g.nodes.size();++i) {
    Node nd=g.nodes[i];
    if(nd.op==0) values[i]=values[nd.a]&values[nd.b];
    else if(nd.op==1) values[i]=values[nd.a]|values[nd.b];
    else if(nd.op==2) values[i]=!values[nd.a];
    else std::abort();
  }
  std::vector<int> outs; for(int o:g.outputs)outs.push_back(values[o]);return outs;
}
static void check_function(const Graph& orig, const Graph& next, int trial, const char *pass){
  if(!next.valid || next.n!=orig.n || next.m!=orig.m) {std::cerr<<"Bad graph "<<trial<<" "<<pass<<"\n";std::exit(1);}
  for (int bits=0;bits<(1<<orig.n);++bits){
    auto a=eval(orig,bits),b=eval(next,bits);
    if(a!=b){std::cerr<<"Semantic failure trial="<<trial<<" pass="<<pass<<" x="<<bits<<"\n";std::exit(2);}
  }
}
int main(){
  std::mt19937_64 rng(0x51B0062026ULL);
  int trials=2000, checks=0, infeasible_recover=0;
  for(int trial=0;trial<trials;++trial){
    int n=2+rng()%5, m=1+rng()%3, gates=4+rng()%43;
    Graph g(n,m);
    for(int k=0;k<gates;k++){
      int id=g.nodes.size(),op=rng()%3;
      int a=rng()%id,b=(op==2?0:rng()%id);
      g.nodes.push_back({op,a,b});
    }
    for(int j=0;j<m;++j){
      int pick = rng()%3==0? n+1+(rng()%gates) : rng()%g.nodes.size();
      g.outputs.push_back(pick);
    }
    Costs c{1+(int)(rng()%8),1+(int)(rng()%5),1+(int)(rng()%8),1+(int)(rng()%5),1+(int)(rng()%6),1+(int)(rng()%4)};
    auto base=g.metric(c);if(!base.valid)std::abort();
    Graph reparsed=parse(g.serialize(),n,m);
    check_function(g,reparsed,trial,"serialize-parse");
    Graph balanced=rebalance(g,c);
    check_function(g,balanced,trial,"rebalance");
    auto b=balanced.metric(c);if(!b.valid)std::abort();
    int target = std::max(1,base.delay)+1+(int)(rng()%14);
    Graph recovered=area_recover(g,c,target,0);
    check_function(g,recovered,trial,"recover");
    auto z=recovered.metric(c);if(!z.valid)std::abort();
    if(z.delay>target)infeasible_recover++;
    Graph chained=area_recover(balanced,c,std::max(1,b.delay)+1+(int)(rng()%14),0);
    check_function(g,chained,trial,"balance-recover");
    if(!chained.metric(c).valid)std::abort();
    checks+=4;
  }
  std::cout<<"PASS cases="<<trials<<" transforms_checked="<<checks
    <<" independent_truth_assignments_per_case=4*(2^n)"
    <<" cases_recover_exceeds_original_feasible_target="<<infeasible_recover<<"\n";
}
