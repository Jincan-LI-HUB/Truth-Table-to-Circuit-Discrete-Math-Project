#ifndef ROUND5_CACHE
#define ROUND5_CACHE 1
#endif
#include "polarity_mapper.hpp"
#include "algebraic_mapper.hpp"
#include "typed_netgraph.hpp"
#include "r8_structural.hpp"
#include "r81_cut.hpp"
#include "r82_archive.hpp"
#include "r82_cut.hpp"
#include "r83_cut.hpp"
#include "r84_cut.hpp"
#include "r821_resource.hpp"
#include <bits/stdc++.h>
using namespace std;
struct BKey {int v,lo,hi;bool operator==(const BKey&o)const{return v==o.v && lo==o.lo && hi==o.hi;}};
struct H3 {size_t operator()(const BKey&k)const { uint64_t z=((uint64_t)(unsigned)k.v<<55)^((uint64_t)(unsigned)k.lo<<26)^(unsigned)k.hi; z^=z>>30;z*=0xbf58476d1ce4e5b9ULL;z^=z>>27;z*=0x94d049bb133111ebULL;return z^(z>>31);}};
struct BNode{int v,lo,hi;};
struct Gate{string type;int a,b;};
struct GKey{int t,a,b;bool operator==(const GKey&o)const{return t==o.t&&a==o.a&&b==o.b;}};
struct HKey{size_t operator()(const GKey &k)const{return H3{}({k.t,k.a,k.b});}};
struct Opt {string order;bool fast, rewrite, expand;int cubemode,margin;bool affine=false;};
struct CandidateTimeout {};

// Per-invocation immutable truth-table cache. A single executable processes
// exactly one input case, but tries many synthesis configurations on it.
struct CachedTruth {
    int n=0,m=0,aa=0,da=0,ao=0,doo=0,an=0,dn=0,D=0;
    std::vector<unsigned char> T;
    std::vector<unsigned long long> influence;
    bool valid=false;
};
const CachedTruth& shared_truth(const std::string& path) {
    static CachedTruth data;
    static std::string last;
    if(last==path) return data;
    last=path;
    data=CachedTruth{};
    std::ifstream in(path);
    if(!in || !(in>>data.n>>data.m) || data.n<1 || data.n>22 || data.m<1)
        return data;
    size_t N=1ull<<data.n;
    data.T.resize(N*size_t(data.m));
    std::string bits;
    for(size_t i=0;i<N;i++) {
        if(!(in>>bits) || bits.size()!=size_t(data.m))return data;
        for(int j=0;j<data.m;j++)data.T[i*data.m+j]=bits[j]-'0';
    }
    if(!(in>>data.aa>>data.da>>data.ao>>data.doo>>data.an>>data.dn>>data.D))
        return data;
    data.influence.assign(data.n,0);
    for(int v=0;v<data.n;v++) {
        size_t step=1ull<<(data.n-1-v);
        for(size_t start=0;start<N;start+=2*step) {
            for(size_t k=0;k<step;k++) {
                size_t a=(start+k)*data.m,b=(start+k+step)*data.m;
                for(int j=0;j<data.m;j++)
                    data.influence[v]+=(data.T[a+j]!=data.T[b+j]);
            }
        }
    }
    data.valid=true;
    return data;
}


