#!/usr/bin/env python3
"""Research-only input conformance and default-policy preparation.
Does not change archived Round 8.x snapshots or claim grading-server passes.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

PARENT_SHA = '6d21a7d3cf80a8662f4f42a965e84c50d6cffcef7766a4d2dccf282c204078d8'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canonicalize(src, dst):
    tokens = src.read_text().split()
    n, m = map(int, tokens[:2])
    assert 1 <= n <= 20 and m >= 1
    N = 1 << n
    assert len(tokens) in (2+N+7, 2+N+8, 2+N+9), (src, len(tokens), N)
    groups = tokens[2:2+N]
    assert all(len(t)==m and set(t)<={'0','1'} for t in groups), str(src)
    tail = list(map(int, tokens[2+N:]))
    assert all(x>0 for x in tail[:7]), str(src)
    assert all(x>=0 for x in tail[7:]), str(src)
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('w',encoding='ascii',newline='\n') as out:
        out.write(str(n)+'\n'+str(m)+'\n')
        out.write(' '.join(groups)+'\n')
        out.write(f'{tail[0]} {tail[1]}\n{tail[2]} {tail[3]}\n{tail[4]} {tail[5]}\n{tail[6]}\n')
        for v in tail[7:]:out.write(str(v)+'\n')
    return {'file':src.name,'n':n,'m':m,'runtime_limit':tail[7] if len(tail)>7 else 0,
            'ram_limit':tail[8] if len(tail)>8 else 0,
            'input_sha256':sha(src),'canonical_sha256':sha(dst),
            'input_bytes':src.stat().st_size,'canonical_bytes':dst.stat().st_size,
            'truth_table_preserved':True, 'costs_and_limits_preserved':True}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--delivery',type=Path,required=True, help='Path to frozen UFUG2106_Round8_7_Delivery')
    p.add_argument('--output',type=Path,required=True,help='Separate output folder')
    p.add_argument('--stress-only',action='store_true',help='Canonicalize just 3 stress cases')
    p.add_argument('--make-default-extra-sop-copy',action='store_true')
    args=p.parse_args()
    root=args.delivery.resolve();out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    rec=[]
    for folder in (['stress_v2'] if args.stress_only else ['holdouts','stress_v2']):
        for src in sorted((root/folder).glob('*.txt')):
            rec.append(canonicalize(src,out/'canonical'/folder/src.name))
    result={'status':'converted','normalization':'Only whitespace layout changed; exact truth tokens and numeric parameters retained.', 'cases':rec}
    if args.make_default_extra_sop_copy:
        srcdir=root/'src';parent=srcdir/'synth_round86.cpp'
        actual=sha(parent)
        if actual!=PARENT_SHA:raise RuntimeError('Frozen parent source hash mismatch: '+actual)
        target=out/'standalone_extra_sop'/'src'
        if target.exists():raise RuntimeError('Refuse to overwrite existing submission test copy: '+str(target))
        shutil.copytree(srcdir,target)
        fn=target/'synth_round86.cpp';old=fn.read_text()
        needle='r86env_early?r86env_early:"baseline"'
        assert old.count(needle)==1
        fn.write_text(old.replace(needle,'r86env_early?r86env_early:"extra_sop"',1))
        result['candidate']={'parent_sha256':actual,'candidate_sha256':sha(fn),'path':str(fn),
        'changed_behavior':'Only the no-environment-variable R86 default changed from baseline to extra_sop',
        'compilation':'g++ -O2 -std=c++17 -pipe -DNDEBUG src/synth_round86.cpp -o synth_submission_candidate'}
    (out/'PREPARATION_MANIFEST.json').write_text(json.dumps(result,indent=2)+'\n')
    print('CANONICALIZED',len(rec),'cases; output',out)
    if args.make_default_extra_sop_copy:print('CANDIDATE_SOURCE',result['candidate']['candidate_sha256'])

if __name__=='__main__':main()
