#include "r81_cut.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
using namespace std;
int main(int argc,char**argv){
 if(argc<4||argc>5){cerr<<"Usage: optimize_cut META_OR_CASE INPUT_NETLIST OUTPUT_NETLIST [sop|shannon|all|choices]\n";return 2;}
 ifstream in(argv[1]);string first;int n,m,aa,da,ao,doo,an,dn,target;long long budget=0;
 if(!(in>>first))return 2;
 if(first=="META"){
  if(!(in>>n>>m>>aa>>da>>ao>>doo>>an>>dn>>target>>budget))return 2;
 }else{
  n=stoi(first);if(!(in>>m)||n<1||n>20)return 2;
  string row;for(int i=0;i<(1<<n);++i)if(!(in>>row))return 3;
  if(!(in>>aa>>da>>ao>>doo>>an>>dn>>target))return 3;
  in>>budget;
 }
 ifstream net(argv[2]);stringstream stream;stream<<net.rdbuf();
 auto g=r51::parse(stream.str(),n,m);r51::Costs c{aa,da,ao,doo,an,dn};
 auto before=g.metric(c);if(!before.valid)return 4;
 string mode=argc==5?argv[4]:"all";
 auto r=r81::rewrite(g,c,target,mode,150,2500);auto met=r.graph.metric(c);
 bool accept=met.valid&&met.delay<=target&&met.area<before.area;
 ofstream out(argv[3]);out<<(accept?r.graph:g).serialize();
 cerr<<"R81_OFFLINE mode="<<mode<<" base="<<before.area<<" new="<<met.area
     <<" delay="<<met.delay<<" accepted="<<accept
     <<" visited="<<r.stats.visited_roots<<" cuts="<<r.stats.cuts
     <<" selected="<<r.stats.selected<<" runtime_ms="<<r.stats.elapsed_ms
     <<" budget_hit="<<r.stats.budget_hit<<"\n";
 return out?0:5;
}