// Compile invariant Quine-McCluskey / greedy-cover choices once per
// truth-table invocation. Mapping to gates is still candidate-specific.
struct R5Cube {int val,mask;};
struct R5CoverPlan {int kind=-1; vector<int> support; vector<R5Cube> chosen;};
const std::vector<std::array<R5CoverPlan,2>>& shared_covers(const CachedTruth &data){
 static std::vector<std::array<R5CoverPlan,2>> cache;
 static const CachedTruth* last_data=nullptr;
 static const unsigned char* last_table=nullptr;
 if(last_data==&data && last_table==data.T.data())return cache;
 last_data=&data;last_table=data.T.data();
 cache.assign(data.m,{});
 if(data.n>13)return cache;
 const bool r7_legacy_merge=[](){const char*p=std::getenv("UFUG_R7_LEGACY_MERGE");return p && *p=='1';}();
 const bool r7_legacy_cover=[](){const char*p=std::getenv("UFUG_R7_LEGACY_COVER");return p && *p=='1';}();
 unsigned long long r7_merge_probes=0,r7_cover_probes=0,r7_merge_rounds=0;
 double r7_merge_ms=0.0,r7_cover_ms=0.0;
 const int n=data.n,m=data.m,N=1<<n;
 const auto &T=data.T;
 for(int j=0;j<m;j++){
  vector<int> support;
  for(int v=0;v<n;v++){
   int step=1<<(n-1-v);bool flag=false;
   for(int start=0;start<N && !flag;start+=step*2)
    for(int z=0;z<step;z++)if(T[((size_t)start+z)*m+j]!=T[((size_t)start+step+z)*m+j]){flag=true;break;}
   if(flag)support.push_back(v);
  }
  int k=(int)support.size();
  if(k>9)continue;
  int Q=1<<k;vector<uint8_t> tt(Q);
  for(int i=0;i<Q;i++){
   size_t orig=0;
   for(int b=0;b<k;b++)if(i&(1<<b))orig|=1ull<<(n-1-support[k-1-b]);
   tt[i]=T[orig*m+j];
  }
  for(int goal=0;goal<=1;goal++){
   R5CoverPlan &plan=cache[j][goal];
   plan.support=support;
   vector<R5Cube> cur;cur.reserve(Q);
   for(int i=0;i<Q;i++)if(tt[i]==goal)cur.push_back({i,Q-1});
   if(cur.empty()){plan.kind=0;continue;}
   if((int)cur.size()==Q){plan.kind=1;continue;}
   plan.kind=2;
   vector<R5Cube> prime;
   const auto r7_merge_start = std::chrono::steady_clock::now();
   while(!cur.empty()){
    ++r7_merge_rounds;
    vector<char> used(cur.size());vector<R5Cube> nxt;
    unordered_set<unsigned long long> hash;
    if(r7_legacy_merge){
     // A/B ablation: the exact Round 5.1 quadratic loop.
     for(size_t a=0;a<cur.size();a++)for(size_t b=a+1;b<cur.size();b++){
      ++r7_merge_probes;
      if(cur[a].mask!=cur[b].mask)continue;
      int diff=(cur[a].val^cur[b].val)&cur[a].mask;
      if(__builtin_popcount((unsigned)diff)!=1)continue;
      used[a]=used[b]=1;
      int mk=cur[a].mask^diff,v=cur[a].val&mk;
      auto id=((unsigned long long)(unsigned)mk<<32)|(unsigned)v;
      if(hash.insert(id).second)nxt.push_back({v,mk});
     }
    }else{
     // For a fixed mask, two normalized cubes merge iff their
     // values differ by one bit set in the mask. O(k*S) expected.
     unordered_map<unsigned long long,size_t> where;
     where.reserve(cur.size()*2+1);
     for(size_t a=0;a<cur.size();a++){
      auto key=((unsigned long long)(unsigned)cur[a].mask<<32)|
               (unsigned)cur[a].val;
      where.emplace(key,a);
     }
     for(size_t a=0;a<cur.size();a++){
      int mask=cur[a].mask,val=cur[a].val;
      for(unsigned bits=(unsigned)mask;bits;bits&=(bits-1)){
       unsigned bit=bits&(~bits+1U);
       auto key=((unsigned long long)(unsigned)mask<<32)|
                (unsigned)(val^(int)bit);
       ++r7_merge_probes;
       auto it=where.find(key);
       if(it==where.end()||it->second<=a)continue;
       size_t b=it->second;
       used[a]=used[b]=1;
       int mk=mask^(int)bit,v=val&mk;
       auto id=((unsigned long long)(unsigned)mk<<32)|(unsigned)v;
       if(hash.insert(id).second)nxt.push_back({v,mk});
      }
     }
    }
    for(size_t a=0;a<cur.size();a++)if(!used[a])prime.push_back(cur[a]);
    cur.swap(nxt);
   }
   r7_merge_ms+=std::chrono::duration<double,std::milli>(
     std::chrono::steady_clock::now()-r7_merge_start).count();
   sort(prime.begin(),prime.end(),[](R5Cube a,R5Cube b){return tie(a.mask,a.val)<tie(b.mask,b.val);});
   prime.erase(unique(prime.begin(),prime.end(),[](R5Cube a,R5Cube b){return a.mask==b.mask&&a.val==b.val;}),prime.end());
   const auto r7_cover_start=std::chrono::steady_clock::now();
   if(r7_legacy_cover){
    // A/B ablation: preserve Round 5.1 greedy scan verbatim.
    vector<char> uncovered(Q,0);int remaining=0;
    for(int i=0;i<Q;i++)if(tt[i]==goal){uncovered[i]=1;remaining++;}
    while(remaining){
     double best=-1;int which=-1;
     for(int t=0;t<(int)prime.size();t++){
      int gains=0;
      for(int i=0;i<Q;i++){
       ++r7_cover_probes;
       if(uncovered[i] && (i&prime[t].mask)==prime[t].val)gains++;
      }
      if(!gains)continue;
      int cost=max(1,__builtin_popcount((unsigned)prime[t].mask));
      double score=double(gains)/(0.4+cost);
      if(score>best){best=score;which=t;}
     }
     if(which<0)throw runtime_error("cover failed");
     auto q=prime[which];plan.chosen.push_back(q);
     for(int i=0;i<Q;i++)if(uncovered[i] && (i&q.mask)==q.val){uncovered[i]=0;remaining--;}
    }
   }else{
    // One bit per minterm; preserve exact gains and original tie-breaking.
    const int words=(Q+63)/64;
    vector<unsigned long long> remaining_bits(words,0);
    int remaining=0;
    for(int i=0;i<Q;i++)if(tt[i]==goal){
     remaining_bits[i>>6]|=1ULL<<(i&63);remaining++;
    }
    vector<vector<unsigned long long>> covers(
      prime.size(),vector<unsigned long long>(words,0));
    for(int t=0;t<(int)prime.size();t++){
     for(int i=0;i<Q;i++)if((i&prime[t].mask)==prime[t].val)
      covers[t][i>>6]|=1ULL<<(i&63);
    }
    while(remaining){
     double best=-1;int which=-1;
     for(int t=0;t<(int)prime.size();t++){
      int gains=0;
      for(int w=0;w<words;w++){
       ++r7_cover_probes;
       gains+=__builtin_popcountll(remaining_bits[w]&covers[t][w]);
      }
      if(!gains)continue;
      int cost=max(1,__builtin_popcount((unsigned)prime[t].mask));
      double score=double(gains)/(0.4+cost);
      if(score>best){best=score;which=t;}
     }
     if(which<0)throw runtime_error("cover failed");
     plan.chosen.push_back(prime[which]);
     for(int w=0;w<words;w++){
      unsigned long long removed=remaining_bits[w]&covers[which][w];
      remaining-=__builtin_popcountll(removed);
      remaining_bits[w]&=~removed;
     }
    }
   }
   r7_cover_ms+=std::chrono::duration<double,std::milli>(
     std::chrono::steady_clock::now()-r7_cover_start).count();
  }
 }
 if(const char* p=std::getenv("UFUG_ROUND5_PROFILE"))if(*p=='1'){
  std::cerr<<"R7_STAGE stage=covers merge_mode="<<(r7_legacy_merge?"legacy":"neighbor")
   <<" greedy_mode="<<(r7_legacy_cover?"legacy":"bitset")
   <<" merge_ms="<<std::fixed<<std::setprecision(3)<<r7_merge_ms
   <<" greedy_ms="<<r7_cover_ms
   <<" merge_probes="<<r7_merge_probes
   <<" greedy_probes="<<r7_cover_probes
   <<" merge_rounds="<<r7_merge_rounds<<"\n";
 }
 return cache;
}
string run_synth(const string &input,const Opt &opt,
  chrono::steady_clock::time_point deadline=chrono::steady_clock::time_point::max()){
 uint64_t steps=0;
 auto checkpoint=[&](){
   if(deadline!=chrono::steady_clock::time_point::max() &&
      ((++steps & 1023ULL)==0) && chrono::steady_clock::now()>deadline)
      throw CandidateTimeout{};
 };
 const CachedTruth &data=shared_truth(input);
 if(!data.valid)return {};
 std::ostringstream out;
 const int n=data.n,m=data.m;
 const size_t N=1ull<<n;
 const std::vector<unsigned char> &T=data.T;
 const int aa=data.aa,da=data.da,ao=data.ao,doo=data.doo,an=data.an,dn=data.dn;
 // Round 5: build a ROBDD once per identical variable ordering, and reuse
 // its immutable structure across mapping configurations. Only the repeated
 // influence-desc order is cached. A bounded node cap avoids holding large
 // BDDs while a different order is being constructed.
 using Time=std::chrono::steady_clock;
 const auto bdd_started=Time::now();
 struct FrozenGraph {
   vector<BNode> nodes;
   vector<int> perm, roots;
   vector<uint64_t> af;
 };
 static std::shared_ptr<const FrozenGraph> shared_desc;
 static string shared_path;
 std::shared_ptr<const FrozenGraph> graph;
 bool bdd_hit=false;
#if ROUND5_CACHE
 if(opt.order=="influence-desc" && shared_desc && shared_path==input) {
    graph=shared_desc;
    bdd_hit=true;
 }
#endif
 if(!graph) {
  auto current=std::make_shared<FrozenGraph>();
  auto &nodes=current->nodes;
  auto &perm=current->perm;
  auto &roots=current->roots;
  nodes.reserve(N);nodes.push_back({-1,0,0});
  unordered_map<BKey,int,H3> cache;
  cache.reserve(min((size_t)N*2,(size_t)5000000));
  perm.resize(n);iota(perm.begin(),perm.end(),0);
  string order=opt.order;
  if(order=="reverse")reverse(perm.begin(),perm.end());
  if(order=="rotate")rotate(perm.begin(),perm.begin()+n/2,perm.end());
  if(order=="influence-asc"||order=="influence-desc"){
   const std::vector<unsigned long long> &influence=data.influence;
   stable_sort(perm.begin(),perm.end(),[&](int a,int b){return order=="influence-asc"?influence[a]<influence[b]:influence[a]>influence[b];});
  }
  vector<size_t> orig(N);
  for(size_t z=1;z<N;z++){
     checkpoint();int bit=__builtin_ctzll(z);
     orig[z]=orig[z&(z-1)]|(1ull<<(n-1-perm[n-1-bit]));
  }
  roots.resize(m);
  vector<int> cur(N),next;
  for(int j=0;j<m;j++){
   cur.resize(N);
   for(size_t i=0;i<N;i++)cur[i]=T[orig[i]*m+j];
   size_t count=N;
   for(int v=n-1;v>=0;v--){
    next.resize(count/2);
    for(size_t k=0;k<count/2;k++){
     checkpoint();int lo=cur[2*k],hi=cur[2*k+1];
     if(lo==hi){next[k]=lo;continue;}
     int flip=(hi&1);int normlo=lo^flip,normhi=hi^flip;
     BKey key={v,normlo,normhi};auto it=cache.find(key);
     if(it!=cache.end()){next[k]=it->second^flip;continue;}
     int id=nodes.size();
     if(deadline!=chrono::steady_clock::time_point::max() && id>600000)throw CandidateTimeout{};
     nodes.push_back({v,normlo,normhi});cache.emplace(key,id<<1);next[k]=(id<<1)^flip;
    }
    cur.swap(next);count/=2;
   }
   roots[j]=cur[0];
  }
  // The affine table is a pure function of ROBDD structure and bit ordering.
  const uint64_t cb=(1ULL<<n), BAD=~0ULL;
  auto &af=current->af;
  af.assign(nodes.size()*2,BAD);
  af[0]=0;af[1]=cb;
  for(size_t k=1;k<nodes.size();k++){
   const auto &nd=nodes[k];
   if(af[nd.lo]!=BAD && af[nd.hi]!=BAD && (af[nd.lo]^af[nd.hi])==cb){
     af[2*k]=af[nd.lo]^(1ULL<<perm[nd.v]);
     af[2*k+1]=af[2*k]^cb;
   }
  }
  graph=current;
#if ROUND5_CACHE
  if(opt.order=="influence-desc" && n<=18 && nodes.size()<=80000){
    shared_path=input;
    shared_desc=std::move(current);
  }
#endif
 }
 const auto &nodes=graph->nodes;
 const auto &roots=graph->roots;
 const auto &perm=graph->perm;
 const uint64_t cb=(1ULL<<n), BAD=~0ULL;
 const auto &af=graph->af;
 const auto bdd_finished=Time::now();
 if(auto p=std::getenv("UFUG_ROUND5_PROFILE"))if(*p=='1') {
   std::cerr<<"R5_STAGE stage=bdd order="<<opt.order
      <<" cache_hit="<<bdd_hit<<" nodes="<<nodes.size()
      <<" elapsed_ms="<<std::fixed<<std::setprecision(3)
      <<std::chrono::duration<double,std::milli>(bdd_finished-bdd_started).count()<<"\n";
 }
 // Emit gates with structural sharing, constant folding, and NOT sharing.
 vector<Gate> gates;
 unordered_map<GKey,int,HKey> gcache;gcache.reserve(nodes.size()*2);
 vector<int> ready(n+1);int A=0;
 auto mk=[&](int t,int a,int b)->int {checkpoint();if(t!=2&&a>b)swap(a,b); GKey k{t,a,b}; auto it=gcache.find(k);if(it!=gcache.end())return it->second;
  int id=n+1+(int)gates.size();gates.push_back({t==0?"AND2":t==1?"OR2":"NOT",a,b}); gcache.emplace(k,id);A+=(t==0?aa:t==1?ao:an);ready.push_back((t==2?ready[a]:max(ready[a],ready[b]))+(t==0?da:t==1?doo:dn));return id;};
 int ONE=mk(2,0,0); // canonical 1
 function<int(int)> neg=[&](int a)->int{
  if(a==0)return ONE;
  if(a==ONE)return 0;
  auto it=gcache.find({2,a,0});if(it!=gcache.end())return it->second;
  if(a>n){Gate &g=gates[a-(n+1)];if(g.type=="NOT")return g.a;}
  return mk(2,a,0);
 };
 auto areInverse=[&](int a,int b)->bool {
   if((a==0&&b==ONE)||(a==ONE&&b==0))return true;
   if(a>n && gates[a-(n+1)].type=="NOT" && gates[a-(n+1)].a==b)return true;
   if(b>n && gates[b-(n+1)].type=="NOT" && gates[b-(n+1)].a==a)return true;
   return false;
 };
 function<int(int,int)> land=[&](int a,int b)->int{if(a==0||b==0)return 0;if(a==ONE)return b;if(b==ONE)return a;if(a==b)return a;if(areInverse(a,b))return 0;if((opt.rewrite && aa>ao+3*an) || opt.fast){
  int na=neg(a),nb=neg(b);int limit=0;
  limit=0;
  if((opt.fast?max(ready[na],ready[nb])+doo+dn<max(ready[a],ready[b])+da:max(ready[na],ready[nb])+doo+dn<=max(ready[a],ready[b])+da+limit))return neg(mk(1,na,nb));
  }return mk(0,a,b);};
 function<int(int,int)> lor=[&](int a,int b)->int{if(a==ONE||b==ONE)return ONE;if(a==0)return b;if(b==0)return a;if(a==b)return a;if(areInverse(a,b))return ONE;if((opt.rewrite && ao>aa+3*an) || opt.fast){
  int na=neg(a),nb=neg(b);int limit=0;
  limit=0;
  if((opt.fast?max(ready[na],ready[nb])+da+dn<max(ready[a],ready[b])+doo:max(ready[na],ready[nb])+da+dn<=max(ready[a],ready[b])+doo+limit))return neg(mk(0,na,nb));
  }return mk(1,a,b);};

 function<int(int,int)> makeXor=[&](int a,int b)->int{
   if(a==b)return 0;
   if(areInverse(a,b))return ONE;
   int p=land(lor(a,b),neg(land(a,b)));
   int q=lor(land(a,neg(b)),land(neg(a),b));
   if(opt.fast)return ready[p]<=ready[q]?p:q;
   return ready[p]<=ready[q]?p:q;
 };
 auto makeAffine=[&](uint64_t mask)->int{
   using Item=pair<int,int>;
   priority_queue<Item,vector<Item>,greater<Item>> pq;
   for(int v=0;v<n;v++)if(mask&(1ULL<<v))pq.emplace(0,v+1);
   while(pq.size()>1){int a=pq.top().second;pq.pop();int b=pq.top().second;pq.pop();int c=makeXor(a,b);pq.emplace(ready[c],c);}
   int root=pq.empty()?0:pq.top().second;
   return (mask&cb)?neg(root):root;
 };
 vector<int> done(nodes.size()*2,-1);done[0]=0;done[1]=ONE;
 function<int(int)> build=[&](int id)->int {
  checkpoint();if(done[id]>=0)return done[id];
  if(opt.affine && af[id]!=BAD)return done[id]=makeAffine(af[id]);
  if((id&1) && done[id^1]>=0)return done[id]=neg(done[id^1]);
  auto node=nodes[id>>1];int x=perm[node.v]+1;
  int lo=build(node.lo^(id&1)),hi=build(node.hi^(id&1)),result;
  if(lo==hi)result=lo;
  else if(lo==0)result=land(x,hi);
  else if(hi==0)result=land(neg(x),lo);
  else if(lo==ONE)result=lor(neg(x),hi);
  else if(hi==ONE)result=lor(x,lo);
  else result=lor(land(neg(x),lo),land(x,hi));
  // Experimental two-level Shannon expansion, compare by local arrival time.
  if(opt.expand && node.lo > 1 && node.hi > 1) {
    auto combine_balanced=[&](vector<int> v,bool isor)->int {
      if(v.empty())return isor?0:ONE;
      auto cmp=[&](int a,int b){return ready[a]>ready[b];};
      priority_queue<int,vector<int>,decltype(cmp)> pq(cmp);
      for(int a:v)pq.push(a);
      while(pq.size()>1){int a=pq.top();pq.pop();int b=pq.top();pq.pop();pq.push(isor?lor(a,b):land(a,b));}
      return pq.top();
    };
    vector<int> terms;
    for(int side=0;side<2;side++){
      int child=(side?node.hi:node.lo)^(id&1);
      int rootlit=side?x:neg(x);
      if(child <= 1) { if(child==1)terms.push_back(rootlit);continue; }
      auto g=nodes[child>>1];int y=perm[g.v]+1;
      for(int side2=0;side2<2;side2++){
        int leaf=build((side2?g.hi:g.lo)^(child&1));
        if(leaf==0)continue;
        vector<int> vs={rootlit,side2?y:neg(y)};
        if(leaf!=ONE)vs.push_back(leaf);
        terms.push_back(combine_balanced(vs,false));
      }
    }
    int expanded=combine_balanced(terms,true);
    int slack=opt.margin;
    if(ready[expanded]+slack < ready[result])result=expanded;
  }
  done[id]=result;return result;
 };
 vector<int> outs;for(int r:roots)outs.push_back(build(r));
 // Cached symbolic implicant covers. Their chosen terms depend only on
 // the truth table; gate construction, hashing and arrival times still depend
 // on this candidate's mapping strategy.
 int cubemode=opt.cubemode;
 if(cubemode && n<=13){
  const auto &covers=shared_covers(data);
  auto combine=[&](vector<int> vs,bool isOr)->int {
   if(vs.empty())return isOr?0:ONE;
   auto cmp=[&](int a,int b){return ready[a]>ready[b];};
   priority_queue<int,vector<int>,decltype(cmp)> pq(cmp);
   for(int a:vs)pq.push(a);
   while(pq.size()>1){int a=pq.top();pq.pop();int b=pq.top();pq.pop();pq.push(isOr?lor(a,b):land(a,b));}
   return pq.top();
  };
  auto calcSOP=[&](const R5CoverPlan &plan)->int{
   if(plan.kind<0)return -1;
   if(plan.kind==0)return 0;
   if(plan.kind==1)return ONE;
   const int k=(int)plan.support.size();
   vector<int> terms;
   for(auto p:plan.chosen){
     vector<int> literals;
     for(int b=0;b<k;b++)if(p.mask&(1<<b)){
       int x=plan.support[k-1-b]+1;
       literals.push_back((p.val&(1<<b))?x:neg(x));
     }
     terms.push_back(combine(literals,false));
   }
   return combine(terms,true);
  };
  for(int j=0;j<m;j++){
   int old=outs[j];
   int p=calcSOP(covers[j][1]);
   if(p<0)continue;
   int q=neg(calcSOP(covers[j][0]));
   int candidate=(ready[p]<=ready[q]?p:q);
   if(cubemode==2 || ready[candidate]<ready[old])outs[j]=candidate;
  }
 }

 // remove unused gates including unnecessary ONE if not needed; preserve ID indexing by regenerating used gates.
 vector<char> use(gates.size());function<void(int)> mark=[&](int id){if(id<=n)return;int j=id-n-1;if(use[j])return;use[j]=1;mark(gates[j].a);if(gates[j].type!="NOT")mark(gates[j].b);};
 for(int o:outs)mark(o);
 vector<int> new_ids(gates.size());int k=n+1;
 for(size_t i=0;i<gates.size();i++)if(use[i])new_ids[i]=k++;
 for(size_t i=0;i<gates.size();i++)if(use[i]){auto g=gates[i];auto fix=[&](int x){return x<=n?x:new_ids[x-n-1];}; out<<new_ids[i]<<" "<<g.type<<" "<<fix(g.a);if(g.type!="NOT")out<<" "<<fix(g.b);out<<"\n";}
 for(int j=0;j<m;j++){if(j)out<<" ";out<<(outs[j]<=n?outs[j]:new_ids[outs[j]-n-1]);}out<<"\n";
 if(auto p=std::getenv("UFUG_ROUND5_PROFILE"))if(*p=='1') {
   std::cerr<<"R5_STAGE stage=mapping order="<<opt.order
     <<" elapsed_ms="<<std::fixed<<std::setprecision(3)
     <<std::chrono::duration<double,std::milli>(Time::now()-bdd_finished).count()<<"\n";
 }
 return out.str();
}

