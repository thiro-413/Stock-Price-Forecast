"""Validate immutable predictions and batch4 prices before publication."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
from prepare_july import ROOT,save
from research import gate,digest,trading_days

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

old=0
for number in range(1,4):
 manifest=json.loads((ROOT/f'results/july_batch{number:02d}_manifest.json').read_text())
 for name,value in manifest['files'].items():assert sha(ROOT/name)==value,(number,name)
 old+=len(manifest['files'])
alljson=list(ROOT.rglob('*.json'))
for path in alljson:json.loads(path.read_text())
assert len(trading_days(7))==22
summary=json.loads((ROOT/'results/july_batch04_summary.json').read_text())
assert summary['hits']==3 and summary['cumulative_hits']==14
checks=[]
for suffix in ['14','15','16']:
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
 checks.append(dict(date=day,sealed_sha256=pred['sha256'],cutoff_gate='passed',input_hash='passed',candidate_count=len(scores['candidates']),unverified_exclusions=len(scores['rejected_candidates']),hits=summary['evaluations'][len(checks)]['hits'],actual_price_count=10))
rows=list(csv.DictReader((ROOT/'results/july_batch04_predictions.csv').open(encoding='utf-8-sig')))
assert len(rows)==30
for row in rows:
 assert abs(100*(float(row['actual_close'])/float(row['previous_close'])-1)-float(row['actual_return_pct']))<1e-9
model=json.loads((ROOT/'data/july_model_frozen.json').read_text())
assert model['artifact_sha256']==sha(ROOT/'july_predict.py')
assert model['specification_sha256']==sha(ROOT/'data/july_model_v1.json')

redacted=[]
for path in sorted((ROOT/'evidence').glob('jb4_*.json')):
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
save(ROOT/'results/july_batch04_audit.json',dict(old_manifest_file_checks=old,parsed_json_count=len(alljson),frozen_code_sha256=model['artifact_sha256'],frozen_model_sha256=model['specification_sha256'],days=checks,all_30_prices_verified=True,old_seals_unchanged=True,full_tse_universe=False,blind_test=False,new_evidence_secret_pattern_scan='passed',source_retrieval_notes=['Yahoo PDF403はJPX転載で補完。東京衡機は会社公開PDFで補完。','ソーバル・QPSHDの実績は日付付き検索保存版のOHLC列から補完、ジェーソンはTraders表と保存検索の前日行を照合。','7/14別表のETF600Aを除外、4819を別記事で照合。7/16福証9388を除外、7138を日付付き時系列で照合。','GO581A、ABEJA5574、セイワ523Aなど原資料を確認しきれなかったニュースのみ候補は除外。保存済み予測に遡及反映しない。','記事・短信の数値差（4616・7719など）は原資料優先、分類記録を保存。'],next_days=['2026-07-17','2026-07-21','2026-07-22']))
print(json.dumps(dict(old_manifest_file_checks=old,json_count=len(alljson),days=checks,new_redactions=len(redacted),all_30_prices=True),ensure_ascii=False))
