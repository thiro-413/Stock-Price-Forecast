"""Audit immutable inputs, score components, price arithmetic and corroboration."""
import csv,hashlib,json,re
from datetime import datetime,timezone
from prepare_july import ROOT,save,texts,ranking
from research import digest,gate,trading_days
from finalize_july_batch06 import DAYS,PRIOR,EXPECTED,RANK_FILES,manifest

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
 old=0
 for number in range(1,6):
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
 second_files=['jb6_secondary23.json','jb6_secondary24.json','jb6_secondary27_final.json']
 extra=[['4890'],['4564'],['4833','6330','7819']]
 for i,day in enumerate(DAYS):
  sec=texts(ROOT/'evidence'/second_files[i]).split('#### 値下がり率上位')[0]
  quotes={}
  for m in re.finditer(r'L\d+: \d+\s*\|\s*([0-9A-Z]{4})\s*\|\s*[^|]+\|\s*([\d,.]+)\s*\|\s*([+\-\d,.]+)\s*\|',sec):quotes[m[1]]=(float(m[2].replace(',','')),float(m[3].replace(',','')))
  for c in extra[i]:
   name='jb6_verify4833_9478.json' if c=='4833' else f'jb6_verify_{c}.json';t=texts(ROOT/'evidence'/name)
   values={}
   for date in [day,PRIOR[i]]:
    m=re.search(date.replace('-','/')+r'\s*\|\s*[\d,]+\s*\|\s*[\d,]+\s*\|\s*[\d,]+\s*\|\s*([\d,]+)',t);assert m,(c,date)
    values[date]=float(m[1].replace(',',''))
   quotes[c]=(values[day],values[day]-values[PRIOR[i]])
  actual=json.loads((ROOT/f'data/july_actuals/{day}.json').read_text())
  for r in actual['top10']:
   assert quotes[r['code']]==(r['close'],r['change']),(day,r['code'],quotes.get(r['code']))
 # Check explanatory errata change no numerical model fields.
 x=json.loads((ROOT/'data/july_inputs/2026-07-24.json').read_text());y=json.loads((ROOT/'data/july_inputs/2026-07-27.json').read_text())
 assert len(json.loads((ROOT/'data/july_batch06_annotation_errata.json').read_text())['corrections'])==2
 assert '3300→6040' in next(v for v in y['evidence'] if v['id']=='release_6999_2026-07-24')['timestamp_evidence']
 assert len(ranking(texts(ROOT/'evidence/jb6_actual27_combined.json')))==146
 summary=json.loads((ROOT/'results/july_batch06_summary.json').read_text())
 assert [x['hits'] for x in checks]==[3,1,0]
 assert summary['hits']==4 and summary['cumulative_hits']==23 and summary['cumulative_prediction_count']==180
 rows=list(csv.DictReader((ROOT/'results/july_batch06_predictions.csv').open(encoding='utf-8-sig')));assert len(rows)==30
 assert sum(bool(r['actual_rank']) for r in rows)==4
 baseline=json.loads((ROOT/'results/july_batch06_baseline.json').read_text());assert [r['hits'] for r in baseline['days']]==[1,3,2]
 # Publication filtering applies only to the new evidence; old manifests remain immutable.
 redactions=[];ledger=[]
 for p in sorted((ROOT/'evidence').glob('jb6_*.json')):
  original=p.read_text();before=sha(p)
  clean=re.sub(r'([?&](?:amp;)?X-Amz-[A-Za-z-]+=)[^&\s)"<>\\]+',lambda m:m[1]+'REDACTED',original,flags=re.I)
  if clean!=original:
   p.write_text(clean);redactions.append(dict(file=str(p.relative_to(ROOT)),original_sha256=before,published_sha256=sha(p)))
  assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',clean),p.name
  ledger.append(dict(file=str(p.relative_to(ROOT)),saved_at_utc=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),sha256=sha(p)))
 if redactions:
  p=ROOT/'PUBLICATION_NOTES.json';notes=json.loads(p.read_text());notes['sanitized_files']+=redactions;save(p,notes)
 save(ROOT/'results/july_batch06_acquisition_ledger.json',dict(note='保存時刻はツール取得直後のファイルmtime。掲載日時と区別。第三者による事前予測証明ではない。',files=ledger))
 save(ROOT/'results/july_batch06_audit.json',dict(old_manifest_file_checks=old,old_seals_unchanged=True,days=checks,all_30_actual_statuses_verified=True,traded_close_count=30,no_regular_trade_count=0,top10_corroborated_each_day=10,frozen_code_sha256=frozen['artifact_sha256'],frozen_model_sha256=frozen['specification_sha256'],annotation_errata_count=2,annotation_score_impact=0,full_tse_universe=False,blind_test=False,new_evidence_secret_pattern_scan='passed',new_redactions=len(redactions),notes=['一部の多重open後の参照ID解決で別資料やエラーを取得。該当試行は保存し、不適合資料を入力に不使用。各採用資料を単独取得し社名・日付・本文を確認。','23日別表の福証3047、24日名証3260、27日名証3260・福証3047・ETN2050を除外。不足は日付付き時系列で照合。','27日原表150行・普通株146行へ取得窓を補完。','9478は当日終値532円・前日552円をTraders/みずほ証券の日付付き検索保存データで確認。','7175・8707の既知速報と同一利益値は初回適格日を維持。','6999・3242の説明文転記誤りを別紙訂正、封印済み入力は保持。'],next_days=summary['next_days']))
 manifest();print(json.dumps(dict(old_manifest_file_checks=old,days=checks,all_30_traded_closes_verified=True,new_redactions=len(redactions)),ensure_ascii=False))

if __name__=='__main__':run()
