#!/usr/bin/env python3
"""Deterministically materialize Round 7 from the user's frozen Round 5.1 source.

The delivery archive intentionally does not duplicate the 43 KB+ upstream
copyright-bearing source; it copies the existing verified local source and
applies two exact, auditable kernel substitutions. Requires no network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM = ROOT.parent / 'UFUG2106_Round5.1_Delivery' / 'src'
SRC = ROOT / 'src'
UPSTREAM_GIT_BLOB = '68ec9f54b27081641ac10358f81eef260acfcbdb'


def git_blob_sha(raw: bytes) -> str:
    header = b'blob ' + str(len(raw)).encode() + b'\x00'
    return hashlib.sha1(header + raw).hexdigest()


def replace_once(source: str, before: str, after: str, what: str) -> str:
    occurrences = source.count(before)
    if occurrences != 1:
        raise ValueError(f'{what}: expected exactly one source anchor, got {occurrences}')
    return source.replace(before, after, 1)


def splice_between(source: str, start: str, end: str, replacement: str, what: str) -> str:
    if what == 'exact bitset greedy cover':
        scope = source.index('const std::vector<std::array<R5CoverPlan,2>>& shared_covers(')
        i = source.index(start, scope)
        if i > source.index('string run_synth(', scope):
            raise ValueError('greedy cover anchor escaped shared_covers()')
    else:
        if source.count(start) != 1:
            raise ValueError(f'{what}: ambiguous/missing start anchor')
        i = source.index(start)
    j = source.index(end, i + len(start))
    return source[:i] + replacement + source[j:]


MERGE_START = '   vector<R5Cube> prime;\n   while(!cur.empty()){'
MERGE_END = '\n   sort(prime.begin(),prime.end(),'
MERGE_REPLACEMENT = r'''   vector<R5Cube> prime;
   const auto r7_merge_start = std::chrono::steady_clock::now();
   while(!cur.empty()){
    ++r7_merge_rounds;
    vector<char> used(cur.size());vector<R5Cube> nxt;
    unordered_set<unsigned long long> hash;
    if(r7_legacy_merge){
     // A/B ablation: the exact Round 5.1 quadratic loop.
     for(size_t a=0;a<cur.size();a++)for(size_t b=a+1;b<cur.size();b++){
      ++r7_merge_probes;
      if(cur[a].mask!=cur[b].mask)continue;
      int diff=(cur[a].val^cur[b].val)&cur[a].mask;
      if(__builtin_popcount((unsigned)diff)!=1)continue;
      used[a]=used[b]=1;
      int mk=cur[a].mask^diff,v=cur[a].val&mk;
      auto id=((unsigned long long)(unsigned)mk<<32)|(unsigned)v;
      if(hash.insert(id).second)nxt.push_back({v,mk});
     }
    }else{
     // For a fixed mask, two normalized cubes merge iff their
     // values differ by one bit set in the mask. O(k*S) expected.
     unordered_map<unsigned long long,size_t> where;
     where.reserve(cur.size()*2+1);
     for(size_t a=0;a<cur.size();a++){
      auto key=((unsigned long long)(unsigned)cur[a].mask<<32)|
               (unsigned)cur[a].val;
      where.emplace(key,a);
     }
     for(size_t a=0;a<cur.size();a++){
      int mask=cur[a].mask,val=cur[a].val;
      for(unsigned bits=(unsigned)mask;bits;bits&=(bits-1)){
       unsigned bit=bits&(~bits+1U);
       auto key=((unsigned long long)(unsigned)mask<<32)|
                (unsigned)(val^(int)bit);
       ++r7_merge_probes;
       auto it=where.find(key);
       if(it==where.end()||it->second<=a)continue;
       size_t b=it->second;
       used[a]=used[b]=1;
       int mk=mask^(int)bit,v=val&mk;
       auto id=((unsigned long long)(unsigned)mk<<32)|(unsigned)v;
       if(hash.insert(id).second)nxt.push_back({v,mk});
      }
     }
    }
    for(size_t a=0;a<cur.size();a++)if(!used[a])prime.push_back(cur[a]);
    cur.swap(nxt);
   }
   r7_merge_ms+=std::chrono::duration<double,std::milli>(
     std::chrono::steady_clock::now()-r7_merge_start).count();'''

GREEDY_START = '   vector<char> uncovered(Q,0);int remaining=0;'
GREEDY_END = '\n  }\n }\n return cache;'
GREEDY_REPLACEMENT = r'''   const auto r7_cover_start=std::chrono::steady_clock::now();
   if(r7_legacy_cover){
    // A/B ablation: preserve Round 5.1 greedy scan verbatim.
    vector<char> uncovered(Q,0);int remaining=0;
    for(int i=0;i<Q;i++)if(tt[i]==goal){uncovered[i]=1;remaining++;}
    while(remaining){
     double best=-1;int which=-1;
     for(int t=0;t<(int)prime.size();t++){
      int gains=0;
      for(int i=0;i<Q;i++){
       ++r7_cover_probes;
       if(uncovered[i] && (i&prime[t].mask)==prime[t].val)gains++;
      }
      if(!gains)continue;
      int cost=max(1,__builtin_popcount((unsigned)prime[t].mask));
      double score=double(gains)/(0.4+cost);
      if(score>best){best=score;which=t;}
     }
     if(which<0)throw runtime_error("cover failed");
     auto q=prime[which];plan.chosen.push_back(q);
     for(int i=0;i<Q;i++)if(uncovered[i] && (i&q.mask)==q.val){uncovered[i]=0;remaining--;}
    }
   }else{
    // One bit per minterm; preserve exact gains and original tie-breaking.
    const int words=(Q+63)/64;
    vector<unsigned long long> remaining_bits(words,0);
    int remaining=0;
    for(int i=0;i<Q;i++)if(tt[i]==goal){
     remaining_bits[i>>6]|=1ULL<<(i&63);remaining++;
    }
    vector<vector<unsigned long long>> covers(
      prime.size(),vector<unsigned long long>(words,0));
    for(int t=0;t<(int)prime.size();t++){
     for(int i=0;i<Q;i++)if((i&prime[t].mask)==prime[t].val)
      covers[t][i>>6]|=1ULL<<(i&63);
    }
    while(remaining){
     double best=-1;int which=-1;
     for(int t=0;t<(int)prime.size();t++){
      int gains=0;
      for(int w=0;w<words;w++){
       ++r7_cover_probes;
       gains+=__builtin_popcountll(remaining_bits[w]&covers[t][w]);
      }
      if(!gains)continue;
      int cost=max(1,__builtin_popcount((unsigned)prime[t].mask));
      double score=double(gains)/(0.4+cost);
      if(score>best){best=score;which=t;}
     }
     if(which<0)throw runtime_error("cover failed");
     plan.chosen.push_back(prime[which]);
     for(int w=0;w<words;w++){
      unsigned long long removed=remaining_bits[w]&covers[which][w];
      remaining-=__builtin_popcountll(removed);
      remaining_bits[w]&=~removed;
     }
    }
   }
   r7_cover_ms+=std::chrono::duration<double,std::milli>(
     std::chrono::steady_clock::now()-r7_cover_start).count();'''


def patch(text: str) -> str:
    text = replace_once(
        text,
        ' if(data.n>13)return cache;\n const int n=data.n,m=data.m,N=1<<n;',
        ''' if(data.n>13)return cache;
 const bool r7_legacy_merge=[](){const char*p=std::getenv("UFUG_R7_LEGACY_MERGE");return p && *p=='1';}();
 const bool r7_legacy_cover=[](){const char*p=std::getenv("UFUG_R7_LEGACY_COVER");return p && *p=='1';}();
 unsigned long long r7_merge_probes=0,r7_cover_probes=0,r7_merge_rounds=0;
 double r7_merge_ms=0.0,r7_cover_ms=0.0;
 const int n=data.n,m=data.m,N=1<<n;''',
        'profile/cfg injection',
    )
    text = splice_between(text, MERGE_START, MERGE_END, MERGE_REPLACEMENT, 'exact cube merging')
    text = splice_between(text, GREEDY_START, GREEDY_END, GREEDY_REPLACEMENT, 'exact bitset greedy cover')
    text = replace_once(
        text,
        '\n  }\n }\n return cache;\n}\nstring run_synth(',
        '''
  }
 }
 if(const char* p=std::getenv("UFUG_ROUND5_PROFILE"))if(*p=='1'){
  std::cerr<<"R7_STAGE stage=covers merge_mode="<<(r7_legacy_merge?"legacy":"neighbor")
   <<" greedy_mode="<<(r7_legacy_cover?"legacy":"bitset")
   <<" merge_ms="<<std::fixed<<std::setprecision(3)<<r7_merge_ms
   <<" greedy_ms="<<r7_cover_ms
   <<" merge_probes="<<r7_merge_probes
   <<" greedy_probes="<<r7_cover_probes
   <<" merge_rounds="<<r7_merge_rounds<<"\\n";
 }
 return cache;
}
string run_synth(''',
        'profile injection',
    )
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', type=Path, default=UPSTREAM)
    ap.add_argument('--allow-source-drift', action='store_true')
    args = ap.parse_args()
    src = args.source_root.resolve()
    raw_path = src / 'synth_round51.cpp'
    if not raw_path.is_file():
        raise SystemExit(f'Missing frozen source: {raw_path}')
    raw = raw_path.read_bytes()
    normalized = raw.decode('utf-8').replace('\r\n', '\n')
    normalized_blob = git_blob_sha(normalized.encode('utf-8'))
    blob = git_blob_sha(raw)
    if normalized_blob != UPSTREAM_GIT_BLOB and not args.allow_source_drift:
        raise SystemExit(
            'Round 5.1 source SHA differs from the reviewed GitHub snapshot.\n'
            f'Expected git blob: {UPSTREAM_GIT_BLOB}\n'
            f'Actual git blob:   {blob}\nNormalized blob:   {normalized_blob}\n'
            'Review the changes before using --allow-source-drift.'
        )
    SRC.mkdir(exist_ok=True)
    output = patch(normalized)
    (SRC / 'synth_round7.cpp').write_text(output, encoding='utf-8')
    source_hashes = {'synth_round51.cpp': hashlib.sha256(raw).hexdigest()}
    for header in ('typed_netgraph.hpp', 'polarity_mapper.hpp', 'algebraic_mapper.hpp'):
        shutil.copy2(src / header, SRC / header)
        source_hashes[header] = hashlib.sha256((src / header).read_bytes()).hexdigest()
    manifest = {
        'milestone': 'Round 7',
        'upstream_git_blob': blob,
        'upstream_normalized_blob': normalized_blob,
        'source_hashes': source_hashes,
        'round7_source_sha256': hashlib.sha256(output.encode()).hexdigest(),
        'changes': ['exact hash-neighbor implicant merging',
                    'exact packed-bitset greedy cover',
                    'independent ablation switches and cover-stage profiling'],
    }
    (ROOT / 'SOURCE_MANIFEST.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Materialized: {SRC / "synth_round7.cpp"}')
    print(f'Round 7 source sha256: {manifest["round7_source_sha256"]}')


if __name__ == '__main__':
    main()
