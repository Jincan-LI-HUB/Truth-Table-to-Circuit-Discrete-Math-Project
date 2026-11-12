"""Independent, standard-library checks of new explanatory examples in Draft v0.6.

These are constructed didactic examples, not official Stage 1 benchmark results.
Run: python3 shared/scripts/verify_deep_exposition.py
"""
from itertools import product

def f1(a,b,c): return (a and b) or ((not a) and c)
def f2(a,b,c): return f1(a,b,c) or b
def f2_factored(a,b,c): return b or ((not a) and c)
def f2_pos(a,b,c): return (b or (not a)) and (b or c)

def influence(fn,idx):
    other=[i for i in range(3) if i!=idx]
    changes=0
    for pair in product((0,1),repeat=2):
        x=[0,0,0]
        for k,v in zip(other,pair):x[k]=v
        x[idx]=0;v0=fn(*x)
        x[idx]=1;v1=fn(*x)
        changes+=(v0!=v1)
    return changes,4

rows=list(product((0,1),repeat=3))
for a,b,c in rows:
    assert f2(a,b,c)==f2_factored(a,b,c)==f2_pos(a,b,c)
    # SOP cover: each cube is in on-set, union is exact
    sop=b or ((not a) and c)
    assert sop==f2(a,b,c)
    # XOR cofactor identity: (not x & q) | (x & not q) == x xor q
    for q in (0,1):
        x=a
        assert bool(((not x) and q) or (x and (not q)))==bool(x^q)

mask=sum(int(bool(f2(*r))) << (4*r[0]+2*r[1]+r[2]) for r in rows)
assert mask==206,mask
assert [influence(f1,i) for i in range(3)]==[(2,4)]*3
assert [influence(f2,i) for i in range(3)]==[(1,4),(3,4),(1,4)]

# Original netlist: 4=NOT(a),5=AND(a,b),6=AND(4,c),7=OR(5,6),8=OR(7,b)
# After rewrite: 8=OR(b,6). All gates 4..8 still reachable from outputs (7,8).
# Prices: AND2 area/delay=2/2; OR2 area/delay=3/2; NOT area/delay=1/1.
A={4:1,5:2,6:2,7:3,8:3}
assert sum(A.values())==11
T={0:0,1:0,2:0,3:0}
T[4]=T[1]+1;T[5]=max(T[1],T[2])+2
T[6]=max(T[4],T[3])+2;T[7]=max(T[5],T[6])+2
old8=max(T[7],T[2])+2
new8=max(T[2],T[6])+2
assert (T[7],old8,new8)==(5,7,5)
# Dtarget=8; y1=7,y2=8; old 7 feeds 8 -> requirement min(8,8-2)
R7_old=min(8,8-2)
R7_new=8 # no use of 7 by 8
assert (R7_old,R7_new)==(6,8)
print('PASS: eight truth rows, SOP/POS equality, cut mask=0xCE')
print('PASS: influences f1=(1/2,1/2,1/2); f2=(1/4,3/4,1/4)')
print('PASS: cofactor/XOR identity, area=11, delay 7->5, required time R(7): 6->8')
