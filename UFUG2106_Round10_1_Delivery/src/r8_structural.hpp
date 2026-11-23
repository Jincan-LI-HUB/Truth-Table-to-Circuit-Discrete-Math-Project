#pragma once
// Round 8 experimental algebraic, DAG-aware multi-choice optimizer.
// All individual identities are universally valid Boolean equalities.
// An alternative is accepted only after exact *whole live DAG* area/delay evaluation.
#include <cstdint>
#include "typed_netgraph.hpp"
#include <chrono>
#include <climits>
#include <string>
#include <functional>
#include <unordered_set>

namespace r8 {
using r51::Graph; using r51::Builder; using r51::Costs;
struct Counts {long long absorption=0, factoring=0, expansion=0, phase=0, attempted=0;};
struct Experiment {Graph graph; Counts counts; std::string mode; double milliseconds=0;};
inline int area_cost(const Costs& c,int op){return op==0?c.aa:op==1?c.ao:c.an;}

// modes: absorb, factor, factor_relaxed, phase, reuse, combined, combined_relaxed
inline Experiment rewrite(const Graph& g, const Costs& c, const std::string& mode, int target){
  auto started=std::chrono::steady_clock::now();
  Experiment result; result.mode=mode;
  if(!g.valid){return result;}
  Builder b(g);
  std::vector<int> mapped(g.nodes.size());
  for(int i=0;i<=g.n;++i)mapped[i]=i;
  std::vector<int> uses(g.nodes.size(),0),needed(g.nodes.size(),INT_MAX/4);
  for(int id=g.n+1;id<int(g.nodes.size());++id){
    auto x=g.nodes[id]; ++uses[x.a]; if(x.op!=2)++uses[x.b];
  }
  for(int o:g.outputs) {++uses[o];needed[o]=std::min(needed[o],target);}
  for(int id=int(g.nodes.size())-1;id>g.n;--id){
    auto x=g.nodes[id];
    if(needed[id]>=INT_MAX/4)continue;
    int v=needed[id]-(x.op==0?c.da:x.op==1?c.dor:c.dn);
    needed[x.a]=std::min(needed[x.a],v);
    if(x.op!=2)needed[x.b]=std::min(needed[x.b],v);
  }
  auto node=[&](int v)->r51::Node{return v<=g.n?r51::Node{-1,0,0}:b.graph.nodes[v];};
  auto isone=[&](int v)->bool{return v>g.n&&b.graph.nodes[v].op==2&&b.graph.nodes[v].a==0;};
  std::function<int(int)> neg=[&](int v)->int{
    if(v==0)return b.add(2,0,0,c);
    if(isone(v))return 0;
    auto t=node(v);
    if(t.op==2)return t.a;
    return b.add(2,v,0,c);
  };
  auto inverse=[&](int a,int z)->bool{return (node(a).op==2&&node(a).a==z)||(node(z).op==2&&node(z).a==a);};
  std::function<int(int,int,int)> basic=[&](int op,int a,int z)->int{
    if(op==2)return neg(a);
    if(a==z)return a;
    if(inverse(a,z))return op==0?0:neg(0);
    if(op==0){
      if(a==0||z==0)return 0;
      if(isone(a))return z; if(isone(z))return a;
    }else{
      if(a==0)return z; if(z==0)return a;
      if(isone(a)||isone(z))return neg(0);
    }
    // Absorption: x & (x | y) = x; x | (x & y) = x
    if(mode!="phase"){
      auto la=node(a),lz=node(z);int opp=1-op;
      if(la.op==opp && (la.a==z||la.b==z)){result.counts.absorption++;return z;}
      if(lz.op==opp && (lz.a==a||lz.b==a)){result.counts.absorption++;return a;}
    }
    return b.add(op,a,z,c);
  };
  bool factor=(mode=="factor"||mode=="factor_relaxed"||mode=="combined"||mode=="combined_relaxed");
  bool use_phase=(mode=="phase"||mode=="combined"||mode=="combined_relaxed");
  bool expand=(mode=="reuse"||mode=="combined_relaxed");
  bool relaxed=(mode=="factor_relaxed"||mode=="combined_relaxed");
  for(int id=g.n+1;id<int(g.nodes.size());++id){
    const auto x=g.nodes[id];int a=mapped[x.a],z=x.op==2?0:mapped[x.b];
    if(x.op==2){mapped[id]=neg(a);continue;}
    int direct=basic(x.op,a,z),chosen=direct;
    if(factor){
      auto l=node(a),r=node(z);int opp=1-x.op;
      if(l.op==opp && r.op==opp){
        int common=-1,la=-1,rb=-1;
        int vs[2]={l.a,l.b},ws[2]={r.a,r.b};
        for(int i=0;i<2&&common<0;++i)for(int j=0;j<2;++j)
          if(vs[i]==ws[j]){common=vs[i];la=vs[1-i];rb=ws[1-j];break;}
        if(common>=0){
          // (x&y)|(x&z) = x&(y|z), and its dual.
          int inner=basic(x.op,la,rb);
          int alternative=basic(opp,common,inner);
          result.counts.attempted++;
          // In conservative mode, don't discard a shared fanout cone;
          // 'relaxed' allows temporary cost changes evaluated globally.
          bool old_private=(uses[x.a]==1 && uses[x.b]==1);
          if((relaxed||old_private) && b.ready[alternative]<=needed[id]){
            chosen=alternative;result.counts.factoring++;
          }
        }
      }
    }
    if(expand && chosen==direct){
      // x&(y|z) = (x&y)|(x&z).  Try only if an existing divisor
      // already computes at least one expanded product, avoiding blind expansion.
      int opp=1-x.op;
      auto l=node(a),r=node(z);
      int left=a,right=z;
      r51::Node distrib{-1,0,0};
      if(l.op==opp){distrib=l;right=z;}
      else if(r.op==opp){distrib=r;right=a;}
      if(distrib.op==opp){
        int t1a=distrib.a,t1b=right,t2a=distrib.b,t2b=right;
        if(t1a>t1b)std::swap(t1a,t1b);
        if(t2a>t2b)std::swap(t2a,t2b);
        bool found=b.intern.count({x.op,t1a,t1b})||b.intern.count({x.op,t2a,t2b});
        if(found){
          int u=basic(x.op,distrib.a,right),v=basic(x.op,distrib.b,right);
          int candidate=basic(opp,u,v);
          result.counts.attempted++;
          if(b.ready[candidate]<=needed[id]){chosen=candidate;result.counts.expansion++;}
        }
      }
    }
    if(use_phase && chosen==direct){
      int p=x.op;
      // De Morgan; NOT has explicit cost, so compare weighted *local* area.
      int saved=area_cost(c,p),altcost=area_cost(c,1-p)+3*c.an;
      if(altcost<saved){
        int alt=neg(basic(1-p,neg(a),neg(z)));
        result.counts.attempted++;
        if(b.ready[alt]<=needed[id]){chosen=alt;result.counts.phase++;}
      }
    }
    mapped[id]=chosen;
  }
  std::vector<int> roots;roots.reserve(g.outputs.size());
  for(int o:g.outputs)roots.push_back(mapped[o]);
  result.graph=b.finish(std::move(roots));
  result.milliseconds=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-started).count();
  return result;
}
} // namespace r8
