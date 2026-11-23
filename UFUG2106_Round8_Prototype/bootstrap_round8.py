#!/usr/bin/env python3
"""Materialize an independent Round 8 research prototype from the frozen R7.2.
No modifications to any earlier round. No network access required.
"""
from pathlib import Path
import hashlib,json,shutil
H=Path(__file__).resolve().parent
SOURCE=H.parent/'UFUG2106_Round7_2_Delivery'/'src'
EXPECTED='d7c0dac7ddb173d8cd76f8ae0ebae9160856a1e0ab443e162584bdd2c15bff9e'
def replace_once(s,old,new,label):
    if s.count(old)!=1:raise RuntimeError(f'patch anchor {label}: {s.count(old)} occurrences')
    return s.replace(old,new,1)
def main():
    raw=(SOURCE/'synth_round72.cpp').read_bytes().replace(b'\r\n',b'\n')
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=EXPECTED:raise RuntimeError(f'Frozen R7.2 source SHA mismatch: {digest}, expected {EXPECTED}')
    s=raw.decode('utf-8')
    s=replace_once(s,'#include "typed_netgraph.hpp"','#include "typed_netgraph.hpp"\n#include "r8_structural.hpp"','include structural optimizer')
    marker=' ofstream out(argv[2]);out<<best;'
    injection=r''' // Round 8: independent structural alternatives, each rigorously checked on
 // the fully rebuilt live DAG. Baseline incumbent is preserved as fallback.
 const char* r8env=std::getenv("UFUG_R8_POLICY");
 std::string r8policy=r8env?r8env:"iterate";
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
 ofstream out(argv[2]);out<<best;'''
    s=replace_once(s,marker,injection,'whole-circuit structural acceptance')
    out=H/'src';out.mkdir(exist_ok=True)
    file=out/'synth_round8.cpp';file.write_text(s,encoding='utf-8')
    for x in ('typed_netgraph.hpp','polarity_mapper.hpp','algebraic_mapper.hpp'):
        shutil.copy2(SOURCE/x,out/x)
    files=list(out.glob('*.cpp'))+list(out.glob('*.hpp'))
    data={'prototype':'Round8.0','parent':'Frozen Round7.2','parent_sha256':EXPECTED,
          'files':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in files}}
    (H/'SOURCE_MANIFEST.json').write_text(json.dumps(data,indent=2)+'\n')
    print('Generated:',file,'SHA256',data['files']['synth_round8.cpp'])
if __name__=='__main__':main()