struct Stats {bool valid=false;long long area=0;int delay=0;};
// Linear-time, allocation-lean parser for synthesizer-created Netlists.
// It checks the same topological-ID and gate-arity conditions as the original
// stringstream parser, but avoids an istringstream, vector<string> and stoi
// for every gate during candidate selection.
Stats stats(const string&net,int n,int m,int aa,int da,int ao,int dor,int an,int dn){
 const char *p=net.data(),*e=p+net.size();
 vector<int> arrivals(n+1,0);
 long long area=0;int count=0;
 auto blank=[&](){while(p<e && (*p==' '||*p=='\t'||*p=='\r'))++p;};
 auto getint=[&]()->int{
   if(p==e||*p<'0'||*p>'9')return -1;
   int v=0;
   while(p<e && *p>='0' && *p<='9'){
     int digit=*p++-'0';
     if(v>(INT_MAX-digit)/10)return -1;
     v=v*10+digit;
   }
   return v;
 };
 while(p<e){
   while(p<e && (*p=='\n'||*p=='\r'||*p==' '||*p=='\t'))++p;
   if(p==e)break;
   int id=getint();if(id<0)return {};
   blank();
   int op=-1;
   if(p+4<=e && p[0]=='A' && p[1]=='N' && p[2]=='D' && p[3]=='2'){
     op=0;p+=4;
   }else if(p+3<=e && p[0]=='O' && p[1]=='R' && p[2]=='2'){
     op=1;p+=3;
   }else if(p+3<=e && p[0]=='N' && p[1]=='O' && p[2]=='T'){
     op=2;p+=3;
   }
   if(op>=0){
     if(p>=e || (*p!=' '&&*p!='\t'))return {};
     blank();int a=getint();
     if(id!=n+1+count || a<0 || a>=id)return {};
     int b=0;
     if(op!=2){
       if(p>=e || (*p!=' '&&*p!='\t'))return {};
       blank();b=getint();if(b<0||b>=id)return {};
     }
     blank();if(p<e && *p!='\n')return {};
     if(p<e)++p;
     int t=op==2?arrivals[a]+dn:max(arrivals[a],arrivals[b])+(op==0?da:dor);
     arrivals.push_back(t);
     area+=(op==0?aa:op==1?ao:an);
     count++;
   }else{
     if(id>=int(arrivals.size()))return {};
     int d=arrivals[id];
     for(int j=1;j<m;j++){
       int v=getint();if(v<0 || v>=int(arrivals.size()))return {};
       d=max(d,arrivals[v]);
       blank();
     }
     blank();if(p<e && *p!='\n')return {};
     return {true,area,d};
   }
 }
 return {};
}

// Experimental single-fanout AND/OR-cone rebalancing, followed by live-gate pruning.
string rebalance(const string &net,int n,int m,int aa,int da,int ao,int dor,int an,int dn){
 (void)aa;(void)ao;(void)an;
 struct N {int op,a,b;};
 istringstream in(net);string line;
 vector<N> old(n+1,{-1,0,0});vector<int> outputs;
 while(getline(in,line)){
  if(line.empty())continue;
  istringstream ss(line);string first,typ;ss>>first;
  if(!(ss>>typ)){outputs.push_back(stoi(first));break;}
  if(typ=="AND2" || typ=="OR2" || typ=="NOT"){
   int id=stoi(first),a,b=0;if(id!=int(old.size()) || !(ss>>a))return {};
   if(typ!="NOT" && !(ss>>b))return {};
   old.push_back({typ=="AND2"?0:typ=="OR2"?1:2,a,b});
  }else{
   outputs.push_back(stoi(first));outputs.push_back(stoi(typ));
   int t;while(ss>>t)outputs.push_back(t);
   break;
  }
 }
 // For m=1, the last output line contains a single token.
 if(outputs.empty()){
  // This branch is only used for single-signal netlists; parse the actual final line.
  auto p=net.rfind('\n');(void)p;
 }
 if(int(outputs.size())!=m)return {};
 vector<int> uses(old.size());
 for(int id=n+1;id<int(old.size());id++){
  ++uses[old[id].a];
  if(old[id].op!=2)++uses[old[id].b];
 }
 for(int o:outputs)if(o>=0 && o<int(uses.size()))++uses[o];else return {};
 vector<N> fresh(n+1,{-1,0,0});vector<int> ready(n+1,0),mapped(n+1);
 iota(mapped.begin(),mapped.end(),0);mapped.resize(old.size(),-1);
 unordered_map<GKey,int,HKey> intern;
 auto gate=[&](int op,int a,int b)->int {
  if(op!=2&&a>b)swap(a,b);
  GKey key{op,a,b};auto it=intern.find(key);
  if(it!=intern.end())return it->second;
  int id=fresh.size();fresh.push_back({op,a,b});
  ready.push_back((op==2?ready[a]:max(ready[a],ready[b]))+(op==0?da:op==1?dor:dn));
  intern.emplace(key,id);return id;
 };
 for(int id=n+1;id<int(old.size());id++){
   const auto &g=old[id];
   if(g.op==2){mapped[id]=gate(2,mapped[g.a],0);continue;}
   vector<int> leaves;
   vector<int> st{id};
   while(!st.empty()){
     int v=st.back();st.pop_back();
     if(v>n && old[v].op==g.op && (v==id||uses[v]==1) && leaves.size()+st.size()<64){
       st.push_back(old[v].a);st.push_back(old[v].b);
     }else leaves.push_back(mapped[v]);
   }
   sort(leaves.begin(),leaves.end());leaves.erase(unique(leaves.begin(),leaves.end()),leaves.end());
   if(leaves.size()==1){mapped[id]=leaves[0];continue;}
   using Item=pair<int,int>;
   priority_queue<Item,vector<Item>,greater<Item>> pq;
   for(int v:leaves)pq.emplace(ready[v],v);
   while(pq.size()>1){int a=pq.top().second;pq.pop();int b=pq.top().second;pq.pop();int z=gate(g.op,a,b);pq.emplace(ready[z],z);}
   mapped[id]=pq.top().second;
 }
 for(int &o:outputs)o=mapped[o];
 vector<uint8_t> live(fresh.size());vector<int> st=outputs;
 while(!st.empty()){
   int v=st.back();st.pop_back();if(v<=n || live[v])continue;
   live[v]=1;st.push_back(fresh[v].a);
   if(fresh[v].op!=2)st.push_back(fresh[v].b);
 }
 vector<int> ids(fresh.size());iota(ids.begin(),ids.begin()+n+1,0);
 int nid=n+1;
 for(int id=n+1;id<int(fresh.size());id++)if(live[id])ids[id]=nid++;
 ostringstream out;
 for(int id=n+1;id<int(fresh.size());id++)if(live[id]){
  auto g=fresh[id];out<<ids[id]<<' '<<(g.op==0?"AND2":g.op==1?"OR2":"NOT")<<' '<<ids[g.a];
  if(g.op!=2)out<<' '<<ids[g.b];
  out<<'\n';
 }
 for(int j=0;j<m;j++){if(j)out<<' ';out<<ids[outputs[j]];}out<<'\n';
 return out.str();
}


// Timing-slack-aware area recovery by local De Morgan mapping.
// The original Netlist is authoritative for required-time computation.
string area_recover(const string &net,int n,int m,int aa,int da,int ao,int dor,int an,int dn,int target,int margin){
 struct N {int op,a,b;};
 istringstream in(net);string line;
 vector<N> old(n+1,{-1,0,0});vector<int> outputs;
 while(getline(in,line)){
  if(line.empty())continue;
  istringstream ss(line);string first,typ;ss>>first;
  if(!(ss>>typ)){outputs.push_back(stoi(first));break;}
  if(typ=="AND2" || typ=="OR2" || typ=="NOT"){
   int id=stoi(first),a,b=0;if(id!=int(old.size()) || !(ss>>a))return {};
   if(typ!="NOT" && !(ss>>b))return {};
   old.push_back({typ=="AND2"?0:typ=="OR2"?1:2,a,b});
  }else{
   outputs.push_back(stoi(first));outputs.push_back(stoi(typ));
   int t;while(ss>>t)outputs.push_back(t);
   break;
  }
 }
 if(int(outputs.size())!=m)return {};
 const int INF=1000000000;
 vector<int> need(old.size(),INF);
 for(int out:outputs)need[out]=min(need[out],target-margin);
 for(int id=int(old.size())-1;id>n;id--){
   if(need[id]>=INF)continue;
   auto g=old[id];int t=(g.op==0?da:g.op==1?dor:dn);
   need[g.a]=min(need[g.a],need[id]-t);
   if(g.op!=2)need[g.b]=min(need[g.b],need[id]-t);
 }
 vector<N> fresh(n+1,{-1,0,0});vector<int> ready(n+1,0),mapped(old.size(),-1);
 iota(mapped.begin(),mapped.begin()+n+1,0);
 unordered_map<GKey,int,HKey> intern;intern.reserve(old.size()*2);
 auto gate=[&](int op,int a,int b)->int {
  if(op!=2&&a>b)swap(a,b);
  GKey key{op,a,b};auto it=intern.find(key);if(it!=intern.end())return it->second;
  int id=fresh.size();fresh.push_back({op,a,b});
  ready.push_back((op==2?ready[a]:max(ready[a],ready[b]))+(op==0?da:op==1?dor:dn));
  intern.emplace(key,id);return id;
 };
 auto neg=[&](int a)->int {
   if(a>n && fresh[a].op==2)return fresh[a].a;
   return gate(2,a,0);
 };
 for(int id=n+1;id<int(old.size());id++){
   auto g=old[id];int a=mapped[g.a],b=g.op==2?0:mapped[g.b];
   if(g.op==2){mapped[id]=neg(a);continue;}
   int org=gate(g.op,a,b);
   int root=org;
   if((g.op==0 && aa>ao+3*an) || (g.op==1 && ao>aa+3*an)){
      int a2=neg(a),b2=neg(b),alt=neg(gate(1-g.op,a2,b2));
      if(ready[alt]<=need[id])root=alt;
   }
   mapped[id]=root;
 }
 for(int &out:outputs)out=mapped[out];
 vector<unsigned char> live(fresh.size());vector<int> st=outputs;
 while(!st.empty()){
  int v=st.back();st.pop_back();if(v<=n||live[v])continue;
  live[v]=1;st.push_back(fresh[v].a);
  if(fresh[v].op!=2)st.push_back(fresh[v].b);
 }
 vector<int> ids(fresh.size());iota(ids.begin(),ids.begin()+n+1,0);
 int next=n+1;
 for(int id=n+1;id<int(fresh.size());id++)if(live[id])ids[id]=next++;
 ostringstream out;
 for(int id=n+1;id<int(fresh.size());id++)if(live[id]){
  auto g=fresh[id];out<<ids[id]<<' '<<(g.op==0?"AND2":g.op==1?"OR2":"NOT")<<' '<<ids[g.a];
  if(g.op!=2)out<<' '<<ids[g.b];
  out<<'\n';
 }
 for(int j=0;j<m;j++){if(j)out<<' ';out<<ids[outputs[j]];}out<<'\n';
 return out.str();
}

