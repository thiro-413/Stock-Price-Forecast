#!/usr/bin/env python3
"""保存済み6月8バッチを集計する。予測モデルやプロンプトは作成しない。"""
import csv,json,hashlib,statistics
from pathlib import Path
from collections import Counter
from research import trading_days
ROOT=Path(__file__).resolve().parent
def save(name,value):
    (ROOT/'results'/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
rows=[]
for b in range(1,9):
    part=json.loads((ROOT/f'results/batch{b:02d}_data.json').read_text())
    for r in part: r['training_batch']=b
    rows+=part
days=sorted({r['date'] for r in rows})
assert days==trading_days(6) and len(rows)==220
assert all(sum(r['date']==d for r in rows)==10 for d in days)
assert len({(r['date'],r['code']) for r in rows})==220
sets={d:{r['code'] for r in rows if r['date']==d} for d in days}
hits=[len(sets[a]&sets[b]) for a,b in zip(days,days[1:])]
frequency=Counter(r['code'] for r in rows);names={r['code']:r['name'] for r in rows}
unknown=sum(r['evidence_grade']=='U' for r in rows)
summary={'days':len(days),'stock_days':len(rows),'unique_stocks':len(names),
 'markets':dict(Counter(r['market'] for r in rows)),
 'evidence_grades':dict(Counter(r['evidence_grade'] for r in rows)),
 'unknown_rows':unknown,'unknown_pct':100*unknown/len(rows),
 'previous_top10_overlap':{'transitions':len(hits),'total_intersections':sum(hits),
 'mean_hits':statistics.mean(hits),'median_hits':statistics.median(hits),'min_hits':min(hits),
 'max_hits':max(hits),'frequency':dict(Counter(hits)),
 'note':'学習期間の事後集合比較。封印済み事前予測成績ではない。'},
 'most_frequent_top10_stocks':[{'code':c,'name':names[c],'stock_days':n} for c,n in frequency.most_common(10)],
 'july_predictions_executed':False,'full_universe_resort_complete':False,
 'long_history_complete':False,'model_frozen':False,'screening_prompt_created':False}
save('june_summary.json',summary);save('june_data.json',rows)
with (ROOT/'results/june_data.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
files=[f'results/batch{b:02d}_data.json' for b in range(1,9)]+[
 'results/june_summary.json','results/june_data.json','results/june_data.csv',
 'results/june_learning_summary.md','finalize_june.py','research.py','PROTOCOL.md']
save('june_manifest.json',{'scope':'June top10 retrospective review',
 'checks':'22 days / 220 rows / 146 unique stock codes',
 'limitations':['full universe raw prices not fully obtained','long OHLCV incomplete','historical predictor versions incomplete'],
 'files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}})
print(json.dumps(summary,ensure_ascii=False))
