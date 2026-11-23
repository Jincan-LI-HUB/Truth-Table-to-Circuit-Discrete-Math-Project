#include "../src/r91_library.hpp"
#include <iostream>
#include <cstdlib>
#include <numeric>
int main(){
 auto& lib=r91lib::library();size_t total=0;
 r51::Costs c{2,2,3,1,1,1};
 for(int k=2;k<=4;++k){
  for(int t=0;t<(1<<(1<<k));++t)for(auto&r:lib.get(k,t)){
   if(r91lib::func(r,k)!=t){std::cerr<<"symbolic signature mismatch";return 1;}
   r51::Graph empty(k,1);r51::Builder b(empty);
   std::vector<int> leaves(k);std::iota(leaves.begin(),leaves.end(),1);
   r84cut::Env env{b,c,leaves,k};
   int output=r91lib::instantiate(r,env);
   auto g=b.finish({output});
   if(!g.metric(c).valid)return 2;
   for(int x=0;x<(1<<k);++x){
    std::vector<int> values(g.nodes.size(),0);
    for(int j=0;j<k;++j)values[j+1]=(x>>j)&1;
    for(int id=k+1;id<(int)g.nodes.size();++id){
     auto node=g.nodes[id];
     values[id]=node.op==0?(values[node.a]&values[node.b]):
                 node.op==1?(values[node.a]|values[node.b]):!values[node.a];
    }
    if(values[g.outputs[0]] != ((t>>x)&1)){
     std::cerr<<"materialized truth mismatch k="<<k<<" t="<<t<<" x="<<x<<"\n";return 3;
    }
   }
   ++total;
  }
  if(lib.counts[k]==0)return 4;
 }
 if(total<100)return 5;
 std::cout<<"PASS R91_LIBRARY_INDEPENDENT_MATERIALIZATION count="<<total<<" k2="<<lib.counts[2]
  <<" k3="<<lib.counts[3]<<" k4="<<lib.counts[4]<<"\n";
 return 0;
}
