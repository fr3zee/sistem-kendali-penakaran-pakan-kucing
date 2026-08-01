#!/usr/bin/env python3
"""Tahap 2 reproducibility verification tool; never overwrites baseline."""
from __future__ import annotations
import csv, hashlib, json, platform, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import scipy, statsmodels
from scipy import stats

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'data'/'pengujian_final'/'master_dataset_160.csv'
import os as _os
OUT=Path(_os.environ.get('PIPELINE_OUTPUT_DIR', str(ROOT/'hasil'/'pemeriksaan_asumsi')))
SC=['Manual Cepat','Manual Presisi','Fixed PID','GS PID']; SP=[15,20,25,30]
MET=['AbsError_pct','MaxOvershoot_pct','Duration_s','RiseTime_10_90_s']; TOL=0.00005
BASELINE_DIR=ROOT/'hasil'/'pemeriksaan_asumsi'
BASE=['hasil_ketersediaan_data.csv','hasil_proporsi_dalam_toleransi_deskriptif.csv','hasil_shapiro_per_kelompok.csv','hasil_shapiro_residual_per_setpoint.csv','hasil_brown_forsythe_per_setpoint.csv','statistik_deskriptif_konsistensi_finalerror.csv']

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def ptxt(p): return '< 0.001' if p<.001 else f'{p:.4f}'
def norm(p): return 'Tidak terdapat bukti signifikan untuk menolak asumsi normalitas' if p>=.05 else 'Terdapat bukti penyimpangan dari distribusi normal'
def var(p): return 'Tidak terdapat bukti signifikan perbedaan varians' if p>=.05 else 'Varians tidak homogen'
def save(name, frame):
 p=OUT/name.replace('.csv','_reproduksi.csv'); frame.to_csv(p,index=False,lineterminator='\n'); return p
def rows(path):
 with path.open(encoding='utf-8-sig',newline='') as f:
  r=csv.DictReader(f); return r.fieldnames or [],list(r)
def compare(base,repro):
 h,a=rows(base); hr,b=rows(repro); bad=[]
 if h!=hr: return [{'file':base.name,'row':'HEADER','column':'*','baseline':h,'reproduction':hr,'difference':'header differs'}]
 if len(a)!=len(b): bad.append({'file':base.name,'row':'ROW_COUNT','column':'*','baseline':len(a),'reproduction':len(b),'difference':'row count differs'})
 for n,(x,y) in enumerate(zip(a,b),2):
  for k in h:
   u,v=x[k],y[k]; ok=u==v; d='text differs'
   if u=='< 0.001':
    if v=='< 0.001': ok=True; d="both values satisfy threshold '< 0.001'"
    else:
     try: ok=float(v)<.001; d="threshold baseline '< 0.001'"
     except ValueError: ok=False
   else:
    try: delta=float(v)-float(u); ok=abs(delta)<=TOL+1e-12; d=f'delta={delta:.10f}'
    except ValueError: pass
   if not ok: bad.append({'file':base.name,'row':n,'column':k,'baseline':u,'reproduction':v,'difference':d})
 return bad
def manifest(p,role):
 try: h,r=rows(p); rc=len(r); cc=len(h)
 except Exception: rc=cc=''
 return {'file':p.name,'role':role,'sha256':digest(p),'rows':rc,'columns':cc}
