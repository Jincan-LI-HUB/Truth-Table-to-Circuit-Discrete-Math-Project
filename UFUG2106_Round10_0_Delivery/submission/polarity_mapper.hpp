#pragma once
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <limits>
#include <numeric>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>
#include <queue>
#include <random>

namespace round4_phase {
struct Ref {int node, flip;};
struct Gate {int op; Ref a,b;};
struct Source {int consumer, flip;};
struct Key {int op,a,b;bool operator==(Key const&k)const{return op==k.op&&a==k.a&&b==k.b;}};
struct Hash {size_t operator()(Key const&k)const {uint64_t x=uint32_t(k.op);x=x*1000003^uint32_t(k.a);x=x*1000003^uint32_t(k.b);x^=x>>30;x*=0xbf58476d1ce4e5b9ULL;x^=x>>27;return x;}};
struct N {int op,a,b;};
class Engine {
 public:
 int n,m,AND,OR,NOT,da,dor,dn,target;
 std::vector<Gate> graph;
 std::vector<Ref> outputs;
 std::vector<std::vector<Source>> fanout;
 std::vector<std::vector<int>> output_demands;
 std::vector<int> phase;
 bool valid=false;
 Engine(std::string const &net,int n_,int m_,int aa,int dt_a,int ao,int dt_o,int an,int dt_n,int tgt)
  :n(n_),m(m_),AND(aa),OR(ao),NOT(an),da(dt_a),dor(dt_o),dn(dt_n),target(tgt){
  graph.resize(n+1); // const0 and inputs
  std::vector<Ref> alias(n+1);
  for(int j=0;j<=n;++j)alias[j]={j,0};
  std::istringstream in(net);std::string line;
  bool seen_outputs=false;
  while(std::getline(in,line)){
    if(line.find_first_not_of(" \r\t")==std::string::npos)continue;
    std::istringstream ss(line);std::string tok,type;
    if(!(ss>>tok))continue;
    if(!(ss>>type)){ // one-output case
      if(m!=1)return;
      int id=std::stoi(tok);if(id<0||id>=int(alias.size()))return;
      outputs.push_back(alias[id]);seen_outputs=true;break;
    }
    if(type=="NOT"||type=="AND2"||type=="OR2"){
      int id=std::stoi(tok),a=-1,b=-1;
      if(id!=int(alias.size())||!(ss>>a)||a<0||a>=id)return;
      if(type=="NOT"){
        std::string extra;if(ss>>extra)return;
        Ref r=alias[a];r.flip^=1;alias.push_back(r);
      }else{
        if(!(ss>>b)||b<0||b>=id)return;
        std::string extra;if(ss>>extra)return;
        int node=graph.size();graph.push_back({type=="AND2"?0:1,alias[a],alias[b]});alias.push_back({node,0});
      }
    }else{ // output identifiers
      int id=std::stoi(tok);if(id<0||id>=int(alias.size()))return;
      outputs.push_back(alias[id]);
      try{int v=std::stoi(type);if(v<0||v>=int(alias.size()))return;outputs.push_back(alias[v]);}catch(...){return;}
      int v;while(ss>>v){if(v<0||v>=int(alias.size()))return;outputs.push_back(alias[v]);}
      seen_outputs=true;break;
    }
  }
  if(!seen_outputs||int(outputs.size())!=m)return;
  fanout.resize(graph.size());output_demands.resize(graph.size());phase.assign(graph.size(),0);
  for(int v=n+1;v<int(graph.size());++v){
    auto const &g=graph[v];
    fanout[g.a.node].push_back({v,g.a.flip});
    fanout[g.b.node].push_back({v,g.b.flip});
  }
  for(auto const &r:outputs)output_demands[r.node].push_back(r.flip);
  valid=true;
 }
 int p(int v,int changed,int newp)const{return v==changed?newp:phase[v];}
 int missing(int src,int changed=-1,int newp=0)const{
   int ps=p(src,changed,newp);
   for(const auto &f:fanout[src])if((p(f.consumer,changed,newp)^f.flip)!=ps)return 1;
   for(int desired:output_demands[src])if(desired!=ps)return 1;
   return 0;
 }
 long long score() const{
   long long cost=0;
   for(int v=n+1;v<int(graph.size());++v)cost+=(graph[v].op^phase[v])?OR:AND;
   for(int v=0;v<int(graph.size());++v)cost+=NOT*missing(v);
   return cost;
 }
 long long delta(int v)const{
   int newp=phase[v]^1;
   long long d=(graph[v].op^newp ? OR:AND)-(graph[v].op^phase[v] ? OR:AND);
   int impacted[3]={v,graph[v].a.node,graph[v].b.node};
   for(int j=0;j<3;++j){int s=impacted[j];bool already=false;for(int k=0;k<j;++k)if(impacted[k]==s)already=true;
     if(!already)d+=NOT*(missing(s,v,newp)-missing(s));}
   return d;
 }
 void improve(int passes=8,bool reverse=false){
   // Coordinate descent on a global polarity cost surrogate. No effect on functionality.
   std::vector<int> seq(graph.size()-n-1);
   std::iota(seq.begin(),seq.end(),n+1);
   if(reverse)std::reverse(seq.begin(),seq.end());
   for(int step=0;step<passes;++step){
     bool change=false;
     for(int v:seq){if(delta(v)<0){phase[v]^=1;change=true;}}
     if(!change)break;
     std::reverse(seq.begin(),seq.end());
   }
 }
 std::string construct()const{
   std::vector<N> gates(n+1,{-1,0,0});
   std::vector<int> ready(n+1,0),mapped(graph.size());
   std::iota(mapped.begin(),mapped.begin()+n+1,0);
   std::unordered_map<Key,int,Hash> lookup;lookup.reserve(graph.size()*3);
   auto raw=[&](int op,int a,int b){
     if(op!=2&&a>b)std::swap(a,b);
     Key k{op,a,b};auto it=lookup.find(k);
     if(it!=lookup.end())return it->second;
     int id=gates.size();gates.push_back({op,a,b});
     ready.push_back((op==2?ready[a]:std::max(ready[a],ready[b]))+(op==0?da:op==1?dor:dn));
     lookup.emplace(k,id);return id;
   };
   int one=-1;
   auto ensure_one=[&](){if(one<0)one=raw(2,0,0);return one;};
   auto neg=[&](int a){
     if(a==0)return ensure_one();
     if(one>=0&&a==one)return 0;
     if(a>n&&gates[a].op==2)return gates[a].a;
     return raw(2,a,0);
   };
   auto opposite=[&](int a,int b){
     if(a==0&&one>=0&&b==one)return true;
     if(b==0&&one>=0&&a==one)return true;
     return (a>n&&gates[a].op==2&&gates[a].a==b)||
            (b>n&&gates[b].op==2&&gates[b].a==a);
   };
   auto combine=[&](int op,int a,int b){
     if(op==0){
       if(a==0||b==0)return 0;
       if(one>=0&&a==one)return b;
       if(one>=0&&b==one)return a;
       if(a==b)return a;
       if(opposite(a,b))return 0;
     }else{
       if(one>=0&&(a==one||b==one))return one;
       if(a==0)return b;
       if(b==0)return a;
       if(a==b)return a;
       if(opposite(a,b))return ensure_one();
     }
     return raw(op,a,b);
   };
   for(int v=n+1;v<int(graph.size());++v){
     const auto &g=graph[v];int pv=phase[v];
     int wantA=pv^g.a.flip, wantB=pv^g.b.flip;
     int a=mapped[g.a.node],b=mapped[g.b.node];
     if(wantA!=phase[g.a.node])a=neg(a);
     if(wantB!=phase[g.b.node])b=neg(b);
     mapped[v]=combine(g.op^pv,a,b);
   }
   std::vector<int> out;
   for(const auto &r:outputs){int v=mapped[r.node];if(r.flip!=phase[r.node])v=neg(v);out.push_back(v);}
   std::vector<uint8_t> alive(gates.size());std::vector<int> st=out;
   while(!st.empty()){
     int v=st.back();st.pop_back();if(v<=n||alive[v])continue;
     alive[v]=1;st.push_back(gates[v].a);if(gates[v].op!=2)st.push_back(gates[v].b);
   }
   std::vector<int> ids(gates.size());std::iota(ids.begin(),ids.begin()+n+1,0);
   int next=n+1;
   for(int v=n+1;v<int(gates.size());++v)if(alive[v])ids[v]=next++;
   std::ostringstream ss;
   for(int v=n+1;v<int(gates.size());++v)if(alive[v]){
      auto &g=gates[v];ss<<ids[v]<<' '<<(g.op==0?"AND2":g.op==1?"OR2":"NOT")<<' '<<ids[g.a];
      if(g.op!=2)ss<<' '<<ids[g.b];
      ss<<'\n';
   }
   for(int j=0;j<m;++j){if(j)ss<<' ';ss<<ids[out[j]];}ss<<'\n';
   return ss.str();
 }
};
} // namespace round4_phase
