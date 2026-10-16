#!/usr/bin/env python3
"""第5回の原文価格照合と累積集計。後日掲載ページは本文の取引日を使用。"""
import csv,json,re,hashlib
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
def texts(v):
    if isinstance(v,dict):
        if isinstance(v.get('text'),str): yield v['text']
        for key,val in v.items():
            if key!='text': yield from texts(val)
    elif isinstance(v,list):
        for val in v: yield from texts(val)
def dump(name,v):
    (ROOT/'results'/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
pattern=re.compile(r'L\d+: 【\d+†([0-9A-Z]{4})†[^】]+】(?:☆)?\s+(.+?)\s+(東Ｐ|東Ｓ|東Ｇ)\s+([\d,.]+)\s+\+([\d,.]+)\s+\+([\d.]+)%\s+([\d,]+)')
mapping={'7813':'2026-06-17','7823':'2026-06-18','7832':'2026-06-19'}
byday=defaultdict(dict)
for block in texts(json.loads((ROOT/'evidence/b5_rankings.json').read_text())):
    for page in block.split('--------------------------------------------------------------------------------'):
        m=re.search(r'fiveup/(7813|7823|7832)\.html',page)
        if not m: continue
        for hit in pattern.finditer(page.replace('|',' ')):
            code,name,market,close,change,pct,vol=hit.groups()
            byday[mapping[m[1]]][code]=(float(close.replace(',','')),float(change.replace(',','')),float(pct),int(vol.replace(',','')))
secondary=defaultdict(dict)
for filename in ('b5_cross_primary.json','b5_cross_macro.json'):
    for block in texts(json.loads((ROOT/'evidence'/filename).read_text())):
        for page in block.split('--------------------------------------------------------------------------------'):
            if 'uiblog.hatenablog.com/entry/' not in page: continue
            m=re.search(r'### 2026年6月(17|18|19)日',page)
            if not m: continue
            day='2026-06-'+m[1]
            for line in page.splitlines():
                hit=re.match(r'L\d+: (\d+)\s*\|\s*([0-9A-Z]{4})\s*\|\s*(.*?)\s*\|\s*([\d,.]+)\s*\|\s*\+([\d,.]+)\s*\|\s*\+([\d.]+)%\s*\|\s*([\d,]+)株',line)
                if hit:
                    rank,code,name,close,change,pct,vol=hit.groups()
                    secondary[day][code]=(float(close.replace(',','')),float(change.replace(',','')),float(pct),int(vol.replace(',','')))
rows=list(csv.DictReader((ROOT/'data/batch05_rankings.csv').open()))
checks=[]
for r in rows:
    wanted=tuple(float(r[k]) for k in ('close','change','reported_pct'))+(int(r['volume']),)
    assert byday[r['date']].get(r['code'])==wanted,('main',r)
    assert secondary[r['date']].get(r['code'])==wanted,('secondary',r)
    checks.append({'date':r['date'],'code':r['code'],'main_table_match':True,'secondary_table_match':True})
assert len(checks)==30
dump('batch05_source_checks.json',checks)
allrows=[]
for n in range(1,6): allrows+=json.loads((ROOT/f'results/batch{n:02d}_data.json').read_text())
days=sorted({r['date'] for r in allrows})
sets={d:{r['code'] for r in allrows if r['date']==d} for d in days}
overlap=[{'from':x,'to':y,'intersection':sorted(sets[x]&sets[y]),'hits':len(sets[x]&sets[y])} for x,y in zip(days,days[1:])]
unknown=sum(r['evidence_grade']=='U' for r in allrows)
summary={'completed_batch':5,'completed_days':len(days),'cumulative_stock_days':len(allrows),'cumulative_unique_stocks':len({r['code'] for r in allrows}),'unknown_cause_rows':unknown,'previous_top10_overlap':overlap,'note':'事後の集合一致。事前予測成績ではない。','source_table_check':'batch05: 30/30 main and 30/30 secondary matches; secondary June19 page posted June20, identified by body trading date'}
dump('cumulative_summary.json',summary)
files=['data/batch05_rankings.csv','data/batch05_analysis.json','results/batch05_data.json','results/batch05_report.md','results/batch05_findings.md','results/batch05_source_checks.json','research.py','finalize_batch05.py']
dump('batch05_manifest.json',{'execution_date_jst':'2026-10-16','batch':5,'price_checks':'passed','source_value_checks':'30/30 main table and 30/30 secondary table matches','unknown_causes':13,'next_batch_requires_user_continue':True,'july_predictions_executed':False,'files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}})
print(json.dumps({'matches':len(checks),'cumulative_rows':len(allrows),'unique_stocks':summary['cumulative_unique_stocks'],'unknown_cause_rows':unknown,'new_overlaps':[r['hits'] for r in overlap[-3:]]},ensure_ascii=False))
