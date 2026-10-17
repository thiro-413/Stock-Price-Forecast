"""Audit immutable inputs, score components, price arithmetic and corroboration."""
import csv,hashlib,json,re
from datetime import datetime,timezone
from prepare_july import ROOT,save,texts,ranking
from research import digest,gate,trading_days
from finalize_july_batch07 import DAYS,PRIOR,EXPECTED,RANK_FILES,SECOND_FILES,EXTRA,historical,manifest

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
 old=0
 for number in range(1,7):
  m=json.loads((ROOT/f'results/july_batch{number:02d}_manifest.json').read_text())
  for name,value in m['files'].items():assert sha(ROOT/name)==value,(number,name)
  old+=len(m['files'])
 for p in ROOT.rglob('*.json'):json.loads(p.read_text())
 frozen=json.loads((ROOT/'data/july_model_frozen.json').read_text())
 assert sha(ROOT/'july_predict.py')==frozen['artifact_sha256']
 assert sha(ROOT/'data/july_model_v1.json')==frozen['specification_sha256']
 checks=[]
 for day,prev in zip(DAYS,PRIOR):
  pred=json.loads((ROOT/f'results/july_predictions/{day}.json').read_text());scores=json.loads((ROOT/f'results/july_scores/{day}.json').read_text());inp=json.loads((ROOT/f'data/july_inputs/{day}.json').read_text())
  assert digest(pred['payload'])==pred['sha256']
  assert sha(ROOT/f'data/july_inputs/{day}.json')==pred['input_sha256']==scores['input_sha256']
  assert scores['candidates'][:10]==pred['payload']['predictions']
  assert not gate(pred['payload']['evidence'],day+'T08:30:00+09:00')['rejected']
  today=(trading_days(6)+trading_days(7)).index(day)
  for r in scores['candidates']:
   momentum=0 if r['previous_return_pct'] is None else max(-2,min(3,r['previous_return_pct']/10))
   material=0
   for ev in r['events']:
    age=today-(trading_days(6)+trading_days(7)).index(ev['first_eligible_session']);assert age>=0
    material=max(material,frozen['features']['material_base'].get(ev['type'],0)*(1 if age==0 else .5 if age in (1,2) else 0))
   assert material==r['components']['material'] and momentum==r['components']['momentum']
   assert abs(sum(r['components'].values())-r['score'])<1e-7
  actual=json.loads((ROOT/f'data/july_actuals/{day}.json').read_text());ev=json.loads((ROOT/f'results/july_evaluations/{day}.json').read_text())
  assert [r['code'] for r in actual['top10']]==EXPECTED[DAYS.index(day)]
  selected={r['code'] for r in pred['payload']['predictions']};winners={r['code'] for r in actual['top10']}
  assert ev['hits']==len(selected&winners)
  assert {r['code'] for r in ev['missed_winners']}==winners-selected
  for r in ev['predictions']:
   assert r['actual_close']>0 and r['previous_close']>0 and r['price_status']=='traded_close'
   assert abs(100*(r['actual_close']/r['previous_close']-1)-r['actual_return_pct'])<1e-9
   assert (r['actual_rank'] is not None)==(r['code'] in winners)
  checks.append(dict(date=day,seal=pred['sha256'],input_sha256=pred['input_sha256'],cutoff_gate='passed',candidate_count=len(scores['candidates']),unverified_exclusions=len(scores['rejected_candidates']),hits=ev['hits'],traded_closes=10))
 # Independently corroborate top-ten prices and changes, excluding non-TSE instruments.
 for i,day in enumerate(DAYS):
  sec=texts(ROOT/'evidence'/SECOND_FILES[i]).split('#### 値下がり率上位')[0]
  quotes={}
  for m in re.finditer(r'L\d+: \d+\s*\|\s*([0-9A-Z]{4})\s*\|\s*[^|]+\|\s*([\d,.]+)\s*\|\s*([+\-\d,.]+)\s*\|',sec):quotes[m[1]]=(float(m[2].replace(',','')),float(m[3].replace(',','')))
  for c in EXTRA[i]:
   h=historical(c);quotes[c]=(h[day]['close'],h[day]['close']-h[PRIOR[i]]['close'])
  actual=json.loads((ROOT/f'data/july_actuals/{day}.json').read_text())
  for r in actual['top10']:
   q=quotes[r['code']];assert abs(q[0]-r['close'])<1e-8 and abs(q[1]-r['change'])<1e-8,(day,r['code'],q)
 assert [len(ranking(texts(ROOT/'evidence'/f))) for f in RANK_FILES]==[22,92,59]
 summary=json.loads((ROOT/'results/july_batch07_summary.json').read_text())
 assert [x['hits'] for x in checks]==[1,2,0]
 assert summary['hits']==3 and summary['cumulative_hits']==26 and summary['cumulative_prediction_count']==210
 rows=list(csv.DictReader((ROOT/'results/july_batch07_predictions.csv').open(encoding='utf-8-sig')));assert len(rows)==30
 assert sum(bool(r['actual_rank']) for r in rows)==3
 baseline=json.loads((ROOT/'results/july_batch07_baseline.json').read_text());assert [r['hits'] for r in baseline['days']]==[1,1,1]
 chat=json.loads((ROOT/'results/chat_handoff_state.json').read_text());assert chat['completed_batches_in_chat']==2 and chat['next_authorized_batch']==[]
 state=json.loads((ROOT/'results/state.json').read_text());assert state['next_days']==['2026-07-31'] and state['requires_user_continue'] and len(state['july_completed_days'])==21
 for day,file in zip(DAYS,['jb7_afterseal28_search.json','jb7_actual29.json','jb7_actual30.json']):
  assert (ROOT/f'results/july_predictions/{day}.json').stat().st_mtime<(ROOT/'evidence'/file).stat().st_mtime
 # Check independent event ages for the two different 4888 announcements.
 for day in DAYS[1:]:
  x=json.loads((ROOT/f'data/july_inputs/{day}.json').read_text());r=next((v for v in x['candidates'] if v['code']=='4888'),None)
  if r is None:continue
  assert {(e['type'],e['first_eligible_session']) for e in r['events']}=={('contract','2026-07-28'),('jv_mou','2026-07-29')}
 # Publication filtering applies only to the new evidence; old manifests remain immutable.
 redactions=[];ledger=[]
 for p in sorted((ROOT/'evidence').glob('jb7_*.json')):
  original=p.read_text();before=sha(p)
  clean=re.sub(r'([?&](?:amp;)?X-Amz-[A-Za-z-]+=)[^&\s)"<>\\]+',lambda m:m[1]+'REDACTED',original,flags=re.I)
  if clean!=original:
   p.write_text(clean);redactions.append(dict(file=str(p.relative_to(ROOT)),original_sha256=before,published_sha256=sha(p)))
  assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',clean),p.name
  ledger.append(dict(file=str(p.relative_to(ROOT)),saved_at_utc=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),sha256=sha(p)))
 if redactions:
  p=ROOT/'PUBLICATION_NOTES.json';notes=json.loads(p.read_text());notes['sanitized_files']+=redactions;save(p,notes)
 save(ROOT/'results/july_batch07_acquisition_ledger.json',dict(note='保存時刻はツール取得直後のファイルmtime。掲載日時と区別。第三者による事前予測証明ではない。',files=ledger))
 save(ROOT/'results/july_batch07_audit.json',dict(old_manifest_file_checks=old,old_seals_unchanged=True,days=checks,all_30_actual_statuses_verified=True,traded_close_count=30,no_regular_trade_count=0,top10_corroborated_each_day=10,frozen_code_sha256=frozen['artifact_sha256'],frozen_model_sha256=frozen['specification_sha256'],full_tse_universe=False,blind_test=False,new_evidence_secret_pattern_scan='passed',new_redactions=len(redactions),notes=['原資料の公表日と取得日を区別。7102画像PDFと6042文字化けを原PDF画像で確認。6501はJPX転載で照合。','7/28別表の名証3260とETF1366/1357、7/29のETN2034を除外。不足は時系列で照合、SHIFTは小数原値を使用。','28日封印後の検索で29日結果の偶発表示あり。入力不採用だが非盲検。','4888の独立した研究契約と基本合意を別証拠・別鮮度で保持。','2311と6663の予想修正混在には固定ルールの-4を併用。'],next_days=summary['next_days']))
 manifest();print(json.dumps(dict(old_manifest_file_checks=old,days=checks,all_30_traded_closes_verified=True,new_redactions=len(redactions)),ensure_ascii=False))

if __name__=='__main__':run()
