#include <bits/stdc++.h>
using namespace std;
struct BKey {int v,lo,hi;bool operator==(const BKey&o)const{return v==o.v && lo==o.lo && hi==o.hi;}};
struct H3 {size_t operator()(const BKey&k)const { uint64_t z=((uint64_t)(unsigned)k.v<<55)^((uint64_t)(unsigned)k.lo<<26)^(unsigned)k.hi; z^=z>>30;z*=0xbf58476d1ce4e5b9ULL;z^=z>>27;z*=0x94d049bb133111ebULL;return z^(z>>31);}};
struct BNode{int v,lo,hi;};
struct Gate{string type;int a,b;};
struct GKey{int t,a,b;bool operator==(const GKey&o)const{return t==o.t&&a==o.a&&b==o.b;}};
struct HKey{size_t operator()(const GKey &k)const{return H3{}({k.t,k.a,k.b});}};
int main(int argc,char**argv){
 if(argc<3)return 2;
 ifstream in(argv[1]);ofstream out(argv[2]);if(!in||!out)return 3;
 int n,m;in>>n>>m; if(n<1 || n>22 || m<1)return 4;
 size_t N=1ull<<n; vector<unsigned char> T(N*m);string bits;
 for(size_t i=0;i<N;i++){in>>bits; if((int)bits.size()!=m)return 5;for(int j=0;j<m;j++)T[i*m+j]=bits[j]-'0';}
 int aa,da,ao,doo,an,dn,D;in>>aa>>da>>ao>>doo>>an>>dn>>D;
 // BDD global canonical graph, terminal 0 and 1.
 vector<BNode> nodes;nodes.reserve(N);nodes.push_back({-1,0,0}); nodes.push_back({-1,1,1});
 unordered_map<BKey,int,H3> cache;cache.reserve(min((size_t)N*2,(size_t)5000000));
 vector<int> roots(m);vector<int> cur(N),next;
 for(int j=0;j<m;j++){
  cur.resize(N);
  for(size_t i=0;i<N;i++)cur[i]=T[i*m+j];
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
  int id=n+1+(int)gates.size();gates.push_back({t==0?"AND2":t==1?"OR2":"NOT",a,b}); gcache.emplace(k,id);A+=(t==0?aa:t==1?ao:an);return id;};
 int ONE=mk(2,0,0); // canonical 1
 function<int(int)> neg=[&](int a)->int{
  if(a==0)return ONE;if(a==ONE)return 0;
  auto it=gcache.find({2,a,0});if(it!=gcache.end())return it->second;
  if(a>n){Gate &g=gates[a-(n+1)];if(g.type=="NOT")return g.a;}
  return mk(2,a,0);
 };
 function<int(int,int)> land=[&](int a,int b)->int{if(a==0||b==0)return 0;if(a==ONE)return b;if(b==ONE)return a;if(a==b)return a;if(neg(a)==b)return 0;return mk(0,a,b);};
 function<int(int,int)> lor=[&](int a,int b)->int{if(a==ONE||b==ONE)return ONE;if(a==0)return b;if(b==0)return a;if(a==b)return a;if(neg(a)==b)return ONE;return mk(1,a,b);};
 vector<int> done(nodes.size(),-1);done[0]=0;done[1]=ONE;
 function<int(int)> build=[&](int id)->int {if(done[id]>=0)return done[id];auto node=nodes[id];int x=node.v+1;
  int lo=build(node.lo),hi=build(node.hi),result;
  if(lo==hi)result=lo;
  else if(lo==0)result=land(x,hi);
  else if(hi==0)result=land(neg(x),lo);
  else if(lo==ONE)result=lor(neg(x),hi);
  else if(hi==ONE)result=lor(x,lo);
  else result=lor(land(neg(x),lo),land(x,hi));
  done[id]=result;return result;
 };
 vector<int> outs;for(int r:roots)outs.push_back(build(r));
 // remove unused gates including unnecessary ONE if not needed; preserve ID indexing by regenerating used gates.
 vector<char> use(gates.size());function<void(int)> mark=[&](int id){if(id<=n)return;int j=id-n-1;if(use[j])return;use[j]=1;mark(gates[j].a);if(gates[j].type!="NOT")mark(gates[j].b);};
 for(int o:outs)mark(o);
 vector<int> new_ids(gates.size());int k=n+1;
 for(size_t i=0;i<gates.size();i++)if(use[i])new_ids[i]=k++;
 for(size_t i=0;i<gates.size();i++)if(use[i]){auto g=gates[i];auto fix=[&](int x){return x<=n?x:new_ids[x-n-1];}; out<<new_ids[i]<<" "<<g.type<<" "<<fix(g.a);if(g.type!="NOT")out<<" "<<fix(g.b);out<<"\n";}
 for(int j=0;j<m;j++){if(j)out<<" ";out<<(outs[j]<=n?outs[j]:new_ids[outs[j]-n-1]);}out<<"\n";
 return 0;
}
