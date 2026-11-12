#include "cut_rewriter.hpp"
#include <fstream>
#include <iostream>
int main(int argc,char**argv){
 if(argc<4||argc>6){std::cerr<<"usage: cut_postprocess CASE OLD_NET NEW_NET [max_roots=4000] [max_millis=120]\n";return 2;}
 std::ifstream f(argv[1]);int n,m;if(!(f>>n>>m))return 3;
 std::string line;for(int i=0;i<(1<<n);i++)if(!(f>>line))return 4;
 r51::Costs c;int target,limit;if(!(f>>c.aa>>c.da>>c.ao>>c.dor>>c.an>>c.dn>>target))return 5;
 std::ifstream nf(argv[2]);std::string net((std::istreambuf_iterator<char>(nf)),{});
 auto original=r51::parse(net,n,m);auto bm=original.metric(c);if(!bm.valid)return 6;
 int roots=argc>4?std::stoi(argv[4]):4000,millis=argc>5?std::stoi(argv[5]):120;
 auto result=r60::rewrite(original,c,target,roots,millis);auto rm=result.graph.metric(c);
 bool accept=rm.valid&&rm.delay<=target&&rm.area<bm.area;
 std::ofstream out(argv[3]);out<<(accept?result.graph.serialize():net);
 std::cerr<<"cut60 visited="<<result.visited<<" cuts="<<result.cuts<<" attempts="<<result.attempts<<" chosen="<<result.chosen
  <<" hit_budget="<<result.budget_hit<<" baseline_area="<<bm.area<<" proposed_area="<<rm.area
  <<" baseline_delay="<<bm.delay<<" proposed_delay="<<rm.delay<<" accepted="<<accept<<'\n';
 return out?0:7;
}
