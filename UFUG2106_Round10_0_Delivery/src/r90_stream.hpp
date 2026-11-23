#pragma once
// Round 9.0 streaming short-limit semantic bypass.
// Deliberately restricted to n>=18 and 0<runtime_limit<=250 (tested in main).
// Caller still consumes all 2^n truth groups: this is not a partial-input guess.
// Only exact literals/constant or GF(2) affine functions are accepted.
// All normal-budget candidate search is unaffected.
#include <algorithm>
#include <cstdint>
#include <queue>
#include <string>
#include <vector>

namespace r90 {
struct StreamCandidate {
 bool solved=false;
 std::string netlist,reason;
 long long area=-1;
 int delay=-1;
};
struct StreamProbe {
 int n,m;
 std::vector<uint64_t> literal;
 std::vector<uint32_t> affine_mask;
 std::vector<uint8_t> affine_ok, constant;
 uint64_t even=0,valid=0;
 bool any_lit=true,any_affine=true;
 explicit StreamProbe(int nn,int mm):n(nn),m(mm),literal(size_t(mm),0),
       affine_mask(size_t(mm),0),affine_ok(size_t(mm),1),constant(size_t(mm),0){
   for(int v=0;v<n;++v)even|=1ULL<<(2+2*v);
   valid=3ULL|even|(even<<1);
   std::fill(literal.begin(),literal.end(),valid);
 }
 void observe(uint32_t row,const std::string&bits){
   if(!any_lit&&!any_affine)return;
   if(int(bits.size())!=m){
     any_lit=any_affine=false;std::fill(literal.begin(),literal.end(),0);
     std::fill(affine_ok.begin(),affine_ok.end(),0);return;
   }
   if(row==0){
     for(int j=0;j<m;++j)constant[j]=uint8_t(bits[j]=='1');
   }
   const bool power=(row!=0 && (row&(row-1))==0);
   uint64_t expected_one=0,expected_zero=0;
   if(any_lit){
     uint64_t present=0;
     for(int v=0;v<n;++v){
       present|=(uint64_t((row>>(n-1-v))&1U)<<(2+2*v));
     }
     expected_one=2ULL|present|((even^present)<<1);
     expected_zero=1ULL|(even^present)|(present<<1);
   }
   bool lit_any=false,aff_any=false;
   for(int j=0;j<m;++j){
     const uint8_t y=uint8_t(bits[j]=='1');
     if(literal[j])literal[j]&=y?expected_one:expected_zero;
     lit_any|=literal[j]!=0;
     if(affine_ok[j]){
       if(power){if(y!=constant[j])affine_mask[j]|=row;}
       else if(row && ((uint8_t(__builtin_parity(affine_mask[j]&row))^constant[j])!=y)){
         affine_ok[j]=0;
       }
     }
     aff_any|=bool(affine_ok[j]);
   }
   any_lit=lit_any;any_affine=aff_any;
 }
 StreamCandidate make_candidate(const r51::Costs&c,int target)const{
   StreamCandidate out;
   const bool simple=std::all_of(literal.begin(),literal.end(),[](uint64_t z){return z!=0;});
   const bool affine=std::all_of(affine_ok.begin(),affine_ok.end(),[](uint8_t z){return z!=0;});
   if(!simple&&!affine)return out;
   r51::Graph empty(n,m);r51::Builder b(empty);
   auto neg=[&](int x){if(x>n && b.graph.nodes[x].op==2)return b.graph.nodes[x].a;
      return b.add(2,x,0,c);};
   auto bxor=[&](int x,int y){
     // x xor y = (x OR y) AND NOT(x AND y), using only allowed gates.
     int o=b.add(1,x,y,c),a=b.add(0,x,y,c);
     return b.add(0,o,neg(a),c);
   };
   std::vector<int> outputs;outputs.reserve(m);
   if(simple){
     for(uint64_t bits:literal){
       const int which=__builtin_ctzll(bits);
       if(which==0)outputs.push_back(0);
       else if(which==1)outputs.push_back(neg(0));
       else if((which&1)==0)outputs.push_back(1+(which-2)/2);
       else outputs.push_back(neg(1+(which-3)/2));
     }
     out.reason="stream_literals";
   }else{
     for(int j=0;j<m;++j){
       std::priority_queue<std::pair<int,int>,std::vector<std::pair<int,int>>,
          std::greater<std::pair<int,int>>> pq;
       for(int v=0;v<n;++v){
         if((affine_mask[j]>>(n-1-v))&1U)pq.push({0,v+1});
       }
       int root=0;
       while(pq.size()>1){
         int a=pq.top().second;pq.pop();int z=pq.top().second;pq.pop();
         int r=bxor(a,z);pq.push({b.ready[r],r});
       }
       if(!pq.empty())root=pq.top().second;
       if(constant[j])root=neg(root);
       outputs.push_back(root);
     }
     out.reason="stream_affine";
   }
   auto graph=b.finish(outputs);
   auto metric=graph.metric(c);
   if(metric.valid && metric.delay<=target){
     out.solved=true;out.netlist=graph.serialize();out.area=metric.area;out.delay=metric.delay;
   }
   return out;
 }
};
} // namespace r90
