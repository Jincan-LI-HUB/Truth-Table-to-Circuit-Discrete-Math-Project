#!/usr/bin/env python3
"""Measure ONLY the symbolic cover kernel, not end-to-end synthesis."""
from __future__ import annotations
import sys
import subprocess
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_exact_cover import HEAD, MID, TAIL, MERGE_REPLACEMENT, GREEDY_REPLACEMENT

BENCH_MAIN = r'''
int main(int argc,char**argv){
 if(argc<2)return 2;
 ifstream in(argv[1]);int n,m;in>>n>>m;
 if(n>9){cerr<<"Benchmark expects n<=9\n";return 3;}
 int Q=1<<n;
 vector<vector<uint8_t>> tts(m,vector<uint8_t>(Q));
 string bits;
 for(int i=0;i<Q;i++){
  in>>bits;
  if((int)bits.size()!=m)return 4;
  for(int j=0;j<m;j++)tts[j][i]=bits[j]-'0';
 }
 auto run=[&](bool old){
  long long guard=0;
  auto started=chrono::steady_clock::now();
  for(int iter=0;iter<10;iter++){
   for(auto &tt:tts){
    for(int g=0;g<2;g++){
     auto v=calc(tt,n,g,old,old);
     guard+=v.size();
     if(iter==0){
      auto other=calc(tt,n,g,!old,!old);
      if(!equal(v,other)){cerr<<"Mismatch"<<"\n";exit(1);}
     }
    }
   }
  }
  double ms=chrono::duration<double,milli>(chrono::steady_clock::now()-started).count()/10;
  cout<<(old?"legacy":"optimized")<<" symbolic covers (mean of 10): "<<ms<<" ms"
      <<" guard="<<guard<<"\n";
 };
 run(true);
 run(false);
 return 0;
}
'''

def main():
    if len(sys.argv)!=2:raise SystemExit('Usage: python3 tests/bench_cover_kernel.py PATH_TO_CASE_016')
    source = HEAD + MERGE_REPLACEMENT + MID + GREEDY_REPLACEMENT + TAIL.split('int main(){',1)[0] + BENCH_MAIN
    with tempfile.TemporaryDirectory(prefix='r7_cover_bench_') as t:
        p=Path(t)
        (p/'bench.cpp').write_text(source)
        subprocess.run(['g++','-O2','-std=c++17',str(p/'bench.cpp'),'-o',str(p/'bench')],check=True)
        subprocess.run([str(p/'bench'),sys.argv[1]],check=True,timeout=120)

if __name__=='__main__':main()
