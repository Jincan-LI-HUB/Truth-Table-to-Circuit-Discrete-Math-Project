#!/usr/bin/env python3
"""Compile the exact Round-7 kernel substitutions and verify A/B identity.

Extracts replacement code from bootstrap_round7.py, so the executable tests
precisely the C++ snippets installed into the synthesized solver.
"""
from __future__ import annotations
import subprocess
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bootstrap_round7 import MERGE_REPLACEMENT, GREEDY_REPLACEMENT

HEAD = r'''
#include <bits/stdc++.h>
using namespace std;
struct R5Cube {int val,mask;};
struct R5CoverPlan {int kind=-1; vector<int> support; vector<R5Cube> chosen;};
vector<R5Cube> calc(const vector<uint8_t>& tt, int k, int goal,
                    bool r7_legacy_merge, bool r7_legacy_cover){
 const int Q=1<<k;
 unsigned long long r7_merge_probes=0,r7_cover_probes=0,r7_merge_rounds=0;
 double r7_merge_ms=0.0,r7_cover_ms=0.0;
 R5CoverPlan plan;
 vector<R5Cube> cur;
 for(int i=0;i<Q;i++)if(tt[i]==goal)cur.push_back({i,Q-1});
 if(cur.empty()||(int)cur.size()==Q)return {};
'''
MID = r'''
 sort(prime.begin(),prime.end(),[](R5Cube a,R5Cube b){return tie(a.mask,a.val)<tie(b.mask,b.val);});
 prime.erase(unique(prime.begin(),prime.end(),[](R5Cube a,R5Cube b){return a.mask==b.mask&&a.val==b.val;}),prime.end());
'''
TAIL = r'''
 return plan.chosen;
}
static bool equal(const vector<R5Cube> &a,const vector<R5Cube>&b){
 if(a.size()!=b.size())return false;
 for(size_t i=0;i<a.size();i++)
  if(a[i].val!=b[i].val||a[i].mask!=b[i].mask)return false;
 return true;
}
int main(){
 std::mt19937 rng(0x71104);
 int checks=0;
 for(int k=1;k<=9;k++){
  int iterations=k<=6?200:k==7?90:k==8?30:12;
  for(int z=0;z<iterations;z++){
   int Q=1<<k;
   vector<uint8_t> tt(Q);
   int threshold=(z%9+1)*10;
   for(int i=0;i<Q;i++)tt[i]=(int(rng()%100))<threshold;
   if(z==0)fill(tt.begin(),tt.end(),0);
   if(z==1)fill(tt.begin(),tt.end(),1);
   for(int goal=0;goal<2;goal++){
    auto expected=calc(tt,k,goal,true,true);
    for(int flags=0;flags<4;flags++){
     auto actual=calc(tt,k,goal,(flags&1)!=0,(flags&2)!=0);
     if(!equal(expected,actual)){
      cerr<<"MISMATCH k="<<k<<" iter="<<z<<" goal="<<goal<<" flags="<<flags<<"\n";
      return 1;
     }
     ++checks;
    }
   }
  }
 }
 cout<<"PASS exact_cover_ablation: "<<checks<<" independent comparisons\n";
}
'''


def main():
    code = HEAD + MERGE_REPLACEMENT + MID + GREEDY_REPLACEMENT + TAIL
    with tempfile.TemporaryDirectory(prefix='round7_kernel_') as t:
        path = Path(t)
        (path / 'verify.cpp').write_text(code, encoding='utf-8')
        subprocess.run(['g++','-O2','-std=c++17','-Wall','-Wextra',
                        str(path/'verify.cpp'),'-o',str(path/'verify')],check=True)
        subprocess.run([str(path/'verify')],check=True,timeout=150)


if __name__=='__main__':
    main()
