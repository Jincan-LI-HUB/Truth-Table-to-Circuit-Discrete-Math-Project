#include <bits/stdc++.h>
using namespace std;
struct BKey {int v,lo,hi;bool operator==(const BKey&o)const{return v==o.v && lo==o.lo && hi==o.hi;}};
struct H3 {size_t operator()(const BKey&k)const { uint64_t z=((uint64_t)(unsigned)k.v<<55)^((uint64_t)(unsigned)k.lo<<26)^(unsigned)k.hi; z^=z>>30;z*=0xbf58476d1ce4e5b9ULL;z^=z>>27;z*=0x94d049bb133111ebULL;return z^(z>>31);}};
struct BNode{int v,lo,hi;};
struct Gate{string type;int a,b;};
struct GKey{int t,a,b;bool operator==(const GKey&o)const{return t==o.t&&a==o.a&&b==o.b;}};
struct HKey{size_t operator()(const GKey &k)const{return H3{}({k.t,k.a,k.b});}};
struct Opt {string order;bool fast, rewrite, expand;int cubemode,margin;bool affine=false;};
string run_synth(const string &input,const Opt &opt){
 ifstream in(input);ostringstream out;if(!in)return {};
 int n,m;in>>n>>m; if(n<1 || n>22 || m<1)return {};
 size_t N=1ull<<n; vector<unsigned char> T(N*m);string bits;
 for(size_t i=0;i<N;i++){in>>bits; if((int)bits.size()!=m)return {};for(int j=0;j<m;j++)T[i*m+j]=bits[j]-'0';}
 int aa,da,ao,doo,an,dn,D;in>>aa>>da>>ao>>doo>>an>>dn>>D;
 // BDD global canonical graph, terminal 0 and 1.
 vector<BNode> nodes;nodes.reserve(N);nodes.push_back({-1,0,0});
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
 vector<size_t> orig(N);for(size_t z=1;z<N;z++){int bit=__builtin_ctzll(z);orig[z]=orig[z&(z-1)]|(1ull<<(n-1-perm[n-1-bit]));}
 vector<int> roots(m);vector<int> cur(N),next;
 for(int j=0;j<m;j++){
  cur.resize(N);
  for(size_t i=0;i<N;i++)cur[i]=T[orig[i]*m+j];
  size_t count=N;
  for(int v=n-1;v>=0;v--){
   next.resize(count/2);
   for(size_t k=0;k<count/2;k++){
    int lo=cur[2*k],hi=cur[2*k+1];
    if(lo==hi){next[k]=lo;continue;}
    int flip=(hi&1);int normlo=lo^flip,normhi=hi^flip;
    BKey key={v,normlo,normhi};auto it=cache.find(key);
    if(it!=cache.end()){next[k]=it->second^flip;continue;}
    int id=nodes.size();nodes.push_back({v,normlo,normhi});cache.emplace(key,id<<1);next[k]=(id<<1)^flip;
   }
   cur.swap(next);count/=2;
  }
  roots[j]=cur[0];
 }
 // Emit gates with structural sharing, constant folding, and NOT sharing.
 vector<Gate> gates;
 unordered_map<GKey,int,HKey> gcache;gcache.reserve(nodes.size()*2);
 vector<int> ready(n+1);int A=0;
 auto mk=[&](int t,int a,int b)->int {if(t!=2&&a>b)swap(a,b); GKey k{t,a,b}; auto it=gcache.find(k);if(it!=gcache.end())return it->second;
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

 const uint64_t cb=(1ULL<<n), BAD=~0ULL;
 vector<uint64_t> af(nodes.size()*2,BAD);
 af[0]=0;af[1]=cb;
 for(size_t k=1;k<nodes.size();k++){
  const auto &nd=nodes[k];
  if(af[nd.lo]!=BAD && af[nd.hi]!=BAD && (af[nd.lo]^af[nd.hi])==cb){
    af[2*k]=af[nd.lo]^(1ULL<<perm[nd.v]);
    af[2*k+1]=af[2*k]^cb;
  }
 }
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
  if(done[id]>=0)return done[id];
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

struct Stats {bool valid=false;long long area=0;int delay=0;};
Stats stats(const string&net,int n,int m,int aa,int da,int ao,int dor,int an,int dn){
 istringstream in(net);string line;vector<int> arr(n+1);long long area=0;int count=0;
 while(getline(in,line)){
  if(line.empty())continue;
  istringstream ss(line);vector<string> parts;string z;while(ss>>z)parts.push_back(z);
  if(parts.size()>=3 && (parts[1]=="AND2"||parts[1]=="OR2"||parts[1]=="NOT")){
   int id=stoi(parts[0]),u=stoi(parts[2]),v=0;
   if(id!=n+1+count||u<0||u>=id)return {};
   if(parts[1]=="NOT"){
    if(parts.size()!=3)return {};
    arr.push_back(arr[u]+dn);area+=an;
   }else{
    if(parts.size()!=4)return {};
    v=stoi(parts[3]);if(v<0||v>=id)return {};
    if(parts[1]=="AND2"){arr.push_back(max(arr[u],arr[v])+da);area+=aa;}
    else{arr.push_back(max(arr[u],arr[v])+dor);area+=ao;}
   }
   ++count;
  }else{
   if(int(parts.size())!=m)return {};
   int delay=0;
   for(const string&t:parts){int v=stoi(t);if(v<0||v>=int(arr.size()))return {};delay=max(delay,arr[v]);}
   return {true,area,delay};
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
string run_synth(const string &input,const Opt &opt){
 ifstream in(input);ostringstream out;if(!in)return {};
 int n,m;in>>n>>m; if(n<1 || n>22 || m<1)return {};
 size_t N=1ull<<n; vector<unsigned char> T(N*m);string bits;
 for(size_t i=0;i<N;i++){in>>bits; if((int)bits.size()!=m)return {};for(int j=0;j<m;j++)T[i*m+j]=bits[j]-'0';}
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
 vector<size_t> orig(N);for(size_t z=1;z<N;z++){int bit=__builtin_ctzll(z);orig[z]=orig[z&(z-1)]|(1ull<<(n-1-perm[n-1-bit]));}
 vector<int> roots(m);vector<int> cur(N),next;
 for(int j=0;j<m;j++){
  cur.resize(N);
  for(size_t i=0;i<N;i++)cur[i]=T[orig[i]*m+j];
  size_t count=N;
  for(int v=n-1;v>=0;v--){
   next.resize(count/2);
   for(size_t k=0;k<count/2;k++){
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
 auto mk=[&](int t,int a,int b)->int {if(t!=2&&a>b)swap(a,b); GKey k{t,a,b}; auto it=gcache.find(k);if(it!=gcache.end())return it->second;
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
 function<int(int)> build=[&](int id)->int {if(done[id]>=0)return done[id];auto node=nodes[id];int x=perm[node.v]+1;
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
 if(argc!=3)return 2;
 ifstream in(argv[1]);int n,m;string line;
 if(!(in>>n>>m))return 3;
 for(int k=0;k<(1<<n);k++)if(!(in>>line))return 4;
 int aa,da,ao,dor,an,dn,target;
 if(!(in>>aa>>da>>ao>>dor>>an>>dn>>target))return 5;
 long long limit=0;in>>limit;
 using Clock=chrono::steady_clock;
 auto start=Clock::now();
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
 string best;Stats b;int chosen=-1,completed=0;
 for(int i=0;i<int(variants.size());i++){
  // Heuristic search budget leaves space for writing and evaluation overhead.
  if(i && limit>0){
   auto elapsed=chrono::duration<double,milli>(Clock::now()-start).count();
   if(elapsed>0.75*limit)break;
  }
  variants[i].affine=true;
  string net=run_synth(argv[1],variants[i]);
  if(net.empty())continue;
  auto z=stats(net,n,m,aa,da,ao,dor,an,dn);if(!z.valid)continue;
  string bal=rebalance(net,n,m,aa,da,ao,dor,an,dn);
  auto bz=stats(bal,n,m,aa,da,ao,dor,an,dn);
  auto ranklocal=[&](Stats x){return make_tuple(max(0,x.delay-target),x.delay<=target?x.area:0LL,x.delay,x.area);};
  if(bz.valid && ranklocal(bz)<ranklocal(z)){net=std::move(bal);z=bz;}
  // Greedy timing-slack recovery; keep only improvements to full-circuit ranking.
  if(z.delay <= target){
    string ar=area_recover(net,n,m,aa,da,ao,dor,an,dn,target,0);
    auto az=stats(ar,n,m,aa,da,ao,dor,an,dn);
    if(az.valid && ranklocal(az)<ranklocal(z)){net=std::move(ar);z=az;}
  }
  completed++;
  auto rank=[&](Stats x){return make_tuple(max(0,x.delay-target), x.delay<=target?x.area:0LL, x.delay, x.area);};
  if(!b.valid || rank(z)<rank(b)) {best=std::move(net);b=z;chosen=i;}
 }
 // A distinct legacy representation remains valuable: complementary normalization
 // should not erase earlier, smaller Area solutions. Only attempt this low-cost
 // fallback for moderate input dimensions and adequate declared runtime budgets.
 if((n<=16 && limit>=5000) || (n<=10 && limit>=100)){
   vector<legacy::Opt> legacyMethods={
      {"influence-desc",false,true,true,1,0},
      {"influence-desc",true,false,true,0,0},
      {"natural",true,false,true,1,0}
   };
   for(const auto &opt:legacyMethods){
      if(limit>0){
        double elapsed=chrono::duration<double,milli>(Clock::now()-start).count();
        if(elapsed>0.72*limit)break;
      }
      string trial=legacy::run_synth(argv[1],opt);
      auto z=stats(trial,n,m,aa,da,ao,dor,an,dn);
      if(!z.valid)continue;
      if(z.delay<=target){
         string ar=area_recover(trial,n,m,aa,da,ao,dor,an,dn,target,0);
         auto az=stats(ar,n,m,aa,da,ao,dor,an,dn);
         if(az.valid && make_tuple(max(0,az.delay-target),az.area,az.delay)<
                         make_tuple(max(0,z.delay-target),z.area,z.delay)){
            z=az;trial=std::move(ar);
         }
      }
      auto rank=[&](Stats x){return make_tuple(max(0,x.delay-target),x.delay<=target?x.area:0LL,x.delay,x.area);};
      if(!b.valid || rank(z)<rank(b)){
         best=std::move(trial);b=z;chosen=100+completed;
      }
      ++completed;
   }
 }
 if(!b.valid)return 6;
 ofstream out(argv[2]);out<<best;
 cerr<<"completed="<<completed<<" chosen="<<chosen<<" area="<<b.area<<" delay="<<b.delay<<'\n';
 return out?0:7;
}
