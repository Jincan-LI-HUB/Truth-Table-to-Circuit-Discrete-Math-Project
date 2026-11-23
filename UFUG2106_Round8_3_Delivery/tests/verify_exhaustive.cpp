// Independent exhaustive bit-parallel equivalence tester for n<=20.
// This parses the *original* truth table, compares ALL 2^n assignments.
#include <bits/stdc++.h>
#include "../src/typed_netgraph.hpp"
using namespace std;
int main(int argc,char**argv){
 if(argc!=3){cerr<<"usage: verify_exhaustive CASE NETLIST\n";return 2;}
 ifstream inp(argv[1]);int n,m;
 if(!(inp>>n>>m) || n<1 || n>20 || m<1)return 3;
 size_t N=1ull<<n,B=(N+63)/64;
 vector<uint64_t> expected(B*size_t(m));
 string bits;for(size_t row=0;row<N;row++){
  if(!(inp>>bits)||bits.size()!=size_t(m))return 4;
  for(int j=0;j<m;j++)if(bits[j]=='1')expected[size_t(j)*B+(row>>6)]|=1ull<<(row&63);
 }
 int aa,da,ao,dor,an,dn,target;
 if(!(inp>>aa>>da>>ao>>dor>>an>>dn>>target))return 5;
 r51::Costs c{aa,da,ao,dor,an,dn};
 ifstream fin(argv[2]);stringstream buf;buf<<fin.rdbuf();auto graph=r51::parse(buf.str(),n,m);
 auto metric=graph.metric(c);if(!metric.valid)return 6;
 vector<uint64_t> signals(graph.nodes.size(),0);
 for(size_t block=0;block<B;block++){
  for(int j=0;j<n;j++){
   uint64_t v=0;for(int k=0;k<64;k++){
    size_t row=block*64+k;
    if(row<N && ((row>>(n-j-1))&1))v|=1ull<<k;
   }
   signals[j+1]=v;
  }
  for(size_t id=n+1;id<graph.nodes.size();id++){
   auto g=graph.nodes[id];uint64_t a=signals[g.a];
   signals[id]=g.op==2?~a:g.op==0?(a&signals[g.b]):(a|signals[g.b]);
  }
  for(int j=0;j<m;j++){
   uint64_t wanted=expected[size_t(j)*B+block];
   uint64_t actual=signals[graph.outputs[j]];
   if(block==B-1 && (N&63))actual&=(1ull<<(N&63))-1;
   if(actual!=wanted){cerr<<"FAIL output="<<j<<" block="<<block<<"\n";return 7;}
  }
 }
 cout<<"PASS exact_assignments="<<N<<" area="<<metric.area<<" delay="<<metric.delay<<" target="<<target<<"\n";
 return 0;
}
