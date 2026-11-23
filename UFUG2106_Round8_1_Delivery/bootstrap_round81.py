#!/usr/bin/env python3
"""Deterministically derive Round8.1 from frozen Round8.0 source.
Does not modify existing rounds. Error on hash drift or duplicated anchors.
"""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
SRC=P.parent/'UFUG2106_Round8_Prototype/src/synth_round8.cpp'
EXPECTED='9ec7dc97161d3dc906dfad7960e0fc232b8e2cf0399908c6c4e99b756d8bacd8'
def patch_once(s,a,b,name):
 n=s.count(a)
 if n!=1:raise RuntimeError(f'Patch anchor {name} occurrence count {n}, expected 1')
 return s.replace(a,b,1)
def main():
 raw=SRC.read_bytes().replace(b'\r\n',b'\n');sha=hashlib.sha256(raw).hexdigest()
 if sha!=EXPECTED:raise RuntimeError('Round8.0 source SHA mismatch: '+sha+' expected '+EXPECTED)
 s=raw.decode('utf-8')
 s=patch_once(s,'#include "r8_structural.hpp"','#include "r8_structural.hpp"\n#include "r81_cut.hpp"','new header')
 anchor=' ofstream out(argv[2]);out<<best;'
 injection=r''' // Round 8.1: independent truth-table cut-resynthesis branches.
 // Parent output remains the incumbent; only exact whole-graph cost gains
 // satisfying declared timing can replace it. No case-specific rules.
 const char* r81raw=std::getenv("UFUG_R81_POLICY");
 const std::string r81policy=r81raw?r81raw:"branch";
 if(r81policy!="off" && r81policy!="sop" && r81policy!="shannon" &&
    r81policy!="all" && r81policy!="choices" && r81policy!="branch" &&
    r81policy!="branch_strict" && r81policy!="reverse"){
   std::cerr<<"R81_ERROR unknown policy "<<r81policy<<"\n";return 11;
 }
 if(r81policy!="off" && limit>=1000 && b.valid && b.delay<=target){
   const double consumed=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
   if(consumed<0.71*double(limit)){
     r51::Costs r81cost{aa,da,ao,dor,an,dn};
     const r51::Graph basegraph=r51::parse(best,n,m);
     const auto basemet=basegraph.metric(r81cost);
     if(basemet.valid){
       std::vector<std::string>branches;
       if(r81policy=="branch"||r81policy=="branch_strict"||r81policy=="reverse")
         branches={"sop","shannon","all"};
       else branches={r81policy};
       const bool strict=(r81policy=="branch_strict");
       const double total_ms=std::min(450.0,0.16*double(limit));
       const double each_ms=std::min(160.0,0.065*double(limit));
       const auto begin81=Clock::now();
       std::string chosenMode="base";
       for(const std::string& mode:branches){
         double spent=std::chrono::duration<double,std::milli>(Clock::now()-begin81).count();
         double elapsed=std::chrono::duration<double,std::milli>(Clock::now()-start).count();
         if(spent>=total_ms||elapsed>=0.82*double(limit))break;
         auto attempt=r81::rewrite(basegraph,r81cost,target,mode,
                    std::min(each_ms,std::max(1.0,total_ms-spent)),2500);
         auto met=attempt.graph.metric(r81cost);
         // Reverse-order ablation: cut first, then pattern rewriting.
         if(r81policy=="reverse" && met.valid && met.delay<=target){
           for(int pass=0;pass<2;++pass){
             if(std::chrono::duration<double,std::milli>(Clock::now()-begin81).count()>=total_ms)break;
             bool improved=false;
             for(const char* rmode:{"reuse","factor","combined_relaxed"}){
               auto a=r8::rewrite(attempt.graph,r81cost,rmode,target);
               auto z=a.graph.metric(r81cost);
               if(z.valid && z.delay<=target && z.area<met.area){
                  attempt.graph=std::move(a.graph);met=z;improved=true;
               }
             }
             if(!improved)break;
           }
         }
         bool accept=met.valid && met.delay<=target &&
                     (!strict||met.delay<=basemet.delay) &&
                     (met.area<b.area || (met.area==b.area&&met.delay<b.delay));
         if(accept){
           best=attempt.graph.serialize();b.area=met.area;b.delay=met.delay;
           chosenMode=mode;
         }
         if(auto p=std::getenv("UFUG_R81_PROFILE"))if(*p=='1'){
           std::cerr<<"R81_STAGE mode="<<mode<<" area="<<met.area
             <<" delay="<<met.delay<<" attempt_ms="<<attempt.stats.elapsed_ms
             <<" visited="<<attempt.stats.visited_roots<<" cuts="<<attempt.stats.cuts
             <<" sop="<<attempt.stats.sop_candidates
             <<" shannon="<<attempt.stats.shannon_candidates
             <<" selected="<<attempt.stats.selected
             <<" zero_gain="<<attempt.stats.zero_gain_choices
             <<" timing_reject="<<attempt.stats.timing_reject
             <<" budget_hit="<<attempt.stats.budget_hit
             <<" accepted="<<accept<<"\n";
         }
       }
       if(auto p=std::getenv("UFUG_R81_PROFILE"))if(*p=='1')
         std::cerr<<"R81_FINAL policy="<<r81policy<<" selected="<<chosenMode
                  <<" area="<<b.area<<" delay="<<b.delay<<"\n";
     }
   }
 }
 ofstream out(argv[2]);out<<best;'''
 s=patch_once(s,anchor,injection,'final incumbent integration')
 out=P/'src/synth_round81.cpp';out.write_text(s)
 digests={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (P/'src').glob('*') if x.is_file()}
 manifest={'round':'8.1','frozen_parent_sha256':EXPECTED,'files':digests}
 (P/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Generated:',out,'sha256:',digests[out.name])
if __name__=='__main__':main()
