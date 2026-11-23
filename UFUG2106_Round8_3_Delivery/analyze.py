import pandas as pd,glob,os,numpy as np,json
from pathlib import Path
base=Path('/mnt/data/r83_audit/experiment/official')
DF=[]
for file in sorted(base.glob('stage*_run*_*.csv')):
 name=file.stem
 import re
 m=re.fullmatch(r'(stage[12])_run([12])_(.+)',name)
 if not m: continue
 d=pd.read_csv(file);d['stage']=m[1];d['run']=int(m[2]);d['variant']=m[3];DF.append(d)
df=pd.concat(DF,ignore_index=True)
assert len(df)==600,len(df)
print('n rows',len(df),'statuses',df.status.value_counts().to_dict());print('versions',df.variant.unique())
R=df.groupby(['run','variant']).agg(area=('area','sum'),delay=('delay','sum'),rtime_sum=('runtime_ms','sum'),rtime_median=('runtime_ms','median'),passed=('status',lambda v:sum(v=='PASS'))).reset_index()
print('\nTotals:')
print(R.to_string(index=False,float_format=lambda x:f'{x:.3f}'))
print('\nStage summary:')
print(df.groupby(['stage','run','variant']).agg(area=('area','sum'),delay=('delay','sum'),rtime_sum=('runtime_ms','sum'),rtime_med=('runtime_ms','median')).to_string(float_format=lambda x:f'{x:.2f}'))

for run in (1,2):
 base_df=df[(df.variant=='r821_dual_area')&(df.run==run)].set_index(['stage','case'])
 print('\n--- Run',run,'paired to old dual ---')
 for v in df.variant.unique():
  dat=df[(df.variant==v)&(df.run==run)].set_index(['stage','case'])
  ar=dat.area-base_df.area; de=dat.delay-base_df.delay; ratios=dat.runtime_ms/base_df.runtime_ms
  log=np.log(ratios)
  adp=((dat.area*dat.delay)/(base_df.area*base_df.delay)).replace([np.inf,-np.inf],np.nan)
  print(v,'area_diff=',int(ar.sum()),'area_diff_cases=',int((ar!=0).sum()),'improved=',int((ar<0).sum()),'degrade=',int((ar>0).sum()),'delay_diff=',int(de.sum()),'delay_diff_cases=',int((de!=0).sum()),'delay_up=',int((de>0).sum()),'delay_down=',int((de<0).sum()),'geom_runtime_ratio=',round(float(np.exp(log.mean())),4),'geom_adp_ratio=',round(float(np.exp(np.log(adp).mean())),5),'runtime_ratio_bounds',round(float(ratios.min()),3),round(float(ratios.max()),3))

for v in sorted(df.variant.unique()):
 d1=df[(df.variant==v)&(df.run==1)].set_index(['stage','case']).sort_index();d2=df[(df.variant==v)&(df.run==2)].set_index(['stage','case']).sort_index()
 differ=d1[['area','delay']].compare(d2[['area','delay']]);rtime=d2.runtime_ms/d1.runtime_ms
 print('\nCross run',v,'area_diff_cases',int((d1.area!=d2.area).sum()),'delay_diff_cases',int((d1.delay!=d2.delay).sum()),'rtime_geom_2/1',round(float(np.exp(np.log(rtime).mean())),3))
 if len(differ):print(differ.to_string())

print('\nCasewise comparison each version VS base run 1 (nonzero area):')
r=1; b=df[(df.variant=='r821_dual_area')&(df.run==r)].set_index(['stage','case'])
for v in ('r83_fast_area','r83_stable_dual','r83_dense_dual','r83_stable_adp'):
 d=df[(df.variant==v)&(df.run==r)].set_index(['stage','case']);di=d.area-b.area
 print('\n',v);print(pd.concat([b[['area','delay']].rename(columns={'area':'b_area','delay':'b_delay'}),d[['area','delay']].rename(columns={'area':'v_area','delay':'v_delay'}),di.rename('delta')],axis=1).query('delta!=0').sort_values('delta',key=lambda s:s.abs(),ascending=False).head(18).to_string())

print('\nLargest relative runtimes and cases near runtime limit?')
print(df.groupby(['stage','case']).runtime_ms.max().sort_values(ascending=False).head(20).to_string())

df.to_csv('/mnt/data/r83_audit/official_600_records.csv',index=False)
R.to_csv('/mnt/data/r83_audit/version_totals.csv',index=False)