namespace legacy {
using namespace std;
struct BKey {int v,lo,hi;bool operator==(const BKey&o)const{return v==o.v && lo==o.lo && hi==o.hi;}};
struct H3 {size_t operator()(const BKey&k)const { uint64_t z=((uint64_t)(unsigned)k.v<<55)^((uint64_t)(unsigned)k.lo<<26)^(unsigned)k.hi; z^=z>>30;z*=0xbf58476d1ce4e5b9ULL;z^=z>>27;z*=0x94d049bb133111ebULL;return z^(z>>31);}};
struct BNode{int v,lo,hi;};
struct Gate{string type;int a,b;};
struct GKey{int t,a,b;bool operator==(const GKey&o)const{return t==o.t&&a==o.a&&b==o.b;}};
struct HKey{size_t operator()(const GKey &k)const{return H3{}({k.t,k.a,k.b});}};
struct Opt {string order;bool fast, rewrite, expand;int cubemode,margin;};
string run_synth(const string &input,const Opt &opt,
  chrono::steady_clock::time_point deadline=chrono::steady_clock::time_point::max()){
 uint64_t r72_checks=0;
 auto r72_checkpoint=[&](){
  if(deadline!=chrono::steady_clock::time_point::max() &&
     ((++r72_checks & 127ULL)==0) && chrono::steady_clock::now()>=deadline)
      throw CandidateTimeout{};
 };
 ifstream in(input);ostringstream out;if(!in)return {};
 int n,m;in>>n>>m; if(n<1 || n>22 || m<1)return {};
 size_t N=1ull<<n; vector<unsigned char> T(N*m);string bits;
 for(size_t i=0;i<N;i++){r72_checkpoint();in>>bits; if((int)bits.size()!=m)return {};for(int j=0;j<m;j++)T[i*m+j]=bits[j]-'0';}
 int aa,da,ao,doo,an,dn,D;in>>aa>>da>>ao>>doo>>an>>dn>>D;
 // BDD global canonical graph, terminal 0 and 1.
 vector<BNode> nodes;nodes.reserve(N);nodes.push_back({-1,0,0}); nodes.push_back({-1,1,1});
 unordered_map<BKey,int,H3> cache;cache.reserve(min((size_t)N*2,(size_t)5000000));
 vector<int> perm(n); iota(perm.begin(),perm.end(),0);
 string order=opt.order;
 if(order=="reverse")reverse(perm.begin(),perm.end());
 if(order=="rotate")rotate(perm.begin(),perm.begin()+n/2,perm.end());
 if(order=="influence-asc"||order=="influence-desc"){
  vector<unsigned long long> influence(n,0);
  for(int v=0;v<n;v++){
    size_t step=1ull<<(n-1-v);
    for(size_t start=0;start<N;start+=2*step){
      for(size_t k=0;k<step;k++){
        size_t a=(start+k)*m,b=(start+k+step)*m;
        for(int j=0;j<m;j++)influence[v]+=(T[a+j]!=T[b+j]);
      }
    }
  }
  stable_sort(perm.begin(),perm.end(),[&](int a,int b){return order=="influence-asc"?influence[a]<influence[b]:influence[a]>influence[b];});
 }
 vector<size_t> orig(N);for(size_t z=1;z<N;z++){r72_checkpoint();int bit=__builtin_ctzll(z);orig[z]=orig[z&(z-1)]|(1ull<<(n-1-perm[n-1-bit]));}
 vector<int> roots(m);vector<int> cur(N),next;
 for(int j=0;j<m;j++){
  cur.resize(N);
  for(size_t i=0;i<N;i++)cur[i]=T[orig[i]*m+j];
  size_t count=N;
  for(int v=n-1;v>=0;v--){
   next.resize(count/2);
   for(size_t k=0;k<count/2;k++){
    r72_checkpoint();
    int lo=cur[2*k],hi=cur[2*k+1];
    if(lo==hi){next[k]=lo;continue;}
    BKey key={v,lo,hi};auto it=cache.find(key);
    if(it!=cache.end()){next[k]=it->second;continue;}
    int id=nodes.size();nodes.push_back({v,lo,hi});cache.emplace(key,id);next[k]=id;
   }
   cur.swap(next);count/=2;
  }
  roots[j]=cur[0];
 }
 // Emit gates with structural sharing, constant folding, and NOT sharing.
 vector<Gate> gates;
 unordered_map<GKey,int,HKey> gcache;gcache.reserve(nodes.size()*2);
 vector<int> ready(n+1);int A=0;
 auto mk=[&](int t,int a,int b)->int {r72_checkpoint();if(t!=2&&a>b)swap(a,b); GKey k{t,a,b}; auto it=gcache.find(k);if(it!=gcache.end())return it->second;
  int id=n+1+(int)gates.size();gates.push_back({t==0?"AND2":t==1?"OR2":"NOT",a,b}); gcache.emplace(k,id);A+=(t==0?aa:t==1?ao:an);ready.push_back((t==2?ready[a]:max(ready[a],ready[b]))+(t==0?da:t==1?doo:dn));return id;};
 int ONE=mk(2,0,0); // canonical 1
 function<int(int)> neg=[&](int a)->int{
  if(a==0)return ONE;
  if(a==ONE)return 0;
  auto it=gcache.find({2,a,0});if(it!=gcache.end())return it->second;
  if(a>n){Gate &g=gates[a-(n+1)];if(g.type=="NOT")return g.a;}
  return mk(2,a,0);
 };
 auto areInverse=[&](int a,int b)->bool {
   if((a==0&&b==ONE)||(a==ONE&&b==0))return true;
   if(a>n && gates[a-(n+1)].type=="NOT" && gates[a-(n+1)].a==b)return true;
   if(b>n && gates[b-(n+1)].type=="NOT" && gates[b-(n+1)].a==a)return true;
   return false;
 };
 function<int(int,int)> land=[&](int a,int b)->int{if(a==0||b==0)return 0;if(a==ONE)return b;if(b==ONE)return a;if(a==b)return a;if(areInverse(a,b))return 0;if((opt.rewrite && aa>ao+3*an) || opt.fast){
  int na=neg(a),nb=neg(b);int limit=0;
  limit=0;
  if((opt.fast?max(ready[na],ready[nb])+doo+dn<max(ready[a],ready[b])+da:max(ready[na],ready[nb])+doo+dn<=max(ready[a],ready[b])+da+limit))return neg(mk(1,na,nb));
  }return mk(0,a,b);};
 function<int(int,int)> lor=[&](int a,int b)->int{if(a==ONE||b==ONE)return ONE;if(a==0)return b;if(b==0)return a;if(a==b)return a;if(areInverse(a,b))return ONE;if((opt.rewrite && ao>aa+3*an) || opt.fast){
  int na=neg(a),nb=neg(b);int limit=0;
  limit=0;
  if((opt.fast?max(ready[na],ready[nb])+da+dn<max(ready[a],ready[b])+doo:max(ready[na],ready[nb])+da+dn<=max(ready[a],ready[b])+doo+limit))return neg(mk(0,na,nb));
  }return mk(1,a,b);};
 vector<int> done(nodes.size(),-1);done[0]=0;done[1]=ONE;
 function<int(int)> build=[&](int id)->int {r72_checkpoint();if(done[id]>=0)return done[id];auto node=nodes[id];int x=perm[node.v]+1;
  int lo=build(node.lo),hi=build(node.hi),result;
  if(lo==hi)result=lo;
  else if(lo==0)result=land(x,hi);
  else if(hi==0)result=land(neg(x),lo);
  else if(lo==ONE)result=lor(neg(x),hi);
  else if(hi==ONE)result=lor(x,lo);
  else result=lor(land(neg(x),lo),land(x,hi));
  // Experimental two-level Shannon expansion, compare by local arrival time.
  if(opt.expand && nodes[id].lo > 1 && nodes[id].hi > 1) {
    auto combine_balanced=[&](vector<int> v,bool isor)->int {
      if(v.empty())return isor?0:ONE;
      auto cmp=[&](int a,int b){return ready[a]>ready[b];};
      priority_queue<int,vector<int>,decltype(cmp)> pq(cmp);
      for(int a:v)pq.push(a);
      while(pq.size()>1){int a=pq.top();pq.pop();int b=pq.top();pq.pop();pq.push(isor?lor(a,b):land(a,b));}
      return pq.top();
    };
    vector<int> terms;
    for(int side=0;side<2;side++){
      int child=side?nodes[id].hi:nodes[id].lo;
      int rootlit=side?x:neg(x);
      if(child <= 1) { if(child==1)terms.push_back(rootlit);continue; }
      auto g=nodes[child];int y=perm[g.v]+1;
      for(int side2=0;side2<2;side2++){
        int leaf=build(side2?g.hi:g.lo);
        if(leaf==0)continue;
        vector<int> vs={rootlit,side2?y:neg(y)};
        if(leaf!=ONE)vs.push_back(leaf);
        terms.push_back(combine_balanced(vs,false));
      }
    }
    int expanded=combine_balanced(terms,true);
    int slack=opt.margin;
    if(ready[expanded]+slack < ready[result])result=expanded;
  }
  done[id]=result;return result;
 };
 vector<int> outs;for(int r:roots)outs.push_back(build(r));
 // Exact implicant enumeration for small truth tables, followed by greedy cover.
 int cubemode=opt.cubemode;
 if(cubemode && n<=13){
  struct Cube {int val,mask;};
  auto calcSOP=[&](int j,int goal)->int {
    vector<int> support;
    for(int v=0;v<n;v++){
      int step=1<<(n-1-v);bool flag=false;
      for(int start=0;start<(int)N && !flag;start+=step*2)
        for(int z=0;z<step;z++)if(T[((size_t)start+z)*m+j]!=T[((size_t)start+step+z)*m+j]){flag=true;break;}
      if(flag)support.push_back(v);
    }
    int k=(int)support.size();if(k>9)return -1;
    int Q=1<<k;vector<uint8_t> tt(Q);
    for(int i=0;i<Q;i++){
      size_t orig=0;
      for(int b=0;b<k;b++)if(i&(1<<b))orig|=1ull<<(n-1-support[k-1-b]);
      tt[i]=T[orig*m+j];
    }
    vector<Cube> cur; cur.reserve(Q);
    for(int i=0;i<Q;i++)if(tt[i]==goal)cur.push_back({i,Q-1});
    if(cur.empty())return 0;
    if((int)cur.size()==Q)return ONE;
    vector<Cube> prime;
    while(!cur.empty()){
      vector<char> used(cur.size());vector<Cube> nxt;
      unordered_set<unsigned long long> hash;
      for(size_t a=0;a<cur.size();a++)for(size_t b=a+1;b<cur.size();b++){
        if(cur[a].mask!=cur[b].mask)continue;
        int diff=(cur[a].val^cur[b].val)&cur[a].mask;
        if(__builtin_popcount((unsigned)diff)!=1)continue;
        used[a]=used[b]=1;
        int mk=cur[a].mask^diff,v=cur[a].val&mk;
        auto id=((unsigned long long)(unsigned)mk<<32)|(unsigned)v;
        if(hash.insert(id).second)nxt.push_back({v,mk});
      }
      for(size_t a=0;a<cur.size();a++)if(!used[a])prime.push_back(cur[a]);
      cur.swap(nxt);
    }
    // Deduplicate and greedily cover all on-set minterms.
    sort(prime.begin(),prime.end(),[](Cube a,Cube b){return tie(a.mask,a.val)<tie(b.mask,b.val);});
    prime.erase(unique(prime.begin(),prime.end(),[](Cube a,Cube b){return a.mask==b.mask&&a.val==b.val;}),prime.end());
    vector<char> uncovered(Q,0);int remaining=0;
    for(int i=0;i<Q;i++)if(tt[i]==goal){uncovered[i]=1;remaining++;}
    vector<Cube> chosen;
    while(remaining){
      double best=-1;int which=-1;
      for(int k=0;k<(int)prime.size();k++){
        int gains=0;
        for(int i=0;i<Q;i++)if(uncovered[i] && (i&prime[k].mask)==prime[k].val)gains++;
        if(!gains)continue;
        int cost=max(1,__builtin_popcount((unsigned)prime[k].mask));
        double score=double(gains)/(0.4+cost);
        if(score>best){best=score;which=k;}
      }
      if(which<0)throw runtime_error("cover failed");
      auto p=prime[which];chosen.push_back(p);
      for(int i=0;i<Q;i++)if(uncovered[i] && (i&p.mask)==p.val){uncovered[i]=0;remaining--;}
    }
    auto combine=[&](vector<int> vs,bool isOr)->int {
       if(vs.empty())return isOr?0:ONE;
       auto cmp=[&](int a,int b){return ready[a]>ready[b];};
       priority_queue<int,vector<int>,decltype(cmp)> pq(cmp);
       for(int a:vs)pq.push(a);
       while(pq.size()>1){int a=pq.top();pq.pop();int b=pq.top();pq.pop();pq.push(isOr?lor(a,b):land(a,b));}
       return pq.top();
    };
    vector<int> terms;
    for(auto p:chosen){
      vector<int> literals;
      for(int b=0;b<k;b++)if(p.mask&(1<<b)){
         int x=support[k-1-b]+1;literals.push_back((p.val&(1<<b))?x:neg(x));
      }
      terms.push_back(combine(literals,false));
    }
    return combine(terms,true);
  };
  for(int j=0;j<m;j++){
   
   int old=outs[j];
   int p=calcSOP(j,1);
   if(p<0)continue;
   int q=neg(calcSOP(j,0));
   int candidate=(ready[p]<=ready[q]?p:q);
   if(cubemode==2 || ready[candidate]<ready[old])outs[j]=candidate;
  }
 }

 // remove unused gates including unnecessary ONE if not needed; preserve ID indexing by regenerating used gates.
 vector<char> use(gates.size());function<void(int)> mark=[&](int id){if(id<=n)return;int j=id-n-1;if(use[j])return;use[j]=1;mark(gates[j].a);if(gates[j].type!="NOT")mark(gates[j].b);};
 for(int o:outs)mark(o);
 vector<int> new_ids(gates.size());int k=n+1;
 for(size_t i=0;i<gates.size();i++)if(use[i])new_ids[i]=k++;
 for(size_t i=0;i<gates.size();i++)if(use[i]){auto g=gates[i];auto fix=[&](int x){return x<=n?x:new_ids[x-n-1];}; out<<new_ids[i]<<" "<<g.type<<" "<<fix(g.a);if(g.type!="NOT")out<<" "<<fix(g.b);out<<"\n";}
 for(int j=0;j<m;j++){if(j)out<<" ";out<<(outs[j]<=n?outs[j]:new_ids[outs[j]-n-1]);}out<<"\n";
 return out.str();
}


}

