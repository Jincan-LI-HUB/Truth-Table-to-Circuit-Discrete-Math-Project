#include <bits/stdc++.h>
#include "polarity_mapper.hpp"
using namespace std;
struct R {long long area;int delay;};
R cost(const string&s,int n,int aa,int da,int ao,int dor,int an,int dn){
 vector<int> at(n+1);long long A=0;istringstream in(s);string line;
 while(getline(in,line)){
  istringstream ss(line);string id,typ; if(!(ss>>id>>typ))break;
  if(typ=="NOT"||typ=="AND2"||typ=="OR2"){
   int a,b=0;ss>>a;if(typ!="NOT")ss>>b;
   if(typ=="NOT"){A+=an;at.push_back(at[a]+dn);}
   else if(typ=="AND2"){A+=aa;at.push_back(max(at[a],at[b])+da);}
   else{A+=ao;at.push_back(max(at[a],at[b])+dor);}
  }else{
    int mx=at[stoi(id)];if(!typ.empty())mx=max(mx,at[stoi(typ)]);int k;while(ss>>k)mx=max(mx,at[k]);return {A,mx};
  }
 }
 return {A,0};
}
int main(int argc,char**argv){
 if(argc<4)return 2;
 ifstream f(argv[1]);int n,m;f>>n>>m;string x;for(int i=0;i<(1<<n);i++)f>>x;
 int aa,da,ao,dor,an,dn,t;f>>aa>>da>>ao>>dor>>an>>dn>>t;
 ifstream fi(argv[2]);string old((istreambuf_iterator<char>(fi)),{});
 round4_phase::Engine e(old,n,m,aa,da,ao,dor,an,dn,t);
 if(!e.valid){cerr<<"invalid netlist parser\n";return 3;}
 auto original=cost(old,n,aa,da,ao,dor,an,dn);long long best_area=original.area;
 string best=old;int bestdelay=original.delay;int which=0;
 int trials=argc>4?stoi(argv[4]):6;
 for(int k=0;k<trials;k++){
   fill(e.phase.begin(),e.phase.end(),0);
   if(k==1 || k==4 || k==5)for(int v=n+1;v<int(e.graph.size());v++)e.phase[v]=1;
   if(k==2 || k==3 || k==5)for(int v=n+1;v<int(e.graph.size());v++)e.phase[v]=e.graph[v].op==0?(aa>ao):(ao>aa);
   if(k>0)e.improve(k==3||k==4?12:4,k==3||k==5);
   string cand=e.construct();auto c=cost(cand,n,aa,da,ao,dor,an,dn);
   if(c.delay<=t && (c.area<best_area || (c.area==best_area && c.delay<bestdelay))){best_area=c.area;bestdelay=c.delay;best=cand;which=k;}
 }
 ofstream o(argv[3]);o<<best;
 cerr<<"old="<<original.area<<" new="<<best_area<<" delay="<<bestdelay<<" candidate="<<which<<" nodes="<<e.graph.size()-n-1<<'\n';
}
