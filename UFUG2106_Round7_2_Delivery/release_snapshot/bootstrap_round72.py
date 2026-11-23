#!/usr/bin/env python3
"""Round 7.2 reproducible source generator.

Chain: frozen Round5.1 git blob -> exact Round7 kernel patch ->
Round7.1 guarded dispatch -> Round7.2 cheap-first bounded legacy candidate.
This generator intentionally requires the verified frozen source in the user's
existing Final Project directory and never overwrites old deliverables.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
UPSTREAM=HERE.parent/'UFUG2106_Round5.1_Delivery'/'src'

def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE/f'{name}.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def once(s,old,new,label):
    if s.count(old)!=1:
        raise ValueError(f'R7.2 patch [{label}]: expected 1 exact source anchor, got {s.count(old)}')
    return s.replace(old,new,1)

def patch72(source):
    s=source
    # The legacy synthesizer has no cancellation protocol. Instrument the
    # expensive loops, with the default deadline disabled for R7.1 controls.
    s=once(s,
      '''string run_synth(const string &input,const Opt &opt){
 ifstream in(input);ostringstream out;if(!in)return {};''',
      '''string run_synth(const string &input,const Opt &opt,
  chrono::steady_clock::time_point deadline=chrono::steady_clock::time_point::max()){
 uint64_t r72_checks=0;
 auto r72_checkpoint=[&](){
  if(deadline!=chrono::steady_clock::time_point::max() &&
     ((++r72_checks & 127ULL)==0) && chrono::steady_clock::now()>=deadline)
      throw CandidateTimeout{};
 };
 ifstream in(input);ostringstream out;if(!in)return {};''',
      'legacy optional checkpoint signature')
    s=once(s,
      '''for(size_t i=0;i<N;i++){in>>bits; if((int)bits.size()!=m)return {};for(int j=0;j<m;j++)T[i*m+j]=bits[j]-'0';}''',
      '''for(size_t i=0;i<N;i++){r72_checkpoint();in>>bits; if((int)bits.size()!=m)return {};for(int j=0;j<m;j++)T[i*m+j]=bits[j]-'0';}''',
      'legacy parse checkpoint')
    s=once(s,
      '''vector<size_t> orig(N);for(size_t z=1;z<N;z++){int bit=__builtin_ctzll(z);orig[z]=orig[z&(z-1)]|(1ull<<(n-1-perm[n-1-bit]));}''',
      '''vector<size_t> orig(N);for(size_t z=1;z<N;z++){r72_checkpoint();int bit=__builtin_ctzll(z);orig[z]=orig[z&(z-1)]|(1ull<<(n-1-perm[n-1-bit]));}''',
      'legacy variable order checkpoint')
    s=once(s,
      '''   for(size_t k=0;k<count/2;k++){
    int lo=cur[2*k],hi=cur[2*k+1];''',
      '''   for(size_t k=0;k<count/2;k++){
    r72_checkpoint();
    int lo=cur[2*k],hi=cur[2*k+1];''',
      'legacy BDD checkpoint')
    s=once(s,
      ''' auto mk=[&](int t,int a,int b)->int {if(t!=2&&a>b)swap(a,b); GKey k{t,a,b};''',
      ''' auto mk=[&](int t,int a,int b)->int {r72_checkpoint();if(t!=2&&a>b)swap(a,b); GKey k{t,a,b};''',
      'legacy gate emission checkpoint')
    s=once(s,
      ''' function<int(int)> build=[&](int id)->int {if(done[id]>=0)return done[id];auto node=nodes[id];''',
      ''' function<int(int)> build=[&](int id)->int {r72_checkpoint();if(done[id]>=0)return done[id];auto node=nodes[id];''',
      'legacy ROBDD mapping checkpoint')
    s=once(s,
      ''' const bool r71_skip_legacy=(r71_guard && limit>0 && limit<=250 &&
    b.valid && b.delay<=target);
 if(r71_trace && r71_skip_legacy)''',
      ''' // R7.2 policy: guard reproduces R7.1; shortlist tries exactly one
 // cheap legacy candidate with cubemode=0 and a cooperative deadline.
 const char* r72_env=std::getenv("UFUG_R72_POLICY");
 const std::string r72_policy=r72_env?r72_env:"shortlist";
 if(r72_policy!="shortlist" && r72_policy!="guard" &&
    r72_policy!="shortlist_nocancel"){
   std::cerr<<"R72_ERROR invalid policy="<<r72_policy<<"\\n";
   return 8;
 }
 const bool r72_short_feasible=(r71_guard && limit>0 && limit<=250 &&
    b.valid && b.delay<=target);
 const bool r72_use_shortlist=(r72_policy=="shortlist" ||
    r72_policy=="shortlist_nocancel") && r72_short_feasible &&
    n<=10 && limit>=100;
 const bool r72_trace=r71_trace;
 if(r72_use_shortlist){
   const double elapsed=r71_elapsed();
   // The dispatch admission test is intentionally stricter than the R7.1
   // 72% threshold. We need headroom for the original phase postprocessor
   // and for evaluator overhead after circuit construction.
   const double admission=0.35*double(limit);
   const double deadline_fraction=0.60;
   if(elapsed<admission){
     const auto candidate_started=Clock::now();
     const auto deadline=start+std::chrono::microseconds(
          static_cast<long long>(deadline_fraction*double(limit)*1000.0));
     try{
       legacy::Opt cheap={"influence-desc",true,false,true,0,0};
       const auto cap=(r72_policy=="shortlist_nocancel")?
          Clock::time_point::max():deadline;
       std::string trial=legacy::run_synth(argv[1],cheap,cap);
       const double search_ms=std::chrono::duration<double,std::milli>(
          Clock::now()-candidate_started).count();
       if(!trial.empty() && r71_elapsed()<0.65*double(limit)){
         r51::Costs cost{aa,da,ao,dor,an,dn};
         r51::Graph typed=r51::parse(trial,n,m);
         auto tz=typed.metric(cost);
         Stats z{tz.valid,tz.area,tz.delay};
         if(z.valid && z.delay<=target){
           r51::Graph ar=r51::area_recover(typed,cost,target,0);
           auto taz=ar.metric(cost);
           Stats az{taz.valid,taz.area,taz.delay};
           auto rank=[&](Stats x){return make_tuple(max(0,x.delay-target),
             x.delay<=target?x.area:0LL,x.delay,x.area);};
           if(az.valid && rank(az)<rank(z)){typed=std::move(ar);z=az;}
         }
         auto rank=[&](Stats x){return make_tuple(max(0,x.delay-target),
           x.delay<=target?x.area:0LL,x.delay,x.area);};
         const bool improved=z.valid && (!b.valid || rank(z)<rank(b));
         if(improved){best=typed.serialize();b=z;chosen=200+completed;}
         ++completed;
         if(r72_trace)std::cerr<<"R72_TRACE event=shortlist result=completed"
           <<" improved="<<improved<<" candidate_area="<<z.area
           <<" candidate_delay="<<z.delay
           <<" search_ms="<<search_ms
           <<" total_ms="<<r71_elapsed()
           <<" incumbent_area="<<b.area<<"\\n";
       }else if(r72_trace){
         std::cerr<<"R72_TRACE event=shortlist result=insufficient_postprocess_budget"
           <<" search_ms="<<search_ms<<" elapsed_ms="<<r71_elapsed()<<"\\n";
       }
     }catch(const CandidateTimeout&){
       if(r72_trace)std::cerr<<"R72_TRACE event=shortlist result=checkpoint_timeout"
          <<" elapsed_ms="<<r71_elapsed()<<"\\n";
     }
   }else if(r72_trace){
     std::cerr<<"R72_TRACE event=shortlist result=admission_denied"
       <<" elapsed_ms="<<elapsed<<"\\n";
   }
 }
 const bool r71_skip_legacy=r72_short_feasible;
 if(r71_trace && r71_skip_legacy)''',
      'one bounded cheap-first legacy candidate before guard')
    # Explicit full-search ablation should still run the R7.1 off path,
    # without being mislabelled as a guard-vs-shortlist comparison.
    s=once(s,
      ''' const bool r72_use_shortlist=(r72_policy=="shortlist" ||''',
      ''' const bool r72_use_shortlist=(r72_policy=="shortlist" ||''',
      'verify shortlist anchor') if False else s
    return s

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path,default=UPSTREAM)
    args=ap.parse_args();src=args.source_root.resolve()
    r7=load('bootstrap_round7');r71=load('bootstrap_round71')
    raw=(src/'synth_round51.cpp').read_bytes().replace(b'\r\n',b'\n')
    blob=r7.git_blob_sha(raw)
    if blob!=r7.UPSTREAM_GIT_BLOB:
        raise SystemExit(f'Frozen R5.1 git blob mismatch: expected {r7.UPSTREAM_GIT_BLOB}; got {blob}')
    s=patch72(r71.patch71(r7.patch(raw.decode('utf-8'))))
    out=HERE/'src';out.mkdir(exist_ok=True)
    p=out/'synth_round72.cpp';p.write_text(s,encoding='utf-8')
    hashes={'synth_round72.cpp':hashlib.sha256(p.read_bytes()).hexdigest()}
    for h in ('typed_netgraph.hpp','polarity_mapper.hpp','algebraic_mapper.hpp'):
        shutil.copy2(src/h,out/h);hashes[h]=hashlib.sha256((out/h).read_bytes()).hexdigest()
    manifest={'milestone':'7.2','frozen_upstream_git_blob':blob,
       'bootstrap_chain':['Round5.1','Round7','Round7.1','Round7.2'],
       'source_sha256':hashes}
    (HERE/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('Materialized:',p);print('Round 7.2 source sha256:',hashes['synth_round72.cpp'])
if __name__=='__main__':main()