def main():
 OUT.mkdir(exist_ok=True); errors=[]; df=pd.read_csv(DATA)
 if len(df)!=160: errors.append(f'rows expected=160 actual={len(df)}')
 c=df.groupby(['Scenario','Setpoint_g']).size()
 if len(c)!=16 or not (c==10).all(): errors.append('Scenario × Setpoint must have 16 groups of 10')
 if not df.Valid.astype(str).str.upper().eq('TRUE').all(): errors.append('Valid must be TRUE')
 if not df.StopReason.eq('TARGET').all(): errors.append('StopReason must be TARGET')
 df.Scenario=pd.Categorical(df.Scenario,SC,ordered=True); df['WithinTolerance']=(df.FinalError_pct.abs()<=5).astype(int); df.SettlingTime_s=pd.to_numeric(df.SettlingTime_s,errors='coerce'); df['ST_available']=df.SettlingTime_s.notna()
 if ((df.WithinTolerance==1)!=df.ST_available).sum(): errors.append('WithinTolerance and SettlingTime_s mismatch')
 av=[]; pr=[]; sg=[]; sr=[]; bf=[]; co=[]
 for m in MET+['SettlingTime_s']:
  for s in SC:
   for z in SP:
    x=df[(df.Scenario==s)&(df.Setpoint_g==z)][m]; n=len(x); a=int(x.notna().sum()); miss=n-a; av.append([m,s,z,n,a,miss,'' if not miss else f'Settling tidak tersedia pada {miss} trial (kondisional)'])
 for s in SC:
  for z in SP:
   x=df[(df.Scenario==s)&(df.Setpoint_g==z)]; n=len(x); w=int(x.WithinTolerance.sum()); a=int(x.ST_available.sum()); mm=int(((x.WithinTolerance==1)!=x.ST_available).sum()); pr.append([s,z,n,w,n-w,round(w/n*100,1),a,n-a,mm,'CONSISTENT' if not mm else 'MISMATCH'])
   e=x.FinalError_g.to_numpy(float); co.append([s,z,n,f'{e.mean():.4f}',f'{e.std(ddof=1):.4f}',f'{e.var(ddof=1):.4f}',f'{e.min():.4f}',f'{e.max():.4f}'])
 for m in MET:
  for z in SP:
   x=df[df.Setpoint_g==z]; res=[]
   for s in SC:
    v=x[x.Scenario==s][m].dropna().to_numpy(float); w,p=stats.shapiro(v); sg.append([m,s,z,len(v),len(np.unique(v)),int((v==0).sum()),round((v==0).mean()*100,1),f'{stats.skew(v):.4f}',f'{w:.4f}',ptxt(p),norm(p)]); res.extend(v-v.mean())
   w,p=stats.shapiro(res); sr.append([m,z,len(res),'10/10/10/10',f'{w:.4f}',ptxt(p),f'{stats.skew(res):.4f}',norm(p),''])
   g=[x[x.Scenario==s][m].dropna().to_numpy(float) for s in SC]; w,p=stats.levene(*g,center='median'); bf.append([m,z,*map(len,g),'Brown-Forsythe (Levene median)',f'{w:.4f}',ptxt(p),var(p),''])
 frames={BASE[0]:pd.DataFrame(av,columns=['Metric','Scenario','Setpoint_g','n_total','n_available','n_unavailable','Keterangan']),BASE[1]:pd.DataFrame(pr,columns=['Scenario','Setpoint_g','n_total','n_within_tolerance','n_outside_tolerance','within_tolerance_pct','n_settlingtime_available','n_settlingtime_unavailable','mismatch_count','verification_status']),BASE[2]:pd.DataFrame(sg,columns=['Metric','Scenario','Setpoint_g','n','n_unique','zero_count','zero_pct','skewness','Shapiro_W','p_value','Keputusan']),BASE[3]:pd.DataFrame(sr,columns=['Metric','Setpoint_g','n_total_available','n_per_scenario','Shapiro_W','p_value','skewness_residual','Keputusan','Catatan']),BASE[4]:pd.DataFrame(bf,columns=['Metric','Setpoint_g','n_Manual_Cepat','n_Manual_Presisi','n_Fixed_PID','n_GS_PID','Test','Statistic','p_value','Keputusan','Catatan']),BASE[5]:pd.DataFrame(co,columns=['Scenario','Setpoint_g','n','mean_error_g','sd_error_g','variance_error_g','min_error_g','max_error_g'])}
 outputs={k:save(k,v) for k,v in frames.items()}; missing=[str(p) for p in [DATA,*[BASELINE_DIR/x for x in BASE],BASELINE_DIR/'rekomendasi_uji_tahap3.csv'] if not p.exists()]; bad=[] if missing else sum((compare(BASELINE_DIR/k,v) for k,v in outputs.items()),[])
 hashes={p.name:digest(p) for p in [DATA,*[BASELINE_DIR/x for x in BASE]] if p.exists()}; entries=[manifest(DATA,'master_dataset')]+[manifest(BASELINE_DIR/x,'baseline') for x in BASE]+[manifest(p,'reproduction') for p in outputs.values()]
 pd.DataFrame(entries).to_csv(OUT/'manifest.csv',index=False); status={'VALIDATION':'PASS' if not errors else 'FAIL','REPRODUCTION':'PASS' if not bad else 'MISMATCH','FILES':'PASS' if not missing else 'FAIL','HASH':'PASS' if len(hashes)==7 else 'FAIL'}; status['OVERALL']='PASS' if all(x=='PASS' for x in status.values()) else ('FAIL' if 'FAIL' in status.values() else 'MISMATCH')
 audit={'purpose':'Alat verifikasi reproduksibilitas Tahap 2; bukan pengganti baseline.','generated_at_utc':datetime.now(timezone.utc).isoformat(),'environment':{'python':sys.version,'scipy':scipy.__version__,'pandas':pd.__version__,'numpy':np.__version__,'statsmodels':statsmodels.__version__,'os':platform.platform()},'hashes':hashes,'missing_files':missing,'validation_errors':errors,'numeric_tolerance':TOL,'mismatch_count':len(bad),'mismatches':bad,'status':status}; (OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 report=['# Laporan Verifikasi Reproduksibilitas Tahap 2','','| Domain | Status |','|---|---|',*[f'| {k} | {v} |' for k,v in status.items()],'','Baseline Tahap 2 tidak diubah. Hasil folder ini adalah reproduksi terisolasi.','']
 if bad: report+=['## Mismatch','','| File | Baris | Kolom | Baseline | Reproduksi | Selisih |','|---|---:|---|---|---|---|',*[f"| {x['file']} | {x['row']} | {x['column']} | `{x['baseline']}` | `{x['reproduction']}` | {x['difference']} |" for x in bad]]
 else: report+=['## Hasil','','Semua pembandingan lolos. Tahap 3–5 dan Bab IV tidak perlu diubah.']
 (OUT/'laporan.md').write_text('\n'.join(report)+'\n',encoding='utf-8'); (OUT/'README.md').write_text('# Verifikasi Reproduksibilitas Tahap 2\n\nFolder hasil hitung ulang dan audit terhadap baseline. Bukan pengganti baseline; tidak mengubah Tahap 3–5.\n\n```powershell\npython tahap2_rekonstruksi_dan_verifikasi.py\n```\n\nLihat `audit.json`, `manifest.csv`, dan `laporan.md`.\n',encoding='utf-8'); print(json.dumps(status)); return 0 if status['OVERALL']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