int main(int argc,char**argv){
 using Clock=chrono::steady_clock;
 const auto r71_launch=Clock::now();
 if(argc!=3)return 2;
 ifstream in(argv[1]);int n,m;string line;
 if(!(in>>n>>m))return 3;
 for(int k=0;k<(1<<n);k++)if(!(in>>line))return 4;
 int aa,da,ao,dor,an,dn,target;
 if(!(in>>aa>>da>>ao>>dor>>an>>dn>>target))return 5;
 long long limit=0,ram_kb=0;
 if(in>>limit){if(!(in>>ram_kb))in.clear();}else in.clear();
 if(limit<0||ram_kb<0){std::cerr<<"R821_ERROR negative_resource_limit\n";return 13;}
 const r51::Costs r821_costs{aa,da,ao,dor,an,dn};
 const bool r821_try_compact=(ram_kb>0 && !r821::bdd_admitted(n,m,ram_kb));
 if(r821_try_compact){
   const auto p=r821::compact_probe(argv[1],n,m,r821_costs,target,ram_kb);
   if(p.solved){
     std::ofstream out(argv[2]);out<<p.netlist;
     std::cerr<<"R821_RESOURCE result=solved path="<<p.reason
       <<" n="<<n<<" m="<<m<<" ram_kb="<<ram_kb
       <<" support="<<p.support<<" area="<<p.area<<" delay="<<p.delay<<"\n";
     return out?0:7;
   }
   if(ram_kb>0 && !r821::bdd_admitted(n,m,ram_kb)){
     std::cerr<<"R821_RESOURCE result=declined_bdd ram_kb="<<ram_kb
       <<" estimate_bytes="<<r821::bdd_reservation_estimate_bytes(n,m)
       <<" fallback="<<p.reason<<" support="<<p.support<<"\n";
     return 14; // Explicit failure is safer than silently exceeding RAM cap.
   }
 }
 const char* r85env_early=std::getenv("UFUG_R85_POLICY");
 const std::string r85policy=r85env_early?r85env_early:"dual_sop_first";
 const bool r85enabled=r85policy!="off";
 const char* r84env_early=std::getenv("UFUG_R84_POLICY");
 const bool r84enabled=(!r85enabled && (r84env_early==nullptr || std::string(r84env_early)!="off"));
 const char* r83env_early=std::getenv("UFUG_R83_POLICY");
 const bool r83enabled=(!r85enabled && !r84enabled && (r83env_early==nullptr || std::string(r83env_early)!="off"));
 auto start=r71_launch;
 // Optional ablation: UFUG_R71_POLICY=off restores the R7 portfolio.
 const char* r71_env=std::getenv("UFUG_R71_POLICY");
 const std::string r71_policy=r71_env?r71_env:"guard";
 const bool r71_guard=(r71_policy!="off");
 const bool r71_trace=[]{const char*p=std::getenv("UFUG_R71_TRACE");return p&&*p=='1';}();
 // A heuristic dispatch reserve, not a hard real-time guarantee.
 const double r71_search_cap=limit>0?
   (limit<=250?0.72*double(limit):0.75*double(limit)):
   std::numeric_limits<double>::infinity();
 auto r71_elapsed=[&](){return std::chrono::duration<double,std::milli>(Clock::now()-start).count();};
 if(r71_trace)std::cerr<<"R71_TRACE event=policy policy="<<r71_policy
    <<" limit_ms="<<limit<<" dispatch_cap_ms="<<r71_search_cap<<"\n";
 // Always try a correct delay-oriented candidate first.
 vector<Opt> variants={
   {"influence-desc",true,false,true,1,0},
   {"influence-desc",false,true,true,1,0},
   {"influence-desc",true,false,true,0,0},
   {"natural",true,false,true,1,0},
   {"influence-desc",true,false,true,1,4}
 };
 // Spend extra search only on sufficiently large budgets and manageable dimensions.
 if(n<=18 && limit>=5000) variants.push_back({"reverse",true,false,true,1,0});
 // Round 4 order diversity: explore non-redundant generic variable permutations.
 if(n<=18 && limit>=5000){
   variants.push_back({"rotate",true,false,true,1,0});
   variants.push_back({"influence-asc",true,false,true,1,0});
 }

 string best;Stats b;int chosen=-1,completed=0;
 for(int i=0;i<int(variants.size());i++){
   // Exact semantic and implementation deduplication:
   // i=0 and i=2 differ only in cubemode; implicant enumeration is gated
   // by n<=13. With n>13 they generate the same netlist by construction.
   if(i==2 && n>13)continue;
  // Heuristic search budget leaves space for writing and evaluation overhead.
  if(i && limit>0){
   auto elapsed=r71_elapsed();
   const double dispatch=r71_guard?r71_search_cap:0.75*limit;
   if(elapsed>=dispatch){
     if(r71_trace)std::cerr<<"R71_TRACE event=primary_skip index="<<i
       <<" elapsed_ms="<<elapsed<<" cause=dispatch_budget\n";
     break;
   }
  }
  variants[i].affine=true;
  auto trial_started=Clock::now();
  string net;
  try {
     if(i>=6){
       const double available=limit>0 ? max(100.0,0.13*double(limit)) : 800.0;
       const double allowance=min(1500.0,available);
       auto deadline=Clock::now()+chrono::microseconds(static_cast<long long>(allowance*1000.0));
       net=run_synth(argv[1],variants[i],deadline);
     }else{
       if(r71_guard && i>0 && limit>0 && limit<=250){
         auto deadline=start+std::chrono::microseconds(
           static_cast<long long>(r71_search_cap*1000.0));
         net=run_synth(argv[1],variants[i],deadline);
       }else{
         net=run_synth(argv[1],variants[i]);
       }
     }
  } catch(const CandidateTimeout&){continue;}
  if(net.empty())continue;
  // Round 5.1: one parse from text to a typed, in-memory DAG.
  // Rebalancing and slack recovery operate on this DAG without an
  // intermediate serialize -> parse cycle.
  r51::Costs cost{aa,da,ao,dor,an,dn};
  r51::Graph typed=r51::parse(net,n,m);
  auto tz=typed.metric(cost);if(!tz.valid)continue;
  Stats z{tz.valid,tz.area,tz.delay};
  r51::Graph bal=r51::rebalance(typed,cost);
  auto tbz=bal.metric(cost);Stats bz{tbz.valid,tbz.area,tbz.delay};
  auto ranklocal=[&](Stats x){return make_tuple(max(0,x.delay-target),x.delay<=target?x.area:0LL,x.delay,x.area);};
  if(bz.valid && ranklocal(bz)<ranklocal(z)){typed=std::move(bal);z=bz;}
  if(z.delay<=target){
    r51::Graph ar=r51::area_recover(typed,cost,target,0);
    auto taz=ar.metric(cost);Stats az{taz.valid,taz.area,taz.delay};
    if(az.valid && ranklocal(az)<ranklocal(z)){typed=std::move(ar);z=az;}
  }
  // Serialization is delayed until this candidate beats the incumbent.
  net.clear();
  completed++;
  if(auto p=std::getenv("UFUG_ROUND5_PROFILE"))if(*p=='1')
    std::cerr<<"R5_STAGE stage=trial_total index="<<i<<" order="<<variants[i].order
      <<" elapsed_ms="<<std::fixed<<std::setprecision(3)
      <<std::chrono::duration<double,std::milli>(Clock::now()-trial_started).count()<<"\n";
  auto rank=[&](Stats x){return make_tuple(max(0,x.delay-target), x.delay<=target?x.area:0LL, x.delay, x.area);};
  const bool improved=(!b.valid || rank(z)<rank(b));
  if(improved){best=typed.serialize();b=z;chosen=i;}
  if(r71_trace)std::cerr<<"R71_TRACE event=primary index="<<i
    <<" elapsed_ms="<<r71_elapsed()
    <<" candidate_ms="<<std::chrono::duration<double,std::milli>(Clock::now()-trial_started).count()
    <<" candidate_area="<<z.area<<" candidate_delay="<<z.delay
    <<" improved="<<(improved?1:0)<<" incumbent_area="<<b.area<<"\n";
 }
 // After a feasible first pass, do not put an already valid circuit at risk
 // by launching more unbounded BDD candidates under a tight memory cap.
 // The budget bound is conservative and is NOT a proof of total RSS usage.
 if(ram_kb>0 && b.valid && b.delay<=target &&
    r821::saturation_mul(uint64_t(ram_kb),1024ULL) <
      r821::saturation_mul(r821::bdd_reservation_estimate_bytes(n,m),2ULL)){
   std::ofstream out(argv[2]);out<<best;
   std::cerr<<"R821_RESOURCE result=conservative_optional_skip"
     <<" ram_kb="<<ram_kb<<" area="<<b.area<<" delay="<<b.delay<<"\n";
   return out?0:7;
 }
 // Zero cost and zero delay are global lower bounds under positive gate costs.
 // Preserve the incumbent and skip ALL optional BDD/legacy/cut passes.
 if(b.valid && b.area==0 && b.delay==0){
   std::ofstream out(argv[2]);out<<best;
   std::cerr<<"R821_RESOURCE result=zero_area_early_exit\n";
   return out?0:7;
 }
 // A distinct legacy representation remains valuable: complementary normalization
 // should not erase earlier, smaller Area solutions. Only attempt this low-cost
 // fallback for moderate input dimensions and adequate declared runtime budgets.
 // R7.2 policy: guard reproduces R7.1; shortlist tries exactly one
 // cheap legacy candidate with cubemode=0 and a cooperative deadline.
 const char* r72_env=std::getenv("UFUG_R72_POLICY");
 const std::string r72_policy=r72_env?r72_env:"shortlist";
 if(r72_policy!="shortlist" && r72_policy!="guard" &&
    r72_policy!="shortlist_nocancel"){
   std::cerr<<"R72_ERROR invalid policy="<<r72_policy<<"\n";
   return 8;
 }
 const bool r72_short_feasible=(r71_guard && limit>0 && limit<=250 &&
    b.valid && b.delay<=target);
 const bool r72_use_shortlist=(r72_policy=="shortlist" ||
    r72_policy=="shortlist_nocancel") && r72_short_feasible &&
    n<=10 && limit>=100;
 const bool r72_trace=r71_trace;
 if(r72_use_shortlist){
   const double elapsed=r71_elapsed();
   // The dispatch admission test is intentionally stricter than the R7.1
   // 72% threshold. We need headroom for the original phase postprocessor
   // and for evaluator overhead after circuit construction.
   const double admission=0.35*double(limit);
   const double deadline_fraction=0.60;
   if(elapsed<admission){
     const auto candidate_started=Clock::now();
     const auto deadline=start+std::chrono::microseconds(
          static_cast<long long>(deadline_fraction*double(limit)*1000.0));
     try{
       legacy::Opt cheap={"influence-desc",true,false,true,0,0};
       const auto cap=(r72_policy=="shortlist_nocancel")?
          Clock::time_point::max():deadline;
       std::string trial=legacy::run_synth(argv[1],cheap,cap);
       const double search_ms=std::chrono::duration<double,std::milli>(
          Clock::now()-candidate_started).count();
       if(!trial.empty() && r71_elapsed()<0.65*double(limit)){
         r51::Costs cost{aa,da,ao,dor,an,dn};
         r51::Graph typed=r51::parse(trial,n,m);
         auto tz=typed.metric(cost);
         Stats z{tz.valid,tz.area,tz.delay};
         if(z.valid && z.delay<=target){
           r51::Graph ar=r51::area_recover(typed,cost,target,0);
           auto taz=ar.metric(cost);
           Stats az{taz.valid,taz.area,taz.delay};
           auto rank=[&](Stats x){return make_tuple(max(0,x.delay-target),
             x.delay<=target?x.area:0LL,x.delay,x.area);};
           if(az.valid && rank(az)<rank(z)){typed=std::move(ar);z=az;}
         }
         auto rank=[&](Stats x){return make_tuple(max(0,x.delay-target),
           x.delay<=target?x.area:0LL,x.delay,x.area);};
         const bool improved=z.valid && (!b.valid || rank(z)<rank(b));
         if(improved){best=typed.serialize();b=z;chosen=200+completed;}
         ++completed;
         if(r72_trace)std::cerr<<"R72_TRACE event=shortlist result=completed"
           <<" improved="<<improved<<" candidate_area="<<z.area
           <<" candidate_delay="<<z.delay
           <<" search_ms="<<search_ms
           <<" total_ms="<<r71_elapsed()
           <<" incumbent_area="<<b.area<<"\n";
       }else if(r72_trace){
         std::cerr<<"R72_TRACE event=shortlist result=insufficient_postprocess_budget"
           <<" search_ms="<<search_ms<<" elapsed_ms="<<r71_elapsed()<<"\n";
       }
     }catch(const CandidateTimeout&){
       if(r72_trace)std::cerr<<"R72_TRACE event=shortlist result=checkpoint_timeout"
          <<" elapsed_ms="<<r71_elapsed()<<"\n";
     }
   }else if(r72_trace){
     std::cerr<<"R72_TRACE event=shortlist result=admission_denied"
       <<" elapsed_ms="<<elapsed<<"\n";
   }
 }
 const bool r71_skip_legacy=r72_short_feasible;
 if(r71_trace && r71_skip_legacy)
   std::cerr<<"R71_TRACE event=legacy_skipped cause=short_budget_feasible_incumbent"
            <<" elapsed_ms="<<r71_elapsed()<<" area="<<b.area
            <<" delay="<<b.delay<<"\n";
 if(!r71_skip_legacy && ((n<=16 && limit>=5000) || (n<=10 && limit>=100))){
   vector<legacy::Opt> legacyMethods={
      {"influence-desc",false,true,true,1,0},
      {"influence-desc",true,false,true,0,0},
      {"natural",true,false,true,1,0}
   };
   for(const auto &opt:legacyMethods){
      if(limit>0){
        double elapsed=r71_elapsed();
        const double cap=r71_guard?std::min(r71_search_cap,0.72*double(limit)):0.72*limit;
        // Legacy runs have no cooperative interruption; stop earlier
        // in short budgets unless a feasible incumbent was already found.
        if(elapsed>=cap || (r71_guard && limit<=250 && elapsed>=0.35*limit)){
          if(r71_trace)std::cerr<<"R71_TRACE event=legacy_stop elapsed_ms="<<elapsed<<"\n";
          break;
        }
      }
      auto r71_legacy_started=Clock::now();
      string trial=legacy::run_synth(argv[1],opt);
      r51::Costs cost{aa,da,ao,dor,an,dn};
      r51::Graph typed=r51::parse(trial,n,m);
      auto tz=typed.metric(cost);Stats z{tz.valid,tz.area,tz.delay};
      if(!z.valid)continue;
      if(z.delay<=target){
         r51::Graph ar=r51::area_recover(typed,cost,target,0);
         auto taz=ar.metric(cost);Stats az{taz.valid,taz.area,taz.delay};
         if(az.valid && make_tuple(max(0,az.delay-target),az.area,az.delay)<
                         make_tuple(max(0,z.delay-target),z.area,z.delay)){
            z=az;typed=std::move(ar);
         }
      }
      auto rank=[&](Stats x){return make_tuple(max(0,x.delay-target),x.delay<=target?x.area:0LL,x.delay,x.area);};
      if(!b.valid || rank(z)<rank(b)){
         best=typed.serialize();b=z;chosen=100+completed;
      }
      ++completed;
      if(r71_trace)std::cerr<<"R71_TRACE event=legacy"
        <<" elapsed_ms="<<r71_elapsed()
        <<" candidate_ms="<<std::chrono::duration<double,std::milli>(Clock::now()-r71_legacy_started).count()
        <<" candidate_area="<<z.area<<" candidate_delay="<<z.delay
        <<" incumbent_area="<<b.area<<"\n";
   }
 }
 if(!b.valid)return 6;
 // Round 4: independent, semantics-preserving post-mapping alternatives.
 // Rank only completed, fully instantiated Netlists; keep the frozen Round 3 candidate.
 auto accept=[&](const std::string &candidate){
   if(candidate.empty())return false;
   auto z=stats(candidate,n,m,aa,da,ao,dor,an,dn);
   if(!z.valid)return false;
   auto rank=[&](Stats x){return make_tuple(max(0,x.delay-target),
          x.delay<=target?x.area:0LL,x.delay,x.area);};
   if(rank(z)<rank(b)){best=candidate;b=z;return true;}
   return false;
 };
 auto within_budget=[&](double pct){
   if(limit<=0)return true;
   const double cap=(r71_guard && limit<=250)?std::min(pct*double(limit),r71_search_cap):pct*double(limit);
   return r71_elapsed()<cap;
 };
 if(within_budget(0.79)){
   const std::string base=best;
   std::string algebra=round4_algebra::rewrite(base,n,m,2);
   if(!algebra.empty())accept(algebra);
   if(within_budget(0.82)){
      round4_phase::Engine phase(base,n,m,aa,da,ao,dor,an,dn,target);
      if(phase.valid){
        for(int variant=0;variant<2;++variant){
          if(!within_budget(0.88))break;
          fill(phase.phase.begin(),phase.phase.end(),0);
          if(variant==1||variant==4||variant==5)
            for(int v=n+1;v<int(phase.graph.size());++v)phase.phase[v]=1;
          if(variant==2||variant==3||variant==5)
            for(int v=n+1;v<int(phase.graph.size());++v)
              phase.phase[v]=phase.graph[v].op==0?(aa>ao):(ao>aa);
          if(variant>0)phase.improve(variant==3||variant==4?12:4,variant==3||variant==5);
          std::string mapped=phase.construct();
          accept(mapped);
          if(within_budget(0.88))accept(round4_algebra::rewrite(mapped,n,m,2));
        }
      }
   }
   if(false && !algebra.empty() && within_budget(0.88)){
     round4_phase::Engine phase(algebra,n,m,aa,da,ao,dor,an,dn,target);
     if(phase.valid){
       for(int variant: {1,2,3,4,5}){
         if(!within_budget(0.91))break;
         fill(phase.phase.begin(),phase.phase.end(),0);
         if(variant==1||variant==4||variant==5)
           for(int v=n+1;v<int(phase.graph.size());++v)phase.phase[v]=1;
         if(variant==2||variant==3||variant==5)
           for(int v=n+1;v<int(phase.graph.size());++v)
             phase.phase[v]=phase.graph[v].op==0?(aa>ao):(ao>aa);
         phase.improve(variant==3||variant==4?12:4,variant==3||variant==5);
         accept(phase.construct());
       }
     }
   }
 }
 // Round 8: independent structural alternatives, each rigorously checked on
 // the fully rebuilt live DAG. Baseline incumbent is preserved as fallback.
 const char* r8env=std::getenv("UFUG_R8_POLICY");
 std::string r8policy=(r83enabled||r84enabled||r85enabled)?"off":(r8env?r8env:((!std::getenv("UFUG_R82_POLICY") || std::string(std::getenv("UFUG_R82_POLICY"))!="off")?"off":"iterate"));
 if(r8policy!="iterate" && r8policy!="iterate_strict" && r8policy!="all" && r8policy!="off" && r8policy!="reuse" &&
    r8policy!="factor" && r8policy!="phase"){
   std::cerr<<"R8_ERROR policy="<<r8policy<<"\n";return 10;
 }
 if(r8policy!="off" && limit>=1000){
   double elapsed=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
   if(elapsed<0.67*double(limit) && b.valid && b.delay<=target){
     r51::Costs r8cost{aa,da,ao,dor,an,dn};
     r51::Graph baseline=r51::parse(best,n,m);
     auto base=baseline.metric(r8cost);
     if(base.valid){
       std::vector<std::string> modes;
       if(r8policy=="all" || r8policy=="iterate" || r8policy=="iterate_strict")modes={"absorb","factor","factor_relaxed","phase","reuse","combined","combined_relaxed"};
       else if(r8policy=="factor")modes={"factor","factor_relaxed"};
       else modes={r8policy};
       const double local_ms=std::min(250.0,0.10*double(limit));
       auto r8start=Clock::now();
       const int max_passes=(r8policy=="iterate" || r8policy=="iterate_strict")?5:1;
       for(int pass=0;pass<max_passes;++pass){
         bool epoch_improved=false;
         r51::Graph next=baseline;
         for(auto &mode:modes){
           double spent=std::chrono::duration<double,std::milli>(Clock::now()-r8start).count();
           elapsed=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
           if(spent>=local_ms || elapsed>=0.82*double(limit))break;
           auto exp=r8::rewrite(baseline,r8cost,mode,target);
           auto met=exp.graph.metric(r8cost);
           bool accepted=met.valid && met.delay<=target &&
             (r8policy!="iterate_strict" || met.delay<=base.delay) &&
             (met.area<b.area || (met.area==b.area && met.delay<b.delay));
           if(accepted){
             next=std::move(exp.graph);b.area=met.area;b.delay=met.delay;
             epoch_improved=true;
           }
           if(auto p=std::getenv("UFUG_R8_PROFILE"))if(*p=='1')
             std::cerr<<"R8_STAGE pass="<<(pass+1)<<" mode="<<mode
               <<" area="<<met.area<<" delay="<<met.delay
               <<" rewrite_ms="<<exp.milliseconds
               <<" factored="<<exp.counts.factoring
               <<" reused="<<exp.counts.expansion<<" accepted="<<accepted<<"\n";
         }
         if(!epoch_improved)break;
         baseline=std::move(next);
         best=baseline.serialize();
       }
     }
   }
 }
 // Round 8.1: independent truth-table cut-resynthesis branches.
 // Parent output remains the incumbent; only exact whole-graph cost gains
 // satisfying declared timing can replace it. No case-specific rules.
 const char* r81raw=std::getenv("UFUG_R81_POLICY");
 const std::string r81policy=(r83enabled||r84enabled||r85enabled)?"off":((!std::getenv("UFUG_R82_POLICY") || std::string(std::getenv("UFUG_R82_POLICY"))!="off")?"off":(r81raw?r81raw:"branch"));
 if(r81policy!="off" && r81policy!="sop" && r81policy!="shannon" &&
    r81policy!="all" && r81policy!="choices" && r81policy!="branch" &&
    r81policy!="branch_strict" && r81policy!="reverse"){
   std::cerr<<"R81_ERROR unknown policy "<<r81policy<<"\n";return 11;
 }
 if(r81policy!="off" && limit>=1000 && b.valid && b.delay<=target){
   const double consumed=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
   if(consumed<0.71*double(limit)){
     r51::Costs r81cost{aa,da,ao,dor,an,dn};
     const r51::Graph basegraph=r51::parse(best,n,m);
     const auto basemet=basegraph.metric(r81cost);
     if(basemet.valid){
       std::vector<std::string>branches;
       if(r81policy=="branch"||r81policy=="branch_strict"||r81policy=="reverse")
         branches={"sop","shannon","all"};
       else branches={r81policy};
       const bool strict=(r81policy=="branch_strict");
       const double total_ms=std::min(450.0,0.16*double(limit));
       const double each_ms=std::min(160.0,0.065*double(limit));
       const auto begin81=Clock::now();
       std::string chosenMode="base";
       for(const std::string& mode:branches){
         double spent=std::chrono::duration<double,std::milli>(Clock::now()-begin81).count();
         double elapsed=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
         if(spent>=total_ms||elapsed>=0.82*double(limit))break;
         auto attempt=r81::rewrite(basegraph,r81cost,target,mode,
                    std::min(each_ms,std::max(1.0,total_ms-spent)),2500);
         auto met=attempt.graph.metric(r81cost);
         // Reverse-order ablation: cut first, then pattern rewriting.
         if(r81policy=="reverse" && met.valid && met.delay<=target){
           for(int pass=0;pass<2;++pass){
             if(std::chrono::duration<double,std::milli>(Clock::now()-begin81).count()>=total_ms)break;
             bool improved=false;
             for(const char* rmode:{"reuse","factor","combined_relaxed"}){
               auto a=r8::rewrite(attempt.graph,r81cost,rmode,target);
               auto z=a.graph.metric(r81cost);
               if(z.valid && z.delay<=target && z.area<met.area){
                  attempt.graph=std::move(a.graph);met=z;improved=true;
               }
             }
             if(!improved)break;
           }
         }
         bool accept=met.valid && met.delay<=target &&
                     (!strict||met.delay<=basemet.delay) &&
                     (met.area<b.area || (met.area==b.area&&met.delay<b.delay));
         if(accept){
           best=attempt.graph.serialize();b.area=met.area;b.delay=met.delay;
           chosenMode=mode;
         }
         if(auto p=std::getenv("UFUG_R81_PROFILE"))if(*p=='1'){
           std::cerr<<"R81_STAGE mode="<<mode<<" area="<<met.area
             <<" delay="<<met.delay<<" attempt_ms="<<attempt.stats.elapsed_ms
             <<" visited="<<attempt.stats.visited_roots<<" cuts="<<attempt.stats.cuts
             <<" sop="<<attempt.stats.sop_candidates
             <<" shannon="<<attempt.stats.shannon_candidates
             <<" selected="<<attempt.stats.selected
             <<" zero_gain="<<attempt.stats.zero_gain_choices
             <<" timing_reject="<<attempt.stats.timing_reject
             <<" budget_hit="<<attempt.stats.budget_hit
             <<" accepted="<<accept<<"\n";
         }
       }
       if(auto p=std::getenv("UFUG_R81_PROFILE"))if(*p=='1')
         std::cerr<<"R81_FINAL policy="<<r81policy<<" selected="<<chosenMode
                  <<" area="<<b.area<<" delay="<<b.delay<<"\n";
     }
   }
 }
 // R8.2 independent full-graph candidate selection, no testcase-specific conditions.
 // R8.1 is disabled for this binary unless R82 policy is explicitly off.
 const char* r82raw=std::getenv("UFUG_R82_POLICY");
 const char* r83raw=std::getenv("UFUG_R83_POLICY");
 const std::string r83policy=(r84enabled||r85enabled)?"off":(r83raw?r83raw:"stable_dual_area");
 const std::string r82policy=(r83enabled||r84enabled||r85enabled)?"off":(r82raw?r82raw:"fast_adp");
 const bool r82active=r82policy!="off";
 if(r82policy!="off" && r82policy!="fast_area" && r82policy!="fast_slack" &&
    r82policy!="fast_adp" && r82policy!="dual_area" && r82policy!="dual_slack" &&
    r82policy!="dual_adp" && r82policy!="dual_strict"){
    std::cerr<<"R82_ERROR unknown policy="<<r82policy<<"\n";return 12;
 }
 if(r82active && limit>=1000 && b.valid && b.delay<=target){
    double sofar=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
    // Preserve time for graph serialization and evaluator overhead.
    if(sofar<0.70*double(limit)){
      r51::Costs c{aa,da,ao,dor,an,dn};
      r51::Graph base=r51::parse(best,n,m);
      auto bm=base.metric(c);
      if(bm.valid){
       std::string objective="area";
       if(r82policy.find("adp")!=std::string::npos)objective="adp";
       else if(r82policy.find("slack")!=std::string::npos)objective="slack";
       else if(r82policy.find("strict")!=std::string::npos)objective="strict";
       r82::Point original{"baseline",bm.area,bm.delay};
       r82::Point selected=original;
       std::vector<r82::Point>archive{original};
       const bool dual=r82policy.substr(0,4)=="dual";
       const std::vector<std::string>modes=dual?std::vector<std::string>{"shannon","sop"}:
                                               std::vector<std::string>{"shannon"};
       int roots=1500;
       if(const char* e=std::getenv("UFUG_R82_ROOT_CAP")){
          try{roots=std::clamp(std::stoi(e),100,4000);}catch(...){roots=1500;}
       }
       const double frac=0.10;
       const double search_budget=std::min(300.0,frac*double(limit));
       const auto tbegin=Clock::now();
       for(const auto&mode:modes){
         double used=std::chrono::duration<double,std::milli>(Clock::now()-tbegin).count();
         double wall=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
         if(used>=search_budget ||wall>=0.82*double(limit))break;
         double remaining=std::min(search_budget-used,0.80*double(limit)-wall);
         if(remaining<1.0)break;
         const char* rawsample=std::getenv("UFUG_R82_SAMPLING");
         std::string sampling=rawsample?rawsample:"priority";
         if(sampling!="priority"&&sampling!="stride")sampling="priority";
         auto result=r82cut::rewrite(base,c,target,mode,std::min(140.0,remaining),roots,sampling);
         auto met=result.graph.metric(c);
         if(!met.valid||met.delay>target)continue;
         r82::Point p{mode,met.area,met.delay};archive.push_back(p);
         const bool admissible=r82::eligible(original,p,target,objective);
         if(admissible && (selected.mode=="baseline"||r82::better(p,selected,objective))){
           best=result.graph.serialize();b.area=met.area;b.delay=met.delay;selected=p;
         }
         if(auto flag=std::getenv("UFUG_R82_PROFILE"))if(*flag=='1'){
           std::cerr<<"R82_STAGE policy="<<r82policy<<" mode="<<mode<<" roots="<<roots
             <<" visited="<<result.stats.visited_roots<<" cuts="<<result.stats.cuts
             <<" area="<<met.area<<" delay="<<met.delay
             <<" base_area="<<bm.area<<" base_delay="<<bm.delay
             <<" eligible="<<admissible<<" selected="<<(selected.mode==mode)
             <<" budget_hit="<<result.stats.budget_hit<<" ms="<<result.stats.elapsed_ms<<"\n";
         }
       }
       if(auto flag=std::getenv("UFUG_R82_PROFILE"))if(*flag=='1'){
         auto pf=r82::pareto(archive);
         for(const auto&p:pf)std::cerr<<"R82_PARETO mode="<<p.mode<<" area="<<p.area<<" delay="<<p.delay<<"\n";
         std::cerr<<"R82_FINAL policy="<<r82policy<<" chosen="<<selected.mode
             <<" area="<<b.area<<" delay="<<b.delay<<"\n";
       }
      }
    }
 }
 // Round 8.3: deterministic per-branch root-work quota with independent modes.
 // All optional candidates compete by complete live-DAG metrics; the frozen
 // Round 8.2.1 incumbent remains the safe fallback.
 if(r83policy!="off"){
   const std::vector<std::string> allowed={"stable_fast_area","stable_fast_adp",
     "stable_dual_area","stable_dual_adp","stable_dual_strict",
     "full_dual_area"};
   if(std::find(allowed.begin(),allowed.end(),r83policy)==allowed.end()){
     std::cerr<<"R83_ERROR unknown policy="<<r83policy<<"\n";return 19;
   }
   if(limit>=1000 && b.valid && b.delay<=target){
     r51::Costs c{aa,da,ao,dor,an,dn};
     r51::Graph base=r51::parse(best,n,m);
     auto met0=base.metric(c);
     const double already=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
     if(met0.valid && already<0.65*double(limit)){
       const bool dual=(r83policy.find("dual")!=std::string::npos);
       const std::vector<std::string> modes=dual?std::vector<std::string>{"shannon","sop"}:
                                                std::vector<std::string>{"shannon"};
       std::string objective="area";
       if(r83policy.find("adp")!=std::string::npos)objective="adp";
       if(r83policy.find("strict")!=std::string::npos)objective="strict";
       int root_cap=dual?900:1200;
       if(r83policy=="full_dual_area")root_cap=1500;
       // Deterministic generic budget reduction on short, high-output tasks.
       // More outputs produce larger candidate graphs and tighter watchdog risk.
       if(limit<=2000 && m>=20)root_cap=std::min(root_cap,600);
       if(const char* e=std::getenv("UFUG_R83_ROOT_CAP")){
         try{root_cap=std::clamp(std::stoi(e),100,1500);}catch(...){}
       }
       const double total_budget=std::min(360.,0.15*double(limit));
       const double branch_guard=dual?std::min(180.,total_budget*0.54):std::min(260.,total_budget);
       const auto overall_begin=Clock::now();
       r82::Point original{"baseline",met0.area,met0.delay},selected=original;
       std::vector<r82::Point> archive{original};
       std::string chosen_net=best;
       for(size_t j=0;j<modes.size();++j){
         const auto since=std::chrono::duration<double,std::milli>(Clock::now()-overall_begin).count();
         const auto wall=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
         if(since>=total_budget || wall>=0.77*double(limit))break;
         const double allowance=std::min(branch_guard,total_budget-since);
         if(allowance<5)break;
         const auto &mode=modes[j];
         auto result=r83cut::rewrite(base,c,target,mode,allowance,1500,"priority",root_cap);
         const auto cm=result.graph.metric(c);
         bool accepted=false;
         if(cm.valid && cm.delay<=target){
           r82::Point candidate{mode,cm.area,cm.delay};archive.push_back(candidate);
           if(r82::eligible(original,candidate,target,objective) &&
             (selected.mode=="baseline" || r82::better(candidate,selected,objective))){
              selected=candidate;chosen_net=result.graph.serialize();accepted=true;
           }
         }
         if(const char* p=std::getenv("UFUG_R83_PROFILE"))if(*p=='1'){
           std::cerr<<"R83_STAGE policy="<<r83policy<<" mode="<<mode
             <<" work_cap="<<root_cap<<" visited="<<result.stats.visited_roots
             <<" cuts="<<result.stats.cuts<<" materializations="<<result.stats.materializations
             <<" work_hit="<<result.stats.work_limit_hit<<" wall_hit="<<result.stats.budget_hit
             <<" elapsed_ms="<<result.stats.elapsed_ms
             <<" area="<<cm.area<<" delay="<<cm.delay
             <<" updated="<<accepted<<"\n";
         }
       }
       if(selected.mode!="baseline"){
         best=std::move(chosen_net);b.area=selected.area;b.delay=selected.delay;
       }
       if(const char* p=std::getenv("UFUG_R83_PROFILE"))if(*p=='1'){
         std::cerr<<"R83_FINAL policy="<<r83policy<<" chosen="<<selected.mode
                  <<" area="<<b.area<<" delay="<<b.delay<<"\n";
       }
     }
   }
 }

 // Round 8.4: priority-consistent Top-Q, and independently budgeted pilot->focus.
 // Search on the frozen incumbent, never on a partially rewritten candidate;
 // final metric acceptance is for the complete live DAG.
 const std::string r84policy=r84enabled?(r84env_early?r84env_early:"topology_dual"):"off";
 if(r84policy!="off"){
   const std::vector<std::string> allowed={"topq_fast","topq_dual","topq_dense",
      "topq_adp","topq_strict","topology_dual","adaptive_dual",
      "mixed33_dual","mixed66_dual"};
   if(std::find(allowed.begin(),allowed.end(),r84policy)==allowed.end()){
     std::cerr<<"R84_ERROR unknown policy="<<r84policy<<"\n";return 24;
   }
   if(limit>=1000 && b.valid && b.delay<=target){
     const r51::Costs c{aa,da,ao,dor,an,dn};
     const auto base=r51::parse(best,n,m);
     const auto bm=base.metric(c);
     const double already=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
     if(bm.valid && bm.delay<=target && already<0.65*double(limit)){
       const bool dual=r84policy!="topq_fast";
       const std::string objective=r84policy=="topq_adp"?"adp":
                                    r84policy=="topq_strict"?"strict":"area";
       const std::string sampling=r84policy=="topology_dual"?"priority":
          r84policy=="mixed33_dual"?"priority_mixed33":
          r84policy=="mixed66_dual"?"priority_mixed66":"priority_topq";
       const std::vector<std::string> modes=dual?std::vector<std::string>{"shannon","sop"}:
                                                std::vector<std::string>{"shannon"};
       int cap=r84policy=="topq_dense"?1100:(dual?900:1200);
       if(limit<=2000 && m>=20)cap=std::min(cap,600);
       if(const char* e=std::getenv("UFUG_R84_ROOT_CAP")){
         try{cap=std::clamp(std::stoi(e),100,1500);}catch(...){}
       }
       const double search_budget=std::min(360.,0.15*double(limit));
       const auto begin=Clock::now();
       r82::Point original{"baseline",bm.area,bm.delay},selected=original;
       std::string chosen_net=best;
       auto elapsed_run=[&](){return std::chrono::duration<double,std::milli>(Clock::now()-begin).count();};
       auto elapsed_all=[&](){return std::chrono::duration<double,std::milli>(Clock::now()-start).count();};
       struct Record{std::string mode;long long area;int delay;uint64_t visited;double elapsed;bool valid;};
       std::vector<Record> trials;
       auto try_one=[&](const std::string &mode,int work,double allowance,const std::string &kind)->bool{
         if(elapsed_run()>=search_budget || elapsed_all()>=0.77*double(limit))return false;
         const double remaining=std::min(allowance,search_budget-elapsed_run());
         if(remaining<5.0)return false;
         const auto result=r84cut::rewrite(base,c,target,mode,remaining,1500,sampling,work);
         const auto cm=result.graph.metric(c);
         const bool valid=cm.valid && cm.delay<=target;
         trials.push_back({mode,valid?cm.area:bm.area,valid?cm.delay:bm.delay,
            result.stats.visited_roots,result.stats.elapsed_ms,valid});
         bool accepted=false;
         if(valid){
           r82::Point cand{mode,cm.area,cm.delay};
           if(r82::eligible(original,cand,target,objective) &&
              (selected.mode=="baseline" || r82::better(cand,selected,objective))){
             selected=cand;chosen_net=result.graph.serialize();accepted=true;
           }
         }
         if(const char* p=std::getenv("UFUG_R84_PROFILE"))if(*p=='1'){
           std::cerr<<"R84_STAGE policy="<<r84policy<<" phase="<<kind<<" mode="<<mode
             <<" cap="<<work<<" visited="<<result.stats.visited_roots
             <<" scored="<<result.stats.ranked_topq_visited
             <<" cuts="<<result.stats.cuts<<" materializations="<<result.stats.materializations
             <<" work_hit="<<result.stats.work_limit_hit<<" wall_hit="<<result.stats.budget_hit
             <<" elapsed_ms="<<result.stats.elapsed_ms<<" area="<<cm.area<<" delay="<<cm.delay
             <<" updated="<<accepted<<"\n";
         }
         return true;
       };
       if(r84policy=="adaptive_dual"){
         // Low-cost deterministic *quality* pilots. Gain per completed root,
         // not wall-time, decides which branch gets a larger follow-up budget.
         int pilot=220,focus=1100;
         if(const char* e=std::getenv("UFUG_R84_PILOT_ROOTS")){
           try{pilot=std::clamp(std::stoi(e),80,450);}catch(...){}
         }
         if(const char* e=std::getenv("UFUG_R84_FOCUS_ROOTS")){
           try{focus=std::clamp(std::stoi(e),pilot,1500);}catch(...){}
         }
         const double pilot_allow=std::min(55.,search_budget*0.24);
         bool a=try_one("shannon",pilot,pilot_allow,"pilot");
         bool z=try_one("sop",pilot,pilot_allow,"pilot");
         if(a && z){
           auto&u=trials[0];auto&v=trials[1];
           // Cross multiplication avoids float-dependent tie-breaking.
           const long long gu=std::max(0LL,bm.area-u.area);
           const long long gv=std::max(0LL,bm.area-v.area);
           const bool sop_wins=gv*std::max<uint64_t>(1,u.visited)>gu*std::max<uint64_t>(1,v.visited);
           const std::string champion=sop_wins?"sop":"shannon";
           if(const char* p=std::getenv("UFUG_R84_PROFILE"))if(*p=='1')
              std::cerr<<"R84_ALLOCATION pilot="<<pilot<<" focus="<<focus
               <<" shannon_gain="<<gu<<" sop_gain="<<gv<<" champion="<<champion<<"\n";
           try_one(champion,focus,std::min(185.,search_budget*0.58),"focus");
         }
       }else{
         for(size_t j=0;j<modes.size();++j){
           const double per=dual?std::min(180.,search_budget*0.54):std::min(260.,search_budget);
           if(!try_one(modes[j],cap,per,"full"))break;
         }
       }
       if(selected.mode!="baseline"){
         best=std::move(chosen_net);b.area=selected.area;b.delay=selected.delay;
       }
       if(const char* p=std::getenv("UFUG_R84_PROFILE"))if(*p=='1')
          std::cerr<<"R84_FINAL policy="<<r84policy<<" chosen="<<selected.mode
                   <<" area="<<b.area<<" delay="<<b.delay
                   <<" branches="<<trials.size()<<" total_ms="<<elapsed_run()<<"\n";
     }
   }
 }
 // Round 8.5: self-contained final-source research branch, with explicit
 // branch-order and unused-budget experiments.  The frozen Round8.4 path is
 // untouched and can be invoked with UFUG_R85_POLICY=off.
 if(r85enabled){
   const std::vector<std::string> allowed={"dual_shannon_first","dual_sop_first",
      "dense_shannon_first","dense_sop_first","sop_only","budget_reclaim"};
   if(std::find(allowed.begin(),allowed.end(),r85policy)==allowed.end()){
     std::cerr<<"R85_ERROR unknown policy="<<r85policy<<"\n";return 25;
   }
   if(limit>=1000 && b.valid && b.delay<=target){
     const r51::Costs c{aa,da,ao,dor,an,dn};
     const auto base=r51::parse(best,n,m);
     const auto base_metric=base.metric(c);
     const double entered=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
     if(base_metric.valid && base_metric.delay<=target && entered<0.65*double(limit)){
       const bool sopfirst=r85policy=="dual_sop_first" || r85policy=="dense_sop_first" ||
                            r85policy=="sop_only";
       const bool single=r85policy=="sop_only";
       const bool reclaim=r85policy=="budget_reclaim";
       int cap=(r85policy=="dense_shannon_first" || r85policy=="dense_sop_first")?1100:900;
       if(limit<=2000 && m>=20)cap=std::min(cap,600);
       if(const char*e=std::getenv("UFUG_R85_ROOT_CAP")){
         try{cap=std::clamp(std::stoi(e),100,1500);}catch(...){}
       }
       const double search_budget=std::min(360.0,0.15*double(limit));
       const auto search_started=Clock::now();
       auto elapsed_search=[&](){return std::chrono::duration<double,std::milli>(Clock::now()-search_started).count();};
       auto elapsed_all=[&](){return std::chrono::duration<double,std::milli>(Clock::now()-start).count();};
       r82::Point baseline{"baseline",base_metric.area,base_metric.delay},selected=baseline;
       std::string selected_net=best;
       std::vector<std::string> order=single?std::vector<std::string>{"sop"}:
             sopfirst?std::vector<std::string>{"sop","shannon"}:
                      std::vector<std::string>{"shannon","sop"};
       for(size_t j=0;j<order.size();++j){
         const double overall=elapsed_all();
         if(elapsed_search()>=search_budget || overall>=0.77*double(limit))break;
         // Reclaim: return any unused first-branch time to the second branch;
         // the global cap remains unchanged and still reserves >=23% runtime.
         const double nominal=single?std::min(260.0,search_budget):
                                     std::min(180.0,search_budget*0.54);
         const double available=std::min(search_budget-elapsed_search(),
                                 0.77*double(limit)-overall);
         const double allowance=std::min(reclaim && j>0?search_budget:nominal,available);
         if(allowance<5.)break;
         int branch_cap=(reclaim && j>0)?std::min(1500,cap+300):cap;
         const auto candidate=r84cut::rewrite(base,c,target,order[j],allowance,
                                               1500,"priority_topq",branch_cap);
         const auto cm=candidate.graph.metric(c);
         bool selected_this=false;
         if(cm.valid && cm.delay<=target){
           r82::Point p{order[j],cm.area,cm.delay};
           if(r82::eligible(baseline,p,target,"area") &&
                (selected.mode=="baseline" || r82::better(p,selected,"area"))){
             selected=p;selected_net=candidate.graph.serialize();selected_this=true;
           }
         }
         if(const char*pr=std::getenv("UFUG_R85_PROFILE"))if(*pr=='1'){
           std::cerr<<"R85_STAGE policy="<<r85policy<<" mode="<<order[j]
            <<" cap="<<branch_cap<<" visited="<<candidate.stats.visited_roots
            <<" work_hit="<<candidate.stats.work_limit_hit
            <<" wall_hit="<<candidate.stats.budget_hit
            <<" stage_ms="<<candidate.stats.elapsed_ms
            <<" wall_ms="<<elapsed_all()<<" area="<<cm.area
            <<" delay="<<cm.delay<<" accepted="<<selected_this<<"\n";
         }
       }
       if(selected.mode!="baseline"){
         best=std::move(selected_net);b.area=selected.area;b.delay=selected.delay;
       }
       if(const char*pr=std::getenv("UFUG_R85_PROFILE"))if(*pr=='1'){
         std::cerr<<"R85_FINAL policy="<<r85policy<<" area="<<b.area
                  <<" delay="<<b.delay<<" search_ms="<<elapsed_search()
                  <<" wall_ms="<<elapsed_all()<<"\n";
       }
     }
   }
 }
 ofstream out(argv[2]);out<<best;
 cerr<<"completed="<<completed<<" chosen="<<chosen<<" area="<<b.area<<" delay="<<b.delay<<'\n';
 if(r71_trace)std::cerr<<"R71_TRACE event=finish total_ms="<<r71_elapsed()
   <<" area="<<b.area<<" delay="<<b.delay<<" completed="<<completed<<"\n";
 return out?0:7;
}
