#!/usr/bin/env python3
"""保存したWeb本文と選定30行を照合し、累積集計とハッシュを更新。"""
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
pattern=re.compile(r'L\d+: 【\d+†([0-9A-Z]{4})†[^】]+】(?:☆)?\s+(.+?)\s+(東Ｐ|東Ｓ|東Ｇ|福Ｑ|東EN|東Ｅ|名Ｎ)\s+([\d,.]+)\s+\+([\d,.]+)\s+\+([\d.]+)%\s+([\d,]+)')
byday=defaultdict(dict)
for filename in ('b3_rankings.json','b3_material_discover.json'):
    value=json.loads((ROOT/'evidence'/filename).read_text())
    for block in texts(value):
        # Each result page is delimited by the connector separator.
        for page in block.split('--------------------------------------------------------------------------------'):
            m=re.search(r'fiveup/(7753|7762|7771)\.html',page)
            if not m: continue
            day={'7753':'2026-06-09','7762':'2026-06-10','7771':'2026-06-11'}[m[1]]
            for match in pattern.finditer(page.replace('|',' ')):
                code,name,market,close,change,pct,vol=match.groups()
                byday[day][code]=(float(close.replace(',','')),float(change.replace(',','')),float(pct),int(vol.replace(',','')))
rows=list(csv.DictReader((ROOT/'data/batch03_rankings.csv').open()))
matched=[]
for r in rows:
    observed=byday[r['date']].get(r['code'])
    wanted=tuple(float(r[k]) for k in ('close','change','reported_pct'))+(int(r['volume']),)
    assert observed==wanted,(r['date'],r['code'],observed,wanted)
    matched.append({'date':r['date'],'code':r['code'],'match':True})
def dump(name,v):
    (ROOT/'results'/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
dump('batch03_source_checks.json',matched)
allrows=[]
for n in (1,2,3): allrows+=json.loads((ROOT/f'results/batch{n:02d}_data.json').read_text())
days=sorted({r['date'] for r in allrows})
sets={d:{r['code'] for r in allrows if r['date']==d} for d in days}
overlap=[{'from':x,'to':y,'intersection':sorted(sets[x]&sets[y]),'hits':len(sets[x]&sets[y])} for x,y in zip(days,days[1:])]
dump('cumulative_summary.json',{'completed_batch':3,'completed_days':len(days),'cumulative_stock_days':len(allrows),'cumulative_unique_stocks':len({r['code'] for r in allrows}),'unknown_cause_rows':sum(r['evidence_grade']=='U' for r in allrows),'previous_top10_overlap':overlap,'note':'事後の集合一致。事前予測成績ではない。','source_table_check':'batch03: all 30 selected price/change/volume records match archived source tables'})
files=['data/batch03_rankings.csv','data/batch03_analysis.json','results/batch03_data.json','results/batch03_report.md','results/batch03_findings.md','results/batch03_source_checks.json','research.py','finalize_batch03.py']
dump('batch03_manifest.json',{'execution_date_jst':'2026-10-16','batch':3,'price_checks':'passed','source_value_checks':'30/30 matched saved source tables','unknown_causes':11,'next_batch_requires_user_continue':True,'july_predictions_executed':False,'files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}})
print(json.dumps({'source_matches':len(matched),'cumulative_rows':len(allrows),'unique_stocks':len({r['code'] for r in allrows}),'unknown_cause_rows':sum(r['evidence_grade']=='U' for r in allrows),'overlaps':[r['hits'] for r in overlap]},ensure_ascii=False))
