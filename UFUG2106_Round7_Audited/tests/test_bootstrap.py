#!/usr/bin/env python3
"""Smoke-test bootstrap anchors and compile the result using synthetic upstream.

This does not replace compiling the actual frozen Round 5.1 source on WSL.
"""
from __future__ import annotations
import subprocess, tempfile, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bootstrap_round7 import patch, MERGE_START, GREEDY_START

ORIGINAL_MERGE = r'''   vector<R5Cube> prime;
   while(!cur.empty()){
    vector<char> used(cur.size());vector<R5Cube> nxt;
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
   }'''

ORIGINAL_COVER = r'''   vector<char> uncovered(Q,0);int remaining=0;
   for(int i=0;i<Q;i++)if(tt[i]==goal){uncovered[i]=1;remaining++;}
   while(remaining){
    double best=-1;int which=-1;
    for(int t=0;t<(int)prime.size();t++){
      int gains=0;
      for(int i=0;i<Q;i++)if(uncovered[i] && (i&prime[t].mask)==prime[t].val)gains++;
      if(!gains)continue;
      int cost=max(1,__builtin_popcount((unsigned)prime[t].mask));
      double score=double(gains)/(0.4+cost);
      if(score>best){best=score;which=t;}
    }
    if(which<0)throw runtime_error("cover failed");
    auto q=prime[which];plan.chosen.push_back(q);
    for(int i=0;i<Q;i++)if(uncovered[i] && (i&q.mask)==q.val){uncovered[i]=0;remaining--;}
   }'''

HEAD = r'''#include <bits/stdc++.h>
using namespace std;
struct R5Cube{int val,mask;};
struct R5CoverPlan{int kind=-1; vector<int> support;vector<R5Cube> chosen;};
struct CachedTruth{int n,m;vector<unsigned char>T;};
const std::vector<std::array<R5CoverPlan,2>>& shared_covers(const CachedTruth &data){
 static std::vector<std::array<R5CoverPlan,2>> cache;
 static const CachedTruth* last_data=nullptr;
 static const unsigned char* last_table=nullptr;
 if(last_data==&data && last_table==data.T.data())return cache;
 last_data=&data;last_table=data.T.data();
 cache.assign(data.m,{});
 if(data.n>13)return cache;
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
'''
MID = r'''
   sort(prime.begin(),prime.end(),[](R5Cube a,R5Cube b){return tie(a.mask,a.val)<tie(b.mask,b.val);});
   prime.erase(unique(prime.begin(),prime.end(),[](R5Cube a,R5Cube b){return a.mask==b.mask&&a.val==b.val;}),prime.end());
'''
TAIL = r'''
  }
 }
 return cache;
}
string run_synth(int){return "";}
int main(){
 CachedTruth d{4,1,{0,1,0,1,0,0,1,0,0,1,1,0,0,0,1,1}};
 const auto&p=shared_covers(d);
 return p[0][1].chosen.empty()?1:0;
}
'''


def main():
    source=HEAD+ORIGINAL_MERGE+MID+ORIGINAL_COVER+TAIL
    assert source.count(MERGE_START)==1
    assert source.count(GREEDY_START)==1
    modified=patch(source)
    assert 'R7_STAGE stage=covers' in modified
    assert 'r7_legacy_merge' in modified
    assert 'r7_legacy_cover' in modified
    with tempfile.TemporaryDirectory(prefix='r7_bootstrap_') as t:
        p=Path(t)
        (p/'smoke.cpp').write_text(modified,encoding='utf8')
        subprocess.run(['g++','-O2','-std=c++17',str(p/'smoke.cpp'),'-o',str(p/'smoke')],check=True)
        subprocess.run([str(p/'smoke')],check=True)
    print('PASS bootstrap patch anchors and generated C++ compilation')

if __name__=='__main__':main()
