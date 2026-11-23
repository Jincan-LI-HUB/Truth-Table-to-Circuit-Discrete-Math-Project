#!/usr/bin/env python3
"""Reproducible R8.2 source generation; frozen R8.1 SHA checked."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
PARENT=P.parent/'UFUG2106_Round8_1_Delivery/src/synth_round81.cpp'
PARENT_SHA='a12ed21f9d48862be0771d0d15801c81bb280bbff908d8d90932cf43a53d4181'
BLOCK=' // R8.2 independent full-graph candidate selection, no testcase-specific conditions.\n // R8.1 is disabled for this binary unless R82 policy is explicitly off.\n const char* r82raw=std::getenv("UFUG_R82_POLICY");\n const std::string r82policy=r82raw?r82raw:"fast_adp";\n const bool r82active=r82policy!="off";\n if(r82policy!="off" && r82policy!="fast_area" && r82policy!="fast_slack" &&\n    r82policy!="fast_adp" && r82policy!="dual_area" && r82policy!="dual_slack" &&\n    r82policy!="dual_adp" && r82policy!="dual_strict"){\n    std::cerr<<"R82_ERROR unknown policy="<<r82policy<<"\\n";return 12;\n }\n if(r82active && limit>=1000 && b.valid && b.delay<=target){\n    double sofar=std::chrono::duration<double,std::milli>(Clock::now()-start).count();\n    // Preserve time for graph serialization and evaluator overhead.\n    if(sofar<0.70*double(limit)){\n      r51::Costs c{aa,da,ao,dor,an,dn};\n      r51::Graph base=r51::parse(best,n,m);\n      auto bm=base.metric(c);\n      if(bm.valid){\n       std::string objective="area";\n       if(r82policy.find("adp")!=std::string::npos)objective="adp";\n       else if(r82policy.find("slack")!=std::string::npos)objective="slack";\n       else if(r82policy.find("strict")!=std::string::npos)objective="strict";\n       r82::Point original{"baseline",bm.area,bm.delay};\n       r82::Point selected=original;\n       std::vector<r82::Point>archive{original};\n       const bool dual=r82policy.substr(0,4)=="dual";\n       const std::vector<std::string>modes=dual?std::vector<std::string>{"shannon","sop"}:\n                                               std::vector<std::string>{"shannon"};\n       int roots=1500;\n       if(const char* e=std::getenv("UFUG_R82_ROOT_CAP")){\n          try{roots=std::clamp(std::stoi(e),100,4000);}catch(...){roots=1500;}\n       }\n       const double frac=0.10;\n       const double search_budget=std::min(300.0,frac*double(limit));\n       const auto tbegin=Clock::now();\n       for(const auto&mode:modes){\n         double used=std::chrono::duration<double,std::milli>(Clock::now()-tbegin).count();\n         double wall=std::chrono::duration<double,std::milli>(Clock::now()-start).count();\n         if(used>=search_budget ||wall>=0.82*double(limit))break;\n         double remaining=std::min(search_budget-used,0.80*double(limit)-wall);\n         if(remaining<1.0)break;\n         const char* rawsample=std::getenv("UFUG_R82_SAMPLING");\n         std::string sampling=rawsample?rawsample:"priority";\n         if(sampling!="priority"&&sampling!="stride")sampling="priority";\n         auto result=r82cut::rewrite(base,c,target,mode,std::min(140.0,remaining),roots,sampling);\n         auto met=result.graph.metric(c);\n         if(!met.valid||met.delay>target)continue;\n         r82::Point p{mode,met.area,met.delay};archive.push_back(p);\n         const bool admissible=r82::eligible(original,p,target,objective);\n         if(admissible && (selected.mode=="baseline"||r82::better(p,selected,objective))){\n           best=result.graph.serialize();b.area=met.area;b.delay=met.delay;selected=p;\n         }\n         if(auto flag=std::getenv("UFUG_R82_PROFILE"))if(*flag==\'1\'){\n           std::cerr<<"R82_STAGE policy="<<r82policy<<" mode="<<mode<<" roots="<<roots\n             <<" visited="<<result.stats.visited_roots<<" cuts="<<result.stats.cuts\n             <<" area="<<met.area<<" delay="<<met.delay\n             <<" base_area="<<bm.area<<" base_delay="<<bm.delay\n             <<" eligible="<<admissible<<" selected="<<(selected.mode==mode)\n             <<" budget_hit="<<result.stats.budget_hit<<" ms="<<result.stats.elapsed_ms<<"\\n";\n         }\n       }\n       if(auto flag=std::getenv("UFUG_R82_PROFILE"))if(*flag==\'1\'){\n         auto pf=r82::pareto(archive);\n         for(const auto&p:pf)std::cerr<<"R82_PARETO mode="<<p.mode<<" area="<<p.area<<" delay="<<p.delay<<"\\n";\n         std::cerr<<"R82_FINAL policy="<<r82policy<<" chosen="<<selected.mode\n             <<" area="<<b.area<<" delay="<<b.delay<<"\\n";\n       }\n      }\n    }\n }'
def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError('Patch anchor drift: '+repr(a[:70]))
    return s.replace(a,b,1)
def main():
    raw=PARENT.read_bytes().replace(b'\r\n',b'\n')
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=PARENT_SHA:raise RuntimeError('Frozen R8.1 source SHA mismatch: '+sha)
    s=raw.decode('utf-8')
    s=once(s,'#include "r81_cut.hpp"','#include "r81_cut.hpp"\n#include "r82_archive.hpp"\n#include "r82_cut.hpp"')
    # R8.2 defaults to the frozen R7.2-derived incumbent without R8.0 preprocessing;
    # explicit UFUG_R8_POLICY still overrides this for a controlled sequence study.
    s=once(s,' std::string r8policy=r8env?r8env:"iterate";',
        ' std::string r8policy=r8env?r8env:((!std::getenv("UFUG_R82_POLICY") || std::string(std::getenv("UFUG_R82_POLICY"))!="off")?"off":"iterate");')
    s=once(s,' const std::string r81policy=r81raw?r81raw:"branch";', 
        ' const std::string r81policy=(!std::getenv("UFUG_R82_POLICY") || std::string(std::getenv("UFUG_R82_POLICY"))!="off")?"off":(r81raw?r81raw:"branch");')
    a=' ofstream out(argv[2]);out<<best;'
    s=once(s,a,BLOCK+'\n'+a)
    dest=P/'src/synth_round82.cpp';dest.write_text(s)
    manifest={'frozen_round81_sha256':PARENT_SHA,'round82_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
    for f in (P/'src').glob('*.hpp'):manifest[f.name]=hashlib.sha256(f.read_bytes()).hexdigest()
    (P/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Generated:',dest,'sha256:',manifest['round82_sha256'],flush=True)
if __name__=='__main__':main()
