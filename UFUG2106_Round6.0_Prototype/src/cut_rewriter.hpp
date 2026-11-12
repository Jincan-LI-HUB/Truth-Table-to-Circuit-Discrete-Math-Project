#pragma once
// Round 6.0: bounded 4-feasible-cut refactoring. Separate from frozen Round 5.1.
// All candidate transformations are checked by exact local truth tables.
// The caller accepts ONLY full-graph strict area improvements with legal timing.
#include <cstdint>
#include "typed_netgraph.hpp"
#include <array>
#include <chrono>
#include <functional>
#include <map>
#include <set>
#include <unordered_set>
namespace r60 {
using r51::Graph;using r51::Node;using r51::Costs;using r51::Builder;
using Clock=std::chrono::steady_clock;
struct Cut{std::vector<int> leaves;};
struct Result{Graph graph;int visited=0,cuts=0,attempts=0,chosen=0;bool budget_hit=false;};
inline int price(const Costs&c,int op){return op==0?c.aa:op==1?c.ao:c.an;}
inline std::vector<int> unite(const std::vector<int>&a,const std::vector<int>&b){
 std::vector<int> r;std::set_union(a.begin(),a.end(),b.begin(),b.end(),std::back_inserter(r));return r;
}
inline unsigned mask_for(const Graph&g,int root,const std::vector<int>&leaves){
 int k=leaves.size(),sz=1<<k;std::unordered_map<int,unsigned> memo;
 std::function<unsigned(int)> calc=[&](int v)->unsigned{
  auto it=memo.find(v);if(it!=memo.end())return it->second;
  if(v==0)return memo[v]=0;
  auto pos=std::lower_bound(leaves.begin(),leaves.end(),v);
  if(pos!=leaves.end()&&*pos==v){unsigned p=0;int j=int(pos-leaves.begin());
   for(int s=0;s<sz;s++)if(s&(1<<j))p|=1U<<s;return memo[v]=p;}
  if(v<=g.n)throw std::runtime_error("invalid cut: unexplained input");
  auto x=g.nodes[v];unsigned a=calc(x.a),all=(1U<<sz)-1;
  unsigned res=x.op==2?(~a)&all:x.op==0?a&calc(x.b):a|calc(x.b);
  return memo[v]=res;
 };
 return calc(root);
}
struct Emit {
 Builder &b;const Costs&c;const std::vector<int>&leaf;
 int one=-1;
 int isone(int v)const{return v>int(b.graph.n)&&b.graph.nodes[v].op==2&&b.graph.nodes[v].a==0;}
 int neg(int a){if(a==0)return one>=0?one:(one=b.add(2,0,0,c));if(isone(a))return 0;
  if(a>b.graph.n&&b.graph.nodes[a].op==2)return b.graph.nodes[a].a;return b.add(2,a,0,c);}
 int binary(int op,int a,int q){
  if(op==0){if(a==0||q==0)return 0;if(isone(a))return q;if(isone(q))return a;}
  else{if(a==0)return q;if(q==0)return a;if(isone(a)||isone(q))return neg(0);}
  if(a==q)return a;
  if((a>b.graph.n&&b.graph.nodes[a].op==2&&b.graph.nodes[a].a==q)||
     (q>b.graph.n&&b.graph.nodes[q].op==2&&b.graph.nodes[q].a==a))return op==0?0:neg(0);
  return b.add(op,a,q,c);
 }
 int product(const std::vector<int>&v,int op){
  if(v.empty())return op==0?neg(0):0;
  std::priority_queue<std::pair<int,int>,std::vector<std::pair<int,int>>,std::greater<std::pair<int,int>>>pq;
  for(int x:v)pq.emplace(b.ready[x],x);
  while(pq.size()>1){int a=pq.top().second;pq.pop();int z=pq.top().second;pq.pop();int y=binary(op,a,z);pq.emplace(b.ready[y],y);}return pq.top().second;
 }
 struct Cube{int fixed=0,value=0,cover=0,lit=0;};
 std::vector<Cube> cover(int k,unsigned truth,int policy){
  int sz=1<<k;unsigned full=(1U<<sz)-1;
  std::vector<Cube> all;
  for(int fixed=0;fixed<(1<<k);fixed++)for(int val=0;val<(1<<k);val++){
   if(val&~fixed)continue;
   int cv=0;for(int x=0;x<sz;x++)if((x&fixed)==val)cv|=1<<x;
   if((cv&truth)!=cv||cv==0)continue;
   all.push_back({fixed,val,cv,__builtin_popcount((unsigned)fixed)});
  }
  // Prime implicants: a cube cannot be generalized while staying in the on-set.
  std::vector<Cube> primes;
  for(auto c:all){bool expandable=false;
   for(int bit=0;bit<k;bit++)if(c.fixed&(1<<bit)){
    int f=c.fixed^(1<<bit),v=c.value&f,cv=0;
    for(int x=0;x<sz;x++)if((x&f)==v)cv|=1<<x;
    if((cv&truth)==cv){expandable=true;break;}
   }
   if(!expandable)primes.push_back(c);
  }
  std::vector<Cube> selected;int uncovered=int(truth&full);
  while(uncovered){int best=-1;double value=-1;
   for(int i=0;i<int(primes.size());i++){
    int newly=__builtin_popcount((unsigned)(primes[i].cover&uncovered));if(!newly)continue;
    // Frozen, non-case-specific greedy covers; two policies.
    double score=policy==0? double(newly)/(0.8+primes[i].lit):double(newly)*100-primes[i].lit;
    if(score>value){value=score;best=i;}
   }
   if(best<0)break;
   selected.push_back(primes[best]);uncovered &=~primes[best].cover;
  }
  return selected;
 }
 int cube(const Cube&x,int k,int omit=-1){
  std::vector<int>v;for(int j=0;j<k;j++)if((x.fixed&(1<<j))&&j!=omit)
   v.push_back((x.value&(1<<j))?leaf[j]:neg(leaf[j]));
  return product(v,0);
 }
 int sop(int k,unsigned truth,int policy,int factor){
  int full=(1<<(1<<k))-1;
  if(!truth)return 0;if(int(truth)==full)return neg(0);
  auto cubes=cover(k,truth,policy);
  if(cubes.empty())return -1;
  if(factor<0){std::vector<int> terms;for(auto &u:cubes)terms.push_back(cube(u,k));return product(terms,1);}
  // Factor every cube containing one common literal; remaining cubes are separate.
  int group=0;for(int i=0;i<int(cubes.size());i++)
   if((cubes[i].fixed&(1<<(factor/2)))&&(((cubes[i].value>>(factor/2))&1)==(factor&1)))group++;
  if(group<2)return -1;
  std::vector<int>terms, grouped;
  for(auto &u:cubes){int v=factor/2;
   if((u.fixed&(1<<v))&&(((u.value>>v)&1)==(factor&1)))grouped.push_back(cube(u,k,v));
   else terms.push_back(cube(u,k));
  }
  int lit=(factor&1)?leaf[factor/2]:neg(leaf[factor/2]);
  terms.push_back(binary(0,lit,product(grouped,1)));
  return product(terms,1);
 }
 int shannon(int k,unsigned truth,int first){
  // Recursive cofactoring; fixed variable ordering avoids combinatorial search.
  std::function<int(std::vector<int>,unsigned)>go=[&](std::vector<int> vars,unsigned f)->int{
   int z=vars.size(),sz=1<<z;unsigned full=(1U<<sz)-1;
   if(!f)return 0;if(f==full)return neg(0);
   if(z==1)return f==2?leaf[vars[0]]:neg(leaf[vars[0]]);
   int j=(first?z-1:0);std::vector<int> rem;
   for(int a=0;a<z;a++)if(a!=j)rem.push_back(vars[a]);
   unsigned l=0,h=0;
   for(int a=0;a<(sz/2);a++){
    int oldlo=0,oldhi=0,shift=0;
    for(int b=0;b<z;b++){
     if(b==j){oldhi|=1<<b;continue;}
     if(a&(1<<shift)){oldlo|=1<<b;oldhi|=1<<b;}shift++;
    }
    if(f&(1U<<oldlo))l|=1U<<a;if(f&(1U<<oldhi))h|=1U<<a;
   }
   if(l==h)return go(rem,l);
   int x=leaf[vars[j]], lo=go(rem,l),hi=go(rem,h);
   if(!l)return binary(0,x,hi);
   if(!h)return binary(0,neg(x),lo);
   if(l==((1U<<(sz/2))-1))return binary(1,neg(x),hi);
   if(h==((1U<<(sz/2))-1))return binary(1,x,lo);
   return binary(1,binary(0,neg(x),lo),binary(0,x,hi));
  };
  std::vector<int>vars(k);std::iota(vars.begin(),vars.end(),0);return go(vars,truth);
 }
};
inline Result rewrite(const Graph&g,const Costs&c,int target,int max_roots=4000,int max_millis=120){
 Result res;res.graph=g;if(!g.valid||g.nodes.size()<=size_t(g.n+1))return res;
 auto began=Clock::now();auto expired=[&](){return max_millis>0&&std::chrono::duration_cast<std::chrono::milliseconds>(Clock::now()-began).count()>=max_millis;};
 int sz=g.nodes.size();std::vector<int>uses(sz),mapped(sz,-1);
 for(int o:g.outputs)uses[o]++;
 for(int v=g.n+1;v<sz;v++){auto t=g.nodes[v];uses[t.a]++;if(t.op!=2)uses[t.b]++;}
 // Cut frontier propagation. At most 10 cuts retained per node, <=4 leaves each.
 std::vector<std::vector<Cut>>cuts(sz);
 for(int v=0;v<=g.n;v++)cuts[v].push_back({{v}});
 Builder b(g);std::iota(mapped.begin(),mapped.begin()+g.n+1,0);
 std::vector<unsigned char> live(sz,0);std::vector<int>st=g.outputs;
 while(!st.empty()){int v=st.back();st.pop_back();if(v<=g.n||live[v])continue;live[v]=1;st.push_back(g.nodes[v].a);if(g.nodes[v].op!=2)st.push_back(g.nodes[v].b);}
 for(int v=g.n+1;v<sz;v++){
  auto t=g.nodes[v];
  // Once the strictly bounded search budget is consumed, propagate original
  // nodes without continuing expensive cut enumeration.
  if(res.visited>=max_roots || expired()){
    if(expired())res.budget_hit=true;
    cuts[v].push_back({{v}});
    mapped[v]=b.add(t.op,mapped[t.a],t.op==2?0:mapped[t.b],c);
    continue;
  }
  std::vector<std::vector<int>> possibilities;
  if(t.op==2){for(auto &ca:cuts[t.a])possibilities.push_back(ca.leaves);}
  else for(auto &ca:cuts[t.a])for(auto &cb:cuts[t.b]){
   auto u=unite(ca.leaves,cb.leaves);if(u.size()<=4)possibilities.push_back(std::move(u));
  }
  std::sort(possibilities.begin(),possibilities.end(),[](auto&a,auto&b){
   if(a.size()!=b.size())return a.size()<b.size();return a<b;});
  possibilities.erase(std::unique(possibilities.begin(),possibilities.end()),possibilities.end());
  // Keep small and medium cuts; limit cost of enumeration.
  cuts[v].push_back({{v}});
  for(auto &u:possibilities){if(u.size()>4||u.empty())continue;cuts[v].push_back({u});if(cuts[v].size()>=10)break;}
  mapped[v]=b.add(t.op,mapped[t.a],t.op==2?0:mapped[t.b],c);
  if(!live[v]||res.visited>=max_roots||expired()){
   if(expired())res.budget_hit=true;continue;
  }
  res.visited++;
  int orig=mapped[v];int best=orig,best_delta=0; // strict negative delta required
  // Precise local cone cost. Speculative gates from rejected rewrites must NOT
  // be treated as zero-cost just because they already exist in the hash table.
  auto cone_cost=[&](int root,const std::vector<int>&lv)->int{
    std::unordered_set<int> frontier(lv.begin(),lv.end()),seen;
    std::vector<int> queue{root};int total=0;
    while(!queue.empty()){
      int a=queue.back();queue.pop_back();
      if(a<=g.n||frontier.count(a)||!seen.insert(a).second)continue;
      const auto& t=b.graph.nodes[a];total+=price(c,t.op);
      queue.push_back(t.a);if(t.op!=2)queue.push_back(t.b);
    }
    return total;
  };
  for(size_t ci=1;ci<cuts[v].size();ci++){
   if(expired()){res.budget_hit=true;break;}
   const auto &leaves=cuts[v][ci].leaves;
   if(leaves.size()<2||leaves.size()>4)continue;
   res.cuts++;
   // Only count gates proven private to this root under the old fanout graph.
   std::unordered_set<int> stop(leaves.begin(),leaves.end());
   std::function<int(int,bool)> gain=[&](int id,bool root)->int{
    if(id<=g.n||stop.count(id)||(!root&&uses[id]!=1))return 0;
    auto nd=g.nodes[id];return price(c,nd.op)+gain(nd.a,false)+(nd.op==2?0:gain(nd.b,false));
   };
   int reclaim=gain(v,true);
   if(reclaim<=0)continue;
   unsigned f;
   try{f=mask_for(g,v,leaves);}catch(...){continue;}
   std::vector<int>lv;for(int x:leaves)lv.push_back(mapped[x]);
   Emit e{b,c,lv};int k=leaves.size(),all=(1<<(1<<k))-1;
   if(int(f)==0||int(f)==all)continue;
   // Two greedy SOP/POS covers, single-literal factoring, two Shannon orders.
   const int variants=4*(1+2*k)+2;
   for(int variant=0;variant<variants;variant++){
    if(expired()){res.budget_hit=true;break;}
    int alt=-1;
    try{
     if(variant<4*(1+2*k)){
      int group=variant%(1+2*k),mode=variant/(1+2*k);
      bool pos=mode>=2;int pol=mode%2;
      alt=e.sop(k,pos?(unsigned)(all^f):f,pol,group==0?-1:group-1);
      if(pos&&alt>=0)alt=e.neg(alt);
     }else alt=e.shannon(k,f,variant%2);
    }catch(...){continue;}
    if(alt<0)continue;
    res.attempts++;
    int delta=cone_cost(alt,lv)-reclaim;
    if(delta<best_delta && b.ready[alt]<=b.ready[orig]){best=alt;best_delta=delta;}
   }
  }
  if(best!=orig){mapped[v]=best;res.chosen++;}
 }
 std::vector<int>outs;for(int x:g.outputs)outs.push_back(mapped[x]);
 res.graph=b.finish(std::move(outs));
 auto met=res.graph.metric(c);
 if(!met.valid||met.delay>target){res.graph=g;res.chosen=0;}
 return res;
}
} // namespace r60
