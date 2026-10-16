#!/usr/bin/env python3
"""第4バッチの価格原文照合、二次表品質検査、累積集計、改変検出用ハッシュ。"""
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
pattern=re.compile(r'L\d+: 【\d+†([0-9A-Z]{4})†[^】]+】(?:☆)?\s+(.+?)\s+(東Ｐ|東Ｓ|東Ｇ|福Ｑ|東EN|東Ｅ|名Ｎ)\s+([\d,.]+)\s+\+([\d,.]+)\s+\+([\d.]+)%\s+([\d,]+)')
mapping={'7785':'2026-06-12','7795':'2026-06-15','7805':'2026-06-16'}
source=json.loads((ROOT/'evidence/b4_rankings.json').read_text())
byday=defaultdict(dict)
for block in texts(source):
    for page in block.split('--------------------------------------------------------------------------------'):
        m=re.search(r'fiveup/(7785|7795|7805)\.html',page)
        if not m: continue
        for match in pattern.finditer(page.replace('|',' ')):
            code,name,market,close,change,pct,vol=match.groups()
            byday[mapping[m[1]]][code]=(float(close.replace(',','')),float(change.replace(',','')),float(pct),int(vol.replace(',','')))
rows=list(csv.DictReader((ROOT/'data/batch04_rankings.csv').open()))
matched=[]
for r in rows:
    expected=tuple(float(r[k]) for k in ('close','change','reported_pct'))+(int(r['volume']),)
    assert byday[r['date']].get(r['code'])==expected,(r,byday[r['date']].get(r['code']))
    matched.append({'date':r['date'],'code':r['code'],'primary_table_match':True})
assert len(matched)==30
# 別表は日付と値を独立して検査。6/12上昇欄は前日転載のため不採用。
second=defaultdict(dict)
for block in texts(json.loads((ROOT/'evidence/b4_crosscheck.json').read_text())):
    for page in block.split('--------------------------------------------------------------------------------'):
        m=re.search(r'/2026/06/(12|15|16)/',page)
        if not m: continue
        day='2026-06-'+m[1]
        for line in page.splitlines():
            hit=re.match(r'L\d+: (\d+)\s*\|\s*([0-9A-Z]{4})\s*\|\s*(.*?)\s*\|\s*([\d,.]+)\s*\|\s*\+([\d,.]+)\s*\|\s*\+([\d.]+)%\s*\|\s*([\d,]+)株',line)
            if hit:
                rank,code,name,close,change,pct,vol=hit.groups()
                second[day][code]=(float(close.replace(',','')),float(change.replace(',','')),float(pct),int(vol.replace(',','')))
for r in rows:
    if r['date']=='2026-06-12': continue
    expected=byday[r['date']][r['code']]
    assert second[r['date']].get(r['code'])==expected,(r,second[r['date']].get(r['code']),expected)
    next(x for x in matched if x['date']==r['date'] and x['code']==r['code'])['secondary_table_match']=True
assert second['2026-06-12'].get('3825')[0]==201
assert byday['2026-06-12']['3825'][0]==276
dump('batch04_source_checks.json',matched)
allrows=[]
for n in (1,2,3,4): allrows+=json.loads((ROOT/f'results/batch{n:02d}_data.json').read_text())
days=sorted({r['date'] for r in allrows})
sets={d:{r['code'] for r in allrows if r['date']==d} for d in days}
overlap=[{'from':x,'to':y,'intersection':sorted(sets[x]&sets[y]),'hits':len(sets[x]&sets[y])} for x,y in zip(days,days[1:])]
unknown=sum(r['evidence_grade']=='U' for r in allrows)
dump('cumulative_summary.json',{'completed_batch':4,'completed_days':len(days),'cumulative_stock_days':len(allrows),'cumulative_unique_stocks':len({r['code'] for r in allrows}),'unknown_cause_rows':unknown,'previous_top10_overlap':overlap,'note':'事後の集合一致。事前予測成績ではない。','source_table_check':'batch04: 30/30 main-table matches; 20/20 secondary matches for June15/16; June12 secondary gain table rejected as stale; 3 June12 JPX rows manually verified'})
files=['data/batch04_rankings.csv','data/batch04_analysis.json','results/batch04_data.json','results/batch04_report.md','results/batch04_findings.md','results/batch04_source_checks.json','results/batch04_source_quality.json','research.py','finalize_batch04.py']
dump('batch04_manifest.json',{'execution_date_jst':'2026-10-16','batch':4,'price_checks':'passed','source_value_checks':'30/30 main table, 20/20 eligible cross-table checks','unknown_causes':sum(r['evidence_grade']=='U' for r in json.loads((ROOT/'results/batch04_data.json').read_text())),'next_batch_requires_user_continue':True,'july_predictions_executed':False,'files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}})
print(json.dumps({'source_matches':len(matched),'secondary_matches':20,'rejected_secondary_day':'2026-06-12','cumulative_rows':len(allrows),'unique_stocks':len({r['code'] for r in allrows}),'unknown_cause_rows':unknown,'overlaps':[r['hits'] for r in overlap]},ensure_ascii=False))
