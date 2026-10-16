#!/usr/bin/env python3
"""第6回の保存原文と集計値を照合し、累積集計を更新する。"""
import csv,json,re,hashlib
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
def texts(v):
    if isinstance(v,dict):
        if isinstance(v.get('text'),str): yield v['text']
        for k,x in v.items():
            if k!='text': yield from texts(x)
    elif isinstance(v,list):
        for x in v: yield from texts(x)
def dump(name,v):
    (ROOT/'results'/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
mapping={'7843':'2026-06-22','7851':'2026-06-23','7860':'2026-06-24'}
main=defaultdict(dict);secondary=defaultdict(dict)
pat=re.compile(r'L\d+: 【\d+†([0-9A-Z]{4})†[^】]+】(?:☆)?\s+(.+?)\s+(東Ｐ|東Ｓ|東Ｇ)\s+([\d,.]+)\s+\+([\d,.]+)\s+\+([\d.]+)%\s+([\d,]+)')
pat2=re.compile(r'L\d+: (\d+)\s*\|\s*([0-9A-Z]{4})\s*\|\s*(.*?)\s*\|\s*([\d,.]+)\s*\|\s*\+([\d,.]+)\s*\|\s*\+([\d.]+)%\s*\|\s*([\d,]+)株')
def values(close,change,pct,vol):
    return tuple(float(x.replace(',','')) for x in (close,change,pct))+(int(vol.replace(',','')),)
for f in sorted((ROOT/'evidence').glob('b6_*.json')):
    for block in texts(json.loads(f.read_text())):
        for page in block.split('--------------------------------------------------------------------------------'):
            m=re.search(r'fiveup/(7843|7851|7860)\.html',page)
            if m:
                for hit in pat.finditer(page.replace('|',' ')):
                    code,name,market,close,change,pct,vol=hit.groups()
                    main[mapping[m[1]]][code]=values(close,change,pct,vol)
            if 'uiblog.hatenablog.com/entry/' not in page: continue
            m=re.search(r'### 2026年6月(22|23|24)日',page)
            if not m: continue
            # PTSと値下がり表は日中終値実績から必ず除外する。
            section=page.split('値上がり率上位',1)[-1].split('値下がり率上位',1)[0]
            for hit in pat2.finditer(section):
                rank,code,name,close,change,pct,vol=hit.groups()
                secondary['2026-06-'+m[1]][code]=values(close,change,pct,vol)
rows=list(csv.DictReader((ROOT/'data/batch06_rankings.csv').open()))
checks=[]
for r in rows:
    wanted=tuple(float(r[k]) for k in ('close','change','reported_pct'))+(int(r['volume']),)
    assert main[r['date']].get(r['code'])==wanted,('main',r)
    assert secondary[r['date']].get(r['code'])==wanted,('secondary',r)
    checks.append({'date':r['date'],'code':r['code'],'main_table_match':True,'secondary_table_match':True})
assert len(checks)==30
dump('batch06_source_checks.json',checks)
allrows=[]
for n in range(1,7): allrows+=json.loads((ROOT/f'results/batch{n:02d}_data.json').read_text())
days=sorted({r['date'] for r in allrows})
sets={d:{r['code'] for r in allrows if r['date']==d} for d in days}
overlap=[{'from':x,'to':y,'intersection':sorted(sets[x]&sets[y]),'hits':len(sets[x]&sets[y])} for x,y in zip(days,days[1:])]
unknown=sum(r['evidence_grade']=='U' for r in allrows)
summary={'completed_batch':6,'completed_days':len(days),'cumulative_stock_days':len(allrows),'cumulative_unique_stocks':len({r['code'] for r in allrows}),'unknown_cause_rows':unknown,'previous_top10_overlap':overlap,'note':'事後の集合一致。事前予測成績ではない。','source_table_check':'batch06: 30/30 main and 30/30 secondary matches; PTS tables excluded; secondary agreement is not proof of independent origin'}
dump('cumulative_summary.json',summary)
files=['data/batch06_rankings.csv','data/batch06_analysis.json','results/batch06_data.json','results/batch06_report.md','results/batch06_findings.md','results/batch06_source_checks.json','research.py','finalize_batch06.py']
dump('batch06_manifest.json',{'execution_date_jst':'2026-10-16','batch':6,'price_checks':'passed','source_value_checks':'30/30 main and 30/30 secondary table matches','unknown_causes':11,'next_batch_requires_user_continue':True,'july_predictions_executed':False,'full_universe_resort':False,'long_ohlcv_complete':False,'files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}})
print(json.dumps({'matches':len(checks),'cumulative_rows':len(allrows),'unique_stocks':summary['cumulative_unique_stocks'],'unknown_cause_rows':unknown,'new_overlaps':overlap[-3:]},ensure_ascii=False))
