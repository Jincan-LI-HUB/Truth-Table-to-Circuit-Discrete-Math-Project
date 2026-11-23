#pragma once
// Round 8.2.1: resource-limited streaming semantics + bounded-support fallback.
// This header is designed to be included AFTER typed_netgraph.hpp.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <functional>
#include <limits>
#include <numeric>
#include <queue>
#include <unordered_map>
#include <sstream>
#include <string>
#include <vector>
namespace r821 {
struct Probe {
  bool solved=false;
  bool attempted=false;
  std::string netlist;
  int support=-1;
  long long area=-1;
  int delay=-1;
  std::string reason;
};
inline uint64_t saturation_mul(uint64_t x,uint64_t y){
  return (y!=0 && x>std::numeric_limits<uint64_t>::max()/y)?
      std::numeric_limits<uint64_t>::max():x*y;
}
inline uint64_t saturation_add(uint64_t x,uint64_t y){
  return x>std::numeric_limits<uint64_t>::max()-y?
      std::numeric_limits<uint64_t>::max():x+y;
}
// Conservative *admission* estimate for existing eager ROBDD implementation.
// Not a proof of peak-RSS compliance. No attempt is made to undercount hash
// buckets, nodes, immutable caches or competing outputs. If this is rejected,
// use the bounded-support low-memory fallback or return an explicit error.
inline uint64_t bdd_reservation_estimate_bytes(int n,int m){
  if(n<1 || n>20 || m<1)return std::numeric_limits<uint64_t>::max();
  uint64_t N=1ULL<<n;
  return saturation_add(3ULL*1024*1024,
    saturation_mul(N,saturation_add(uint64_t(m),104ULL)));
}
inline bool bdd_admitted(int n,int m,long long ram_kb){
  if(ram_kb==0)return true;
  if(ram_kb<0)return false;
  return saturation_mul(uint64_t(ram_kb),1024ULL)>=bdd_reservation_estimate_bytes(n,m);
}

// Bounded reduced-order BDD built directly from packed truth bits.
// Unlike the frozen builder, no N-element size_t permutation, eager N-node
// reserve, or 2*N hash-bucket reserve is used. A deterministic node cap is
// chosen from the RAM budget before allocating the 2^n/2 integer row buffer.
inline Probe bounded_packed_bdd(const std::vector<uint64_t>& packed,int n,int m,
          const r51::Costs& cost,int target,long long ram_kb){
  Probe out;out.attempted=true;out.reason="packed_bdd_not_admitted";
  if(ram_kb<=0 || n<1 || n>20 || m<1)return out;
  const uint64_t N=1ULL<<n,words=(N+63)/64;
  const uint64_t cap=saturation_mul(uint64_t(ram_kb),1024ULL);
  const uint64_t buffer=saturation_mul(N,3); // cur N/2 ints + next N/4 ints.
  const uint64_t overhead=saturation_add(4ULL*1024*1024,
                                 saturation_add(buffer,saturation_mul(words,uint64_t(m)*8ULL)));
  if(overhead>=cap || (cap-overhead)/240<64)return out;
  const int max_nodes=int(std::min<uint64_t>(50000,(cap-overhead)/240));
  struct Key{int v,lo,hi;bool operator==(const Key&z)const{
    return v==z.v&&lo==z.lo&&hi==z.hi;
  }};
  struct Hash{size_t operator()(const Key&k)const{
    uint64_t x=uint32_t(k.v);
    x=(x*0x9e3779b97f4a7c15ULL)^uint32_t(k.lo);
    x=(x*0xbf58476d1ce4e5b9ULL)^uint32_t(k.hi);
    return size_t(x^(x>>31));
  }};
  std::vector<Key> nodes;
  std::unordered_map<Key,int,Hash> intern;
  bool exceeded=false;
  auto add=[&](int var,int lo,int hi)->int{
    if(lo==hi)return lo;
    Key key{var,lo,hi};auto it=intern.find(key);
    if(it!=intern.end())return it->second;
    if(int(nodes.size())>=max_nodes){exceeded=true;return -1;}
    const int id=int(nodes.size())+2;
    nodes.push_back(key);intern.emplace(key,id);return id;
  };
  auto value=[&](int j,uint64_t row)->int{
    return int((packed[uint64_t(j)*words+(row>>6)]>>(row&63))&1ULL);
  };
  std::vector<int> roots;
  for(int j=0;j<m && !exceeded;j++){
    std::vector<int> cur(N/2),next;
    for(uint64_t i=0;i<N/2;i++){
      int z=add(n-1,value(j,i*2),value(j,i*2+1));
      if(z<0)break;
      cur[i]=z;
    }
    if(exceeded)break;
    size_t count=N/2;
    for(int v=n-2;v>=0;v--){
      next.resize(count/2);
      for(size_t i=0;i<count/2;i++){
        int z=add(v,cur[2*i],cur[2*i+1]);
        if(z<0)break;
        next[i]=z;
      }
      if(exceeded)break;
      cur.swap(next);count/=2;
    }
    if(!exceeded)roots.push_back(cur[0]);
  }
  if(exceeded || int(roots.size())!=m){out.reason="packed_bdd_node_cap";return out;}
  r51::Graph empty(n,m);r51::Builder builder(empty);
  const int one=builder.add(2,0,0,cost);
  auto neg=[&](int id){
    if(id==0)return one;
    if(id==one)return 0;
    if(id>n && builder.graph.nodes[id].op==2)return builder.graph.nodes[id].a;
    return builder.add(2,id,0,cost);
  };
  std::vector<int> mapped(nodes.size()+2,0);
  mapped[0]=0;mapped[1]=one;
  for(size_t i=0;i<nodes.size();i++){
    Key key=nodes[i];
    int lo=mapped[key.lo],hi=mapped[key.hi],x=key.v+1;
    if(lo==hi){mapped[i+2]=lo;continue;}
    int nx=neg(x);
    if(lo==0)mapped[i+2]=(hi==one?x:builder.add(0,x,hi,cost));
    else if(hi==0)mapped[i+2]=(lo==one?nx:builder.add(0,nx,lo,cost));
    else if(lo==one)mapped[i+2]=builder.add(1,nx,hi,cost);
    else if(hi==one)mapped[i+2]=builder.add(1,x,lo,cost);
    else{
      int a=builder.add(0,nx,lo,cost),b=builder.add(0,x,hi,cost);
      mapped[i+2]=builder.add(1,a,b,cost);
    }
  }
  std::vector<int> outputs;for(int root:roots)outputs.push_back(mapped[root]);
  auto graph=builder.finish(outputs);auto met=graph.metric(cost);
  auto balanced=r51::rebalance(graph,cost);
  auto bm=balanced.metric(cost);
  if(bm.valid && (bm.delay<met.delay || (bm.delay==met.delay && bm.area<met.area))){
    graph=std::move(balanced);met=bm;
  }
  if(met.valid && met.delay<=target){
    out.solved=true;out.netlist=graph.serialize();out.area=met.area;
    out.delay=met.delay;out.reason="memory_bounded_packed_bdd";out.support=n;
  }else out.reason="packed_bdd_delay_infeasible";
  return out;
}

// First input pass does not materialize 2^n row permutations or full BDD nodes.
// In a low-RAM setting, packed truth storage costs ceil(2^n/64)*m*8 bytes.
// It is optional and capped to <=1/6 of the declared RAM limit.
inline Probe compact_probe(const std::string&path,int n,int m,
               const r51::Costs&cost,int target,long long ram_kb){
  Probe out;out.attempted=true;
  if(n<1||n>20||m<1){out.reason="invalid_dimensions";return out;}
  std::ifstream in(path);int r_n=0,r_m=0;
  if(!(in>>r_n>>r_m)||r_n!=n||r_m!=m){out.reason="invalid_header";return out;}
  const uint64_t N=1ULL<<n, words=(N+63)/64;
  const uint64_t pack_bytes=saturation_mul(saturation_mul(words,uint64_t(m)),8);
  const bool pack=(ram_kb>0 &&
    pack_bytes<=saturation_mul(uint64_t(ram_kb),1024ULL)/6 && pack_bytes<=8ULL*1024*1024);
  std::vector<uint64_t> packed;
  if(pack)packed.assign(words*uint64_t(m),0ULL);
  const int options=2+2*n;
  std::vector<uint8_t> candidates(size_t(m)*size_t(options),1);
  std::string bits;
  for(uint64_t row=0;row<N;row++){
    if(!(in>>bits)||int(bits.size())!=m){out.reason="malformed_truth_table";return out;}
    const uint64_t base=uint64_t(row>>6);
    for(int j=0;j<m;j++){
      const int y=bits[j]-'0';
      if(y!=0 && y!=1){out.reason="nonbinary_row";return out;}
      if(pack && y)packed[uint64_t(j)*words+base]|=1ULL<<(row&63);
      uint8_t* c=candidates.data()+size_t(j)*options;
      c[0]&=uint8_t(y==0);c[1]&=uint8_t(y==1);
      for(int v=0;v<n;v++){
        const int b=(row>>(n-1-v))&1;
        c[2+2*v]&=uint8_t(y==b);
        c[3+2*v]&=uint8_t(y!=b);
      }
    }
  }
  std::vector<int> simple(m,-1);
  bool all_simple=true;
  for(int j=0;j<m;j++){
    for(int kind=0;kind<options;kind++)if(candidates[size_t(j)*options+kind]){
      simple[j]=kind;break;
    }
    if(simple[j]==-1)all_simple=false;
  }
  if(all_simple){
    r51::Graph g(n,m);
    r51::Builder b(g);
    std::vector<int> outputs;
    for(int kind:simple){
      if(kind==0)outputs.push_back(0);
      else if(kind==1)outputs.push_back(b.add(2,0,0,cost));
      else if((kind&1)==0)outputs.push_back(1+(kind-2)/2);
      else outputs.push_back(b.add(2,1+(kind-3)/2,0,cost));
    }
    auto result=b.finish(outputs);
    auto metric=result.metric(cost);
    if(metric.valid && metric.delay<=target){
      out.solved=true;out.netlist=result.serialize();out.area=metric.area;
      out.delay=metric.delay;out.support=0;out.reason="streaming_literals";
      return out;
    }
  }
  if(!pack){out.reason="nontrivial_without_compact_storage";return out;}
  auto value=[&](int j,uint64_t row)->bool{
    return (packed[size_t(j)*words+(row>>6)]>>(row&63))&1ULL;
  };
  // Affine functions can use all n inputs yet admit extremely small circuits.
  // Check the complete truth table, not merely a sample or a syntactic form.
  std::vector<std::vector<int>> linear(m);
  std::vector<int> affine_constant(m,0);
  bool all_affine=true;
  for(int j=0;j<m;j++){
    affine_constant[j]=int(value(j,0));
    for(int v=0;v<n;v++){
      if(int(value(j,1ULL<<(n-1-v)))!=affine_constant[j])
        linear[j].push_back(v);
    }
    for(uint64_t row=0;row<N;row++){
      int predicted=affine_constant[j];
      for(int v:linear[j])predicted^=int((row>>(n-1-v))&1ULL);
      if(predicted!=int(value(j,row))){all_affine=false;break;}
    }
    if(!all_affine)break;
  }
  if(all_affine){
    r51::Graph empty(n,m);r51::Builder b(empty);
    int one=b.add(2,0,0,cost);
    auto neg=[&](int id){
      if(id==0)return one;
      if(id==one)return 0;
      if(id>n && b.graph.nodes[id].op==2)return b.graph.nodes[id].a;
      return b.add(2,id,0,cost);
    };
    auto bxor=[&](int a,int c){
      if(a==0)return c;
      if(c==0)return a;
      // Shannon-independent XOR = (a OR c) AND NOT(a AND c).
      int t=b.add(1,a,c,cost),u=b.add(0,a,c,cost);
      return b.add(0,t,neg(u),cost);
    };
    std::vector<int> outputs;
    for(int j=0;j<m;j++){
      // Lowest-arrival-first balanced reduction; structural hashing reuses
      // equal subexpressions across affine outputs.
      using Item=std::pair<int,int>;
      std::priority_queue<Item,std::vector<Item>,std::greater<Item>> pq;
      for(int v:linear[j])pq.push({0,v+1});
      int root=0;
      while(pq.size()>1){
        int a=pq.top().second;pq.pop();int c=pq.top().second;pq.pop();
        int z=bxor(a,c);pq.push({b.ready[z],z});
      }
      if(!pq.empty())root=pq.top().second;
      if(affine_constant[j])root=neg(root);
      outputs.push_back(root);
    }
    auto graph=b.finish(outputs);
    auto met=graph.metric(cost);
    if(met.valid && met.delay<=target){
      out.solved=true;out.netlist=graph.serialize();out.area=met.area;
      out.delay=met.delay;out.reason="packed_affine";out.support=n;
      return out;
    }
  }
  // True semantic support is measured per output. A union of supports can
  // exceed ten while each separate output still has a small local support.
  std::vector<std::vector<int>> supports(m);
  int union_support=0;
  for(int v=0;v<n;v++){
    const uint64_t step=1ULL<<(n-1-v);
    bool any=false;
    for(int j=0;j<m;j++){
      bool used=false;
      for(uint64_t row=0;row<N && !used;row+=step*2){
        for(uint64_t i=0;i<step;i++){
          if(value(j,row+i)!=value(j,row+step+i)){used=true;break;}
        }
      }
      if(used){supports[j].push_back(v);any=true;}
    }
    if(any)union_support++;
  }
  out.support=union_support;
  for(const auto&support:supports)if(support.size()>10){
    auto bdd=bounded_packed_bdd(packed,n,m,cost,target,ram_kb);
    if(bdd.solved)return bdd;
    out.reason=bdd.reason;
    return out;
  }
  r51::Graph empty(n,m);r51::Builder builder(empty);
  const int one=builder.add(2,0,0,cost);
  auto negative=[&](int id){
    if(id==0)return one;
    if(id==one)return 0;
    if(id>n && builder.graph.nodes[id].op==2)return builder.graph.nodes[id].a;
    return builder.add(2,id,0,cost);
  };
  std::vector<int> outputs;
  for(int j=0;j<m;j++){
    const auto&support=supports[j];
    const int k=int(support.size()),reduced=1<<k;
    std::vector<uint8_t> tt(reduced);
    for(int idx=0;idx<reduced;idx++){
      uint64_t orig=0;
      for(int q=0;q<k;q++)if((idx>>(k-1-q))&1)
        orig|=1ULL<<(n-1-support[q]);
      tt[idx]=value(j,orig);
    }
    std::function<int(int,int,int)> rec;
    rec=[&](int at,int len,int dep)->int{
      uint8_t v=tt[at];bool constant=true;
      for(int i=1;i<len;i++)if(tt[at+i]!=v){constant=false;break;}
      if(constant)return v?one:0;
      if(dep>=k)throw std::runtime_error("inconsistent reduced support");
      const int half=len/2;
      const int lo=rec(at,half,dep+1);
      const int hi=rec(at+half,half,dep+1);
      if(lo==hi)return lo;
      const int x=support[dep]+1;
      const int nx=negative(x);
      if(lo==0)return hi==one?x:builder.add(0,x,hi,cost);
      if(hi==0)return lo==one?nx:builder.add(0,nx,lo,cost);
      if(lo==one)return builder.add(1,nx,hi,cost);
      if(hi==one)return builder.add(1,x,lo,cost);
      int a=builder.add(0,nx,lo,cost),b=builder.add(0,x,hi,cost);
      return builder.add(1,a,b,cost);
    };
    outputs.push_back(rec(0,reduced,0));
  }
  auto built=builder.finish(outputs);
  auto met=built.metric(cost);
  auto balanced=r51::rebalance(built,cost);
  auto bm=balanced.metric(cost);
  if(bm.valid && (bm.delay<met.delay || (bm.delay==met.delay && bm.area<met.area))){
    built=std::move(balanced);met=bm;
  }
  if(met.valid && met.delay<=target){
    out.solved=true;out.netlist=built.serialize();out.area=met.area;
    out.delay=met.delay;out.reason="bounded_support_shannon";
  }else out.reason="fallback_delay_infeasible";
  return out;
}
} // namespace r821
