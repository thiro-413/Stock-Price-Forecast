"""Validate immutable predictions and batch5 prices before publication."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
from prepare_july import ROOT,save
from research import gate,digest,trading_days

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

old=0
for number in range(1,5):
 manifest=json.loads((ROOT/f'results/july_batch{number:02d}_manifest.json').read_text())
 for name,value in manifest['files'].items():assert sha(ROOT/name)==value,(number,name)
 old+=len(manifest['files'])
alljson=list(ROOT.rglob('*.json'))
for path in alljson:json.loads(path.read_text())
assert len(trading_days(7))==22
summary=json.loads((ROOT/'results/july_batch05_summary.json').read_text())
assert summary['hits']==5 and summary['cumulative_hits']==19
checks=[]
for suffix in ['17','21','22']:
 day='2026-07-'+suffix
 pred=json.loads((ROOT/f'results/july_predictions/{day}.json').read_text())
 assert digest(pred['payload'])==pred['sha256']
 assert sha(ROOT/f'data/july_inputs/{day}.json')==pred['input_sha256']
 assert not gate(pred['payload']['evidence'],day+'T08:30:00+09:00')['rejected']
 scores=json.loads((ROOT/f'results/july_scores/{day}.json').read_text())
 assert scores['candidates'][:10]==pred['payload']['predictions']
 for row in pred['payload']['predictions']:
  assert all(event['first_eligible_session']<=day for event in row['events'])
 actual=json.loads((ROOT/f'data/july_actuals/{day}.json').read_text())
 assert len(actual['top10'])==10 and len({row['code'] for row in actual['top10']})==10
 values=[row['return_pct'] for row in actual['top10']]
 assert values==sorted(values,reverse=True)
 checks.append(dict(date=day,sealed_sha256=pred['sha256'],cutoff_gate='passed',input_hash='passed',candidate_count=len(scores['candidates']),unverified_exclusions=len(scores['rejected_candidates']),hits=summary['evaluations'][len(checks)]['hits'],actual_price_count=9 if suffix=='21' else 10,no_regular_trade_count=1 if suffix=='21' else 0))
rows=list(csv.DictReader((ROOT/'results/july_batch05_predictions.csv').open(encoding='utf-8-sig')))
assert len(rows)==30
for row in rows:
 if row['price_status']=='no_regular_trade':
  assert row['date']=='2026-07-21' and row['code']=='5078' and row['actual_close']=='' and row['actual_return_pct']==''
  assert float(row['previous_close'])==4870
 else:
  assert float(row['actual_close'])>0 and float(row['previous_close'])>0
  assert abs(100*(float(row['actual_close'])/float(row['previous_close'])-1)-float(row['actual_return_pct']))<1e-9
model=json.loads((ROOT/'data/july_model_frozen.json').read_text())
assert model['artifact_sha256']==sha(ROOT/'july_predict.py')
assert model['specification_sha256']==sha(ROOT/'data/july_model_v1.json')

redacted=[]
for path in sorted((ROOT/'evidence').glob('jb5_*.json')):
 text=path.read_text();before=sha(path)
 pattern=r'([?&](?:amp;)?X-Amz-[A-Za-z-]+=)[^&\s)"<>\\]+'
 sanitized=re.sub(pattern,lambda m:m[1]+'REDACTED',text,flags=re.I)
 if sanitized!=text:
  path.write_text(sanitized)
  redacted.append(dict(file=str(path.relative_to(ROOT)),original_sha256=before,published_sha256=sha(path)))
 assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',sanitized),path.name
if redacted:
 path=ROOT/'PUBLICATION_NOTES.json';notes=json.loads(path.read_text())
 notes['sanitized_files']+=redacted;save(path,notes)
from prepare_july import texts,ranking
no_trade=texts(ROOT/'evidence/jb5_hist5078_page2.json')
assert re.search(r'2026/07/21\s*\|\s*0\s*\|\s*0\s*\|\s*0\s*\|\s*0\s*\|\s*-\s*\|\s*-\s*\|\s*0',no_trade)
assert sum(row['price_status']=='no_regular_trade' for row in rows)==1
assert sum(bool(row['actual_rank']) for row in rows)==5
assert summary['exact_rank_hits']==1
baseline=json.loads((ROOT/'results/july_batch05_baseline.json').read_text())
assert [r['hits'] for r in baseline['days']]==[3,3,2]
for code,prev,close in [('6573',25,27),('1827',1228,1325)]:
 text=texts(ROOT/f'evidence/jb5_verify17_{code}.json')
 for date,value in [('2026/07/16',prev),('2026/07/17',close)]:
  match=re.search(date+r'\s*\|\s*[\d,]+\s*\|\s*[\d,]+\s*\|\s*[\d,]+\s*\|\s*([\d,]+)',text)
  assert match and float(match[1].replace(',',''))==value
assert len(ranking(texts(ROOT/'evidence/jb5_actual21_complete.json')))==174
save(ROOT/'results/july_batch05_audit.json',dict(old_manifest_file_checks=old,parsed_json_count=len(alljson),frozen_code_sha256=model['artifact_sha256'],frozen_model_sha256=model['specification_sha256'],days=checks,all_30_actual_statuses_verified=True,traded_close_count=29,no_regular_trade_count=1,old_seals_unchanged=True,full_tse_universe=False,blind_test=False,new_evidence_secret_pattern_scan='passed',source_retrieval_notes=['原開示のYahoo403はJPX転載で補完。','インフキュリオン・岩井コスモは対象日OHLC表の検索保存版で補完。','7/17実績別表のETF/ETNを除外し6573・1827は日付付き時系列を照合。SHIFT別表の整数丸めは採用しない。','5078の7/21は立会出来高0。0円終値・0%リターンを作らずnull。','7/21価格表の取得窓は7/22入力・封印前に補完し174普通株を確認。','5074探索中に8/14契約中止見出しが偶発表示。予測入力から除外したが非盲検。'],next_days=['2026-07-23','2026-07-24','2026-07-27']))
print(json.dumps(dict(old_manifest_file_checks=old,json_count=len(alljson),days=checks,new_redactions=len(redacted),traded_closes=29,no_regular_trade=1),ensure_ascii=False))
