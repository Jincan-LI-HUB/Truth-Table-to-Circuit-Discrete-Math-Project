#include "../src/r82_archive.hpp"
#include <cassert>
#include <iostream>
int main(){
 using namespace r82;
 Point b{"base",100,20};
 assert(delay_cap(b,50,"strict")==20);
 assert(delay_cap(b,50,"slack")==30);
 assert(delay_cap(b,50,"area")==50);
 assert(eligible(b,{"trade",80,25},50,"area"));
 assert(eligible(b,{"trade",80,25},50,"slack"));
 assert(!eligible(b,{"trade",80,25},50,"adp")); // 80*25 == 100*20
 assert(eligible(b,{"better",79,25},50,"adp"));
 assert(!eligible(b,{"slow",50,40},50,"adp"));
 assert(!eligible(b,{"too_slow",60,32},50,"slack"));
 assert(!eligible(b,{"bad_area",110,17},50,"adp")); // no area regression
 auto p=pareto({{"a",110,10},{"b",100,20},{"c",120,15},{"d",100,20},{"e",90,25}});
 assert(p.size()==3);assert(p[0].mode=="a"&&p[1].mode=="b"&&p[2].mode=="e");
 assert(better({"a",80,18},{"b",70,22},"adp")); // 1440 < 1540
 assert(better({"b",70,22},{"a",80,18},"area"));
 std::cout<<"PASS r82_objectives: ADP, bounded slack, strict, Pareto non-domination\n";
}
