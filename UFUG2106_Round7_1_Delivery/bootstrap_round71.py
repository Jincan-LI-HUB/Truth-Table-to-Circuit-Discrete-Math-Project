"""Round 7.1: materialize a reproducible standalone source snapshot.

The starting point is the reviewed frozen R5.1 git blob. The unchanged
Round 7 exact-cover patch is applied first, then the R7.1 policy patch.
No network or external code generator is required.
"""
from __future__ import annotations
import argparse, hashlib, json, importlib.util, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
UPSTREAM=HERE.parent/'UFUG2106_Round5.1_Delivery'/'src'

def load_round7():
    spec=importlib.util.spec_from_file_location('bootstrap_round7',HERE/'bootstrap_round7.py')
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def replace_one(s,needle,replacement,label):
    if s.count(needle)!=1:
        raise ValueError(f'{label}: expected one anchor, found {s.count(needle)}')
    return s.replace(needle,replacement,1)

def patch71(source):
    s=source
    s=replace_one(s,
      'int main(int argc,char**argv){\n if(argc!=3)return 2;',
      'int main(int argc,char**argv){\n using Clock=chrono::steady_clock;\n const auto r71_launch=Clock::now();\n if(argc!=3)return 2;',
      'start timing at process entry')
    s=replace_one(s,
      ' using Clock=chrono::steady_clock;\n auto start=Clock::now();',
      ''' auto start=r71_launch;
 // Optional ablation: UFUG_R71_POLICY=off restores the R7 portfolio.
 const char* r71_env=std::getenv("UFUG_R71_POLICY");
 const std::string r71_policy=r71_env?r71_env:"guard";
 const bool r71_guard=(r71_policy!="off");
 const bool r71_trace=[]{const char*p=std::getenv("UFUG_R71_TRACE");return p&&*p=='1';}();
 // A heuristic dispatch reserve, not a hard real-time guarantee.
 const double r71_search_cap=limit>0?
   (limit<=250?0.72*double(limit):0.75*double(limit)):
   std::numeric_limits<double>::infinity();
 auto r71_elapsed=[&](){return std::chrono::duration<double,std::milli>(Clock::now()-start).count();};
 if(r71_trace)std::cerr<<"R71_TRACE event=policy policy="<<r71_policy
    <<" limit_ms="<<limit<<" dispatch_cap_ms="<<r71_search_cap<<"\\n";''',
      'resource policy injection')
    s=replace_one(s,
       '''  if(i && limit>0){
   auto elapsed=chrono::duration<double,milli>(Clock::now()-start).count();
   if(elapsed>0.75*limit)break;
  }''',
       '''  if(i && limit>0){
   auto elapsed=r71_elapsed();
   const double dispatch=r71_guard?r71_search_cap:0.75*limit;
   if(elapsed>=dispatch){
     if(r71_trace)std::cerr<<"R71_TRACE event=primary_skip index="<<i
       <<" elapsed_ms="<<elapsed<<" cause=dispatch_budget\\n";
     break;
   }
  }''',
       'primary candidate dispatch guard')
    s=replace_one(s,
       '       net=run_synth(argv[1],variants[i]);',
       '''       if(r71_guard && i>0 && limit>0 && limit<=250){
         auto deadline=start+std::chrono::microseconds(
           static_cast<long long>(r71_search_cap*1000.0));
         net=run_synth(argv[1],variants[i],deadline);
       }else{
         net=run_synth(argv[1],variants[i]);
       }''',
       'secondary candidate cooperative timeout')
    s=replace_one(s,
       '''  if(!b.valid || rank(z)<rank(b)) {best=typed.serialize();b=z;chosen=i;}
 }
 // A distinct legacy representation''',
       '''  const bool improved=(!b.valid || rank(z)<rank(b));
  if(improved){best=typed.serialize();b=z;chosen=i;}
  if(r71_trace)std::cerr<<"R71_TRACE event=primary index="<<i
    <<" elapsed_ms="<<r71_elapsed()
    <<" candidate_ms="<<std::chrono::duration<double,std::milli>(Clock::now()-trial_started).count()
    <<" candidate_area="<<z.area<<" candidate_delay="<<z.delay
    <<" improved="<<(improved?1:0)<<" incumbent_area="<<b.area<<"\\n";
 }
 // A distinct legacy representation''',
       'candidate quality tracing')
    s=replace_one(s,
       ''' if((n<=16 && limit>=5000) || (n<=10 && limit>=100)){
   vector<legacy::Opt> legacyMethods={''',
       ''' const bool r71_skip_legacy=(r71_guard && limit>0 && limit<=250 &&
    b.valid && b.delay<=target);
 if(r71_trace && r71_skip_legacy)
   std::cerr<<"R71_TRACE event=legacy_skipped cause=short_budget_feasible_incumbent"
            <<" elapsed_ms="<<r71_elapsed()<<" area="<<b.area
            <<" delay="<<b.delay<<"\\n";
 if(!r71_skip_legacy && ((n<=16 && limit>=5000) || (n<=10 && limit>=100))){
   vector<legacy::Opt> legacyMethods={''',
       'short budget legacy guard')
    s=replace_one(s,
       '''      if(limit>0){
        double elapsed=chrono::duration<double,milli>(Clock::now()-start).count();
        if(elapsed>0.72*limit)break;
      }
      string trial=legacy::run_synth(argv[1],opt);''',
       '''      if(limit>0){
        double elapsed=r71_elapsed();
        const double cap=r71_guard?std::min(r71_search_cap,0.72*double(limit)):0.72*limit;
        // Legacy runs have no cooperative interruption; stop earlier
        // in short budgets unless a feasible incumbent was already found.
        if(elapsed>=cap || (r71_guard && limit<=250 && elapsed>=0.35*limit)){
          if(r71_trace)std::cerr<<"R71_TRACE event=legacy_stop elapsed_ms="<<elapsed<<"\\n";
          break;
        }
      }
      auto r71_legacy_started=Clock::now();
      string trial=legacy::run_synth(argv[1],opt);''',
       'legacy guarded dispatch')
    s=replace_one(s,
       '''      ++completed;
   }
 }
 if(!b.valid)return 6;''',
       '''      ++completed;
      if(r71_trace)std::cerr<<"R71_TRACE event=legacy"
        <<" elapsed_ms="<<r71_elapsed()
        <<" candidate_ms="<<std::chrono::duration<double,std::milli>(Clock::now()-r71_legacy_started).count()
        <<" candidate_area="<<z.area<<" candidate_delay="<<z.delay
        <<" incumbent_area="<<b.area<<"\\n";
   }
 }
 if(!b.valid)return 6;''',
       'legacy trace')
    s=replace_one(s,
       ''' auto within_budget=[&](double pct){
   return limit<=0 || chrono::duration<double,milli>(Clock::now()-start).count() < pct*limit;
 };''',
       ''' auto within_budget=[&](double pct){
   if(limit<=0)return true;
   const double cap=(r71_guard && limit<=250)?std::min(pct*double(limit),r71_search_cap):pct*double(limit);
   return r71_elapsed()<cap;
 };''',
       'postprocessing budget')
    s=replace_one(s,
       ''' cerr<<"completed="<<completed<<" chosen="<<chosen<<" area="<<b.area<<" delay="<<b.delay<<'\\n';
 return out?0:7;''',
       ''' cerr<<"completed="<<completed<<" chosen="<<chosen<<" area="<<b.area<<" delay="<<b.delay<<'\\n';
 if(r71_trace)std::cerr<<"R71_TRACE event=finish total_ms="<<r71_elapsed()
   <<" area="<<b.area<<" delay="<<b.delay<<" completed="<<completed<<"\\n";
 return out?0:7;''',
       'finish trace')
    return s

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-root',type=Path,default=UPSTREAM)
    args=ap.parse_args()
    src=args.source_root.resolve()
    raw=(src/'synth_round51.cpp').read_bytes()
    r7=load_round7()
    blob=r7.git_blob_sha(raw.replace(b'\r\n',b'\n'))
    if blob!=r7.UPSTREAM_GIT_BLOB:
        raise SystemExit(f'Frozen R5.1 source mismatch: expected {r7.UPSTREAM_GIT_BLOB}; got {blob}. Refusing to patch.')
    initial=raw.decode('utf-8').replace('\r\n','\n')
    round7=r7.patch(initial)
    round71=patch71(round7)
    target=HERE/'src';target.mkdir(exist_ok=True)
    output=target/'synth_round71.cpp';output.write_text(round71,encoding='utf-8')
    hashes={}
    for header in ('typed_netgraph.hpp','polarity_mapper.hpp','algebraic_mapper.hpp'):
        shutil.copy2(src/header,target/header)
        hashes[header]=hashlib.sha256((target/header).read_bytes()).hexdigest()
    hashes['synth_round71.cpp']=hashlib.sha256(output.read_bytes()).hexdigest()
    manifest={'milestone':'Round 7.1','upstream_blob':blob,
      'upstream_sha256':hashlib.sha256(raw).hexdigest(),
      'generated_source_sha256':hashes['synth_round71.cpp'],'generated_files_sha256':hashes,
      'policy':'UFUG_R71_POLICY=guard (default); off = Round7 portfolio ablation',
      'cover_ablation':'UFUG_R7_LEGACY_MERGE, UFUG_R7_LEGACY_COVER'}
    (HERE/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('Generated',output)
    print('SHA256',hashes['synth_round71.cpp'])

if __name__=='__main__':main()
