#pragma once
#include <algorithm>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <functional>
#include <numeric>
namespace round4_algebra {
struct Node{int op,a,b;};
struct K{int op,a,b;bool operator==(const K&k)const{return op==k.op&&a==k.a&&b==k.b;}};
struct H{size_t operator()(const K&k)const{unsigned long long x=(unsigned)k.op;x=x*1000003^(unsigned)k.a;x=x*1000003^(unsigned)k.b;return (size_t)x;}};
std::string rewrite(const std::string &net,int n,int m,int mode){
 std::vector<Node> old(n+1,{-1,0,0});std::vector<int> outputs;
 std::istringstream is(net);std::string line;
 while(std::getline(is,line)){
  if(line.find_first_not_of(" \t\r")==std::string::npos)continue;
  std::istringstream ss(line);std::string a,op;
  if(!(ss>>a))continue;
  if(!(ss>>op)) {outputs.push_back(std::stoi(a));break;}
  if(op!="NOT"&&op!="AND2"&&op!="OR2"){
   outputs.push_back(std::stoi(a));outputs.push_back(std::stoi(op));int v;while(ss>>v)outputs.push_back(v);break;
  }
  int id=std::stoi(a),u=-1,v=0;if(id!=int(old.size())||!(ss>>u)||u<0||u>=id)return {};
  if(op!="NOT"&&(!(ss>>v)||v<0||v>=id))return {};
  old.push_back({op=="AND2"?0:op=="OR2"?1:2,u,v});
 }
 if(int(outputs.size())!=m)return {};
 std::vector<int> map(old.size());std::iota(map.begin(),map.begin()+n+1,0);
 std::vector<Node> g(n+1,{-1,0,0});
 std::unordered_map<K,int,H> hs;hs.reserve(old.size()*2);
 auto raw=[&](int op,int a,int b)->int {
  if(op!=2&&a>b)std::swap(a,b);
  K k{op,a,b};auto it=hs.find(k);
  if(it!=hs.end())return it->second;
  int id=g.size();g.push_back({op,a,b});hs.emplace(k,id);return id;
 };
 int ONE=-1;
 std::function<int(int)> neg=[&](int a)->int {
  if(a==0){if(ONE<0)ONE=raw(2,0,0);return ONE;}
  if(ONE>=0&&a==ONE)return 0;
  if(a>n && g[a].op==2)return g[a].a;
  return raw(2,a,0);
 };
 auto inverse=[&](int a,int b)->bool{
  if(a==0&&ONE>=0&&b==ONE)return true;
  if(b==0&&ONE>=0&&a==ONE)return true;
  return (a>n&&g[a].op==2&&g[a].a==b)||(b>n&&g[b].op==2&&g[b].a==a);
 };
 std::function<int(int,int,int)> combine;
 combine=[&](int op,int a,int b)->int {
  if(op==0){
   if(a==0||b==0)return 0;
   if(ONE>=0&&a==ONE)return b;
   if(ONE>=0&&b==ONE)return a;
  }else{
   if(ONE>=0&&(a==ONE||b==ONE))return ONE;
   if(a==0)return b;
   if(b==0)return a;
  }
  if(a==b)return a;
  if(inverse(a,b))return op==0?0:neg(0);
  auto contains=[&](int v,int gop,int needle)->bool{
    return v>n && g[v].op==gop && (g[v].a==needle || g[v].b==needle);
  };
  // Absorption: a&(a|b)=a or a|(a&b)=a.
  if(contains(a,1-op,b))return b;
  if(contains(b,1-op,a))return a;
  // Complement absorption: a&(not(a)|b)=a&b.
  if(mode>=1){
   auto half_absorb=[&](int outer,int inner)->int{
     if(inner<=n||g[inner].op!=1-op)return -1;
     auto p=g[inner].a,q=g[inner].b;
     if(inverse(outer,p))return combine(op,outer,q);
     if(inverse(outer,q))return combine(op,outer,p);
     return -1;
   };
   int u=half_absorb(a,b);if(u>=0)return u;
   u=half_absorb(b,a);if(u>=0)return u;
  }
  // Boolean distributivity: (a&b)|(a&c)=a&(b|c), and dual.
  if(mode>=2 && a>n && b>n && g[a].op==1-op && g[b].op==1-op){
    int cands[2]={g[a].a,g[a].b};
    for(int common:cands){
      int otherA=(g[a].a==common?g[a].b:g[a].a);
      int otherB=-1;
      if(g[b].a==common)otherB=g[b].b;
      if(g[b].b==common)otherB=g[b].a;
      if(otherB<0)continue;
      return combine(1-op,common,combine(op,otherA,otherB));
    }
  }
  return raw(op,a,b);
 };
 for(int id=n+1;id<int(old.size());++id){
   auto u=old[id];map[id]=(u.op==2?neg(map[u.a]):combine(u.op,map[u.a],map[u.b]));
 }
 for(int &o:outputs)o=map[o];
 std::vector<unsigned char> live(g.size());std::vector<int> st=outputs;
 while(!st.empty()){
  int v=st.back();st.pop_back();if(v<=n||live[v])continue;
  live[v]=1;st.push_back(g[v].a);if(g[v].op!=2)st.push_back(g[v].b);
 }
 std::vector<int> ids(g.size());std::iota(ids.begin(),ids.begin()+n+1,0);
 int next=n+1;for(int v=n+1;v<int(g.size());++v)if(live[v])ids[v]=next++;
 std::ostringstream out;
 for(int v=n+1;v<int(g.size());++v)if(live[v]){
   auto u=g[v];out<<ids[v]<<' '<<(u.op==0?"AND2":u.op==1?"OR2":"NOT")<<' '<<ids[u.a];
   if(u.op!=2)out<<' '<<ids[u.b];
   out<<'\n';
 }
 for(int j=0;j<m;j++){if(j)out<<' ';out<<ids[outputs[j]];}out<<'\n';return out.str();
}
}
