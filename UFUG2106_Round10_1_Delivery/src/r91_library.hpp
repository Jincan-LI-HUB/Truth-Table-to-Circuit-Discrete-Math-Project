#pragma once
// Round 9.1: independently indexed 2/3/4-cut Boolean template library.
// Experimental, disabled by default. Baseline R9.0 code remains immutable.
#include "r84_cut.hpp"
#include <array>
#include <cmath>
#include <cstdint>
#include <tuple>
#include <limits>
#include <numeric>
#include <algorithm>
#include <chrono>
#include <vector>

namespace r91lib {
using r51::Graph; using r51::Costs; using r51::Builder;
using Clock=std::chrono::steady_clock;
struct Recipe {
 uint8_t shape=0, q=0, negmask=0, ops=0, outneg=0;
 std::array<uint8_t,4> pos{};
};
struct Stats {
 uint64_t selected_roots=0,visited=0,cuts=0,matching_cuts=0,recipes=0;
 uint64_t local_choices=0,delay_reject=0,global_reject=0;
 bool deadline_hit=false;double elapsed_ms=0;
};
struct Result {Graph graph;Stats stats;};
inline int func(const Recipe&r,int k){
 int assignments=1<<k,full=(1<<assignments)-1;
 int t[4]{};
 for(int j=0;j<r.q;++j){
  int v=0;for(int x=0;x<assignments;++x)if(x&(1<<r.pos[j]))v|=1<<x;
  t[j]=((r.negmask>>j)&1)?full^v:v;
 }
 auto combine=[&](int a,int b,int bit){return bit?a|b:a&b;};
 int out=0;
 if(r.shape==0)out=t[0];
 if(r.shape==1){out=t[0];for(int j=1;j<r.q;++j)out=combine(out,t[j],(r.ops>>(j-1))&1);}
 if(r.shape==2)out=combine(combine(t[0],t[1],r.ops&1),combine(t[2],t[3],(r.ops>>1)&1),(r.ops>>2)&1);
 if(r.shape==3)out=(t[0]&t[1])|((full^t[0])&t[2]);
 if(r.shape==4)out=t[0]^t[1];
 if(r.shape==5)out=t[0]^t[1]^t[2];
 if(r.shape==6)out=(t[0]&t[1])|((t[0]|t[1])&t[2]);
 return r.outneg?(full^out):out;
}
// Each bit signature is a complete truth table. A template cannot ever change
// semantics if the signature matches; this is also asserted in the pass.
struct Library {
 std::array<std::vector<std::vector<Recipe>>,5> indexed;
 std::array<uint64_t,5> counts{};
 Library(){for(int k=2;k<=4;++k)build(k);}
 void add(int k,const Recipe&r){
  int f=func(r,k);
  auto&v=indexed[k][f];
  // Diverse, deterministic bounded library; template enumeration order gives
  // simple, low-gate expressions first, then factored/MUX/XOR choices.
  if(v.size()<32){v.push_back(r);++counts[k];}
 }
 void build(int k){
  indexed[k].resize(1<<(1<<k));
  std::array<uint8_t,4> p{};
  for(int i=0;i<k;++i)p[i]=i;
  for(int q=1;q<=k;++q){
   std::array<uint8_t,4> perm=p;
   do {
    // No duplicate subsets from the permutations of unused leaves.
    if(q<k && !std::is_sorted(perm.begin()+q,perm.begin()+k))continue;
    for(int mask=0;mask<(1<<q);++mask)
    for(int flip=0;flip<2;++flip){
     Recipe r{};r.q=q;r.pos=perm;r.negmask=mask;r.outneg=flip;
     if(q==1){r.shape=0;add(k,r);continue;}
     r.shape=1;
     for(int ops=0;ops<(1<<(q-1));++ops){r.ops=ops;add(k,r);}
     if(q==4){r.shape=2;for(int ops=0;ops<8;++ops){r.ops=ops;add(k,r);}}
     if(q==3){
      for(int kind=3;kind<=3;++kind){r.shape=kind;r.ops=0;add(k,r);}
      r.shape=5;r.ops=0;add(k,r);
      r.shape=6;r.ops=0;add(k,r);
     }
     if(q==2){r.shape=4;r.ops=0;add(k,r);}
    }
   }while(std::next_permutation(perm.begin(),perm.begin()+k));
  }
 }
 const std::vector<Recipe>& get(int k,int signature)const{return indexed[k].at(signature);}
};
inline Library& library(){static Library x;return x;}
inline int instantiate(const Recipe&r,r84cut::Env&e){
 std::array<int,4> t{};
 for(int j=0;j<r.q;++j){t[j]=e.leaves[r.pos[j]];if((r.negmask>>j)&1)t[j]=e.neg(t[j]);}
 auto combine=[&](int a,int b,int bit){return e.bin(bit?1:0,a,b);};
 int out=0;
 if(r.shape==0)out=t[0];
 if(r.shape==1){out=t[0];for(int j=1;j<r.q;++j)out=combine(out,t[j],(r.ops>>(j-1))&1);}
 if(r.shape==2)out=combine(combine(t[0],t[1],r.ops&1),combine(t[2],t[3],(r.ops>>1)&1),(r.ops>>2)&1);
 if(r.shape==3)out=e.bin(1,e.bin(0,t[0],t[1]),e.bin(0,e.neg(t[0]),t[2]));
 if(r.shape==4)out=e.bin(1,e.bin(0,t[0],e.neg(t[1])),e.bin(0,e.neg(t[0]),t[1]));
 if(r.shape==5){
  int x=e.bin(1,e.bin(0,t[0],e.neg(t[1])),e.bin(0,e.neg(t[0]),t[1]));
  out=e.bin(1,e.bin(0,x,e.neg(t[2])),e.bin(0,e.neg(x),t[2]));
 }
 if(r.shape==6)out=e.bin(1,e.bin(0,t[0],t[1]),e.bin(0,e.bin(1,t[0],t[1]),t[2]));
 if(r.outneg)out=e.neg(out);
 return out;
}
inline Result rewrite(const Graph&g,const Costs&c,int target,int max_roots=160,double budget_ms=80){
 Result out;out.graph=g;
 if(!g.valid||g.nodes.size()<size_t(g.n+2)||max_roots<=0||budget_ms<3)return out;
 auto started=Clock::now();auto deadline=started+std::chrono::microseconds((long long)(budget_ms*1000));
 const int sz=(int)g.nodes.size();
 const auto& lib=library();
 std::vector<int>uses(sz,0),needed(sz,std::numeric_limits<int>::max()/4),arrival(sz,0);
 for(int i=g.n+1;i<sz;++i){
  auto z=g.nodes[i];++uses[z.a];if(z.op!=2)++uses[z.b];
  arrival[i]=(z.op==2?arrival[z.a]:std::max(arrival[z.a],arrival[z.b]))+r84cut::delay(c,z.op);
 }
 for(int x:g.outputs){++uses[x];needed[x]=std::min(needed[x],target);}
 for(int i=sz-1;i>g.n;--i){
  if(needed[i]>=std::numeric_limits<int>::max()/4)continue;
  auto z=g.nodes[i];int t=needed[i]-r84cut::delay(c,z.op);
  needed[z.a]=std::min(needed[z.a],t);if(z.op!=2)needed[z.b]=std::min(needed[z.b],t);
 }
 std::vector<std::pair<long long,int>> rank;
 rank.reserve(sz);
 for(int i=g.n+1;i<sz;++i){
  if(!uses[i]||needed[i]>=std::numeric_limits<int>::max()/4)continue;
  auto z=g.nodes[i];long long potential=r84cut::cost(c,z.op)*16LL;
  if(z.a>g.n&&uses[z.a]==1)potential+=8LL*r84cut::cost(c,g.nodes[z.a].op);
  if(z.op!=2&&z.b>g.n&&uses[z.b]==1)potential+=8LL*r84cut::cost(c,g.nodes[z.b].op);
  potential+=std::min(8,std::max(0,needed[i]-arrival[i]));
  rank.emplace_back(-potential,i);
 }
 std::sort(rank.begin(),rank.end());
 std::vector<unsigned char>selected(sz,0);
 for(int i=0;i<std::min(max_roots,(int)rank.size());++i)selected[rank[i].second]=1;
 out.stats.selected_roots=std::min(max_roots,(int)rank.size());
 std::vector<std::vector<std::vector<int>>> cuts(sz);
 for(int i=0;i<=g.n;++i)cuts[i].push_back({i});
 Builder b(g);std::vector<int>mapped(sz,-1);std::iota(mapped.begin(),mapped.begin()+g.n+1,0);
 for(int i=g.n+1;i<sz;++i){
  auto z=g.nodes[i];
  std::vector<std::vector<int>> possible;
  if(z.op==2)possible=cuts[z.a];
  else for(auto&a:cuts[z.a])for(auto&d:cuts[z.b]){
   auto u=r84cut::unite(a,d);if(u.size()<=4)possible.push_back(std::move(u));
  }
  std::sort(possible.begin(),possible.end(),[](auto&a,auto&b){
   if(a.size()!=b.size())return a.size()>b.size();return a<b;
  });
  possible.erase(std::unique(possible.begin(),possible.end()),possible.end());
  cuts[i].push_back({i});
  for(auto&u:possible){
   if(cuts[i].size()>=8)break;
   if(u.size()>=2&&u.size()<=4)cuts[i].push_back(u);
  }
  mapped[i]=b.add(z.op,mapped[z.a],z.op==2?0:mapped[z.b],c);
  if(!selected[i]||!uses[i])continue;
  if((out.stats.visited&3)==0 && Clock::now()>deadline){out.stats.deadline_hit=true;break;}
  ++out.stats.visited;
  int incumbent=mapped[i],chosen=incumbent;
  int best_diff=0,best_ready=b.ready[incumbent];
  for(int ci=1;ci<(int)cuts[i].size();++ci){
   const auto&front=cuts[i][ci];int k=(int)front.size();
   ++out.stats.cuts;
   int t;
   try{t=r84cut::truth(g,i,front);}catch(...){continue;}
   const auto& recipes=lib.get(k,t);
   if(recipes.empty())continue;
   ++out.stats.matching_cuts;
   int reclaim=r84cut::private_reclaim(g,i,front,uses,c);
   if(reclaim<=0)continue;
   std::vector<int>actual;actual.reserve(k);
   for(int v:front)actual.push_back(mapped[v]);
   r84cut::Env e{b,c,actual,k};
   for(const auto&r:recipes){
    ++out.stats.recipes;
    // Independent exact Boolean signature check prior to materialization.
    if(func(r,k)!=t)continue;
    int candidate=instantiate(r,e);
    if(b.ready[candidate]>needed[i]){++out.stats.delay_reject;continue;}
    int dif=r84cut::cone_cost(b.graph,candidate,actual,c)-reclaim;
    if(dif<best_diff ||(dif==best_diff&&best_diff<0&&b.ready[candidate]<best_ready)){
     chosen=candidate;best_diff=dif;best_ready=b.ready[candidate];
    }
   }
  }
  if(chosen!=incumbent){mapped[i]=chosen;++out.stats.local_choices;}
 }
 for(int i=g.n+1;i<sz;++i)if(mapped[i]<0){
  auto z=g.nodes[i];mapped[i]=b.add(z.op,mapped[z.a],z.op==2?0:mapped[z.b],c);
 }
 std::vector<int>outputs;for(int o:g.outputs)outputs.push_back(mapped[o]);
 auto candidate=b.finish(std::move(outputs));
 auto before=g.metric(c),after=candidate.metric(c);
 if(after.valid&&before.valid&&after.delay<=target&&after.area<before.area)out.graph=std::move(candidate);
 else if(out.stats.local_choices)++out.stats.global_reject;
 out.stats.elapsed_ms=std::chrono::duration<double,std::milli>(Clock::now()-started).count();
 return out;
}
} // namespace r91lib
