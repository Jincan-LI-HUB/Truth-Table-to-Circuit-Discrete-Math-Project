#include "r8_structural.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <chrono>
using namespace std;
int main(int argc,char**argv){
 if(argc<4 || argc>5){cerr<<"Usage: optimize_netlist CASE INPUT_NETLIST OUTPUT_NETLIST [mode|all]\n";return 2;}
 int n,m,aa,da,ao,dor,an,dn,target;long long runtime=0;
 ifstream in(argv[1]);string first;if(!(in>>first))return 3;
 if(first=="META"){
   if(!(in>>n>>m>>aa>>da>>ao>>dor>>an>>dn>>target>>runtime))return 5;
 }else{
   n=stoi(first);if(!(in>>m))return 3;
   if(n<1||n>20||m<1)return 3;
   string row;for(size_t i=0;i<(1u<<n);++i)if(!(in>>row))return 4;
   if(!(in>>aa>>da>>ao>>dor>>an>>dn>>target))return 5;in>>runtime;
 }
 if(n<1||n>20||m<1)return 3;
 r51::Costs c{aa,da,ao,dor,an,dn};
 ifstream ni(argv[2]);ostringstream buf;buf<<ni.rdbuf();
 auto g=r51::parse(buf.str(),n,m);auto base=g.metric(c);if(!base.valid)return 6;
 vector<string> modes={"absorb","factor","factor_relaxed","phase","reuse","combined","combined_relaxed"};
 if(argc==5 && string(argv[4])!="all")modes={argv[4]};
 auto best=g;auto score=base;
 for(auto &mode:modes){
  auto r=r8::rewrite(g,c,mode,target);
  auto met=r.graph.metric(c);
  bool accept=met.valid && met.delay<=target && met.area<score.area;
  if(accept){best=std::move(r.graph);score=met;}
  cerr<<"R8_PROBE mode="<<mode<<" area="<<met.area<<" delay="<<met.delay
      <<" ms="<<r.milliseconds<<" attempts="<<r.counts.attempted
      <<" factor="<<r.counts.factoring<<" absorb="<<r.counts.absorption
      <<" expand="<<r.counts.expansion<<" phase="<<r.counts.phase
      <<" accepted="<<accept<<"\n";
 }
 ofstream out(argv[3]);out<<best.serialize();
 cerr<<"R8_RESULT base_area="<<base.area<<" base_delay="<<base.delay<<" area="<<score.area<<" delay="<<score.delay<<"\n";
 return out?0:7;
}
