"""Verify the final July session and the complete monthly aggregation."""
import csv,hashlib,json,re
from datetime import datetime,timezone
from prepare_july import ROOT,save,texts,ranking
from research import digest,gate,trading_days
from finalize_july_batch08 import DAY,PRIOR,EXPECTED,RANK_FILE,NEXT,historical,manifest

def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
 old=0
 for n in range(1,8):
  m=read(f'results/july_batch{n:02d}_manifest.json')
  for p,h in m['files'].items():assert sha(ROOT/p)==h,(n,p)
  old+=len(m['files'])
 for p in ROOT.rglob('*.json'):json.loads(p.read_text())
 frozen=read('data/july_model_frozen.json')
 assert sha(ROOT/'july_predict.py')==frozen['artifact_sha256']
 assert sha(ROOT/'data/july_model_v1.json')==frozen['specification_sha256']
 days=trading_days(7);calendar=trading_days(6)+days
 for day in days:
  pred=read(f'results/july_predictions/{day}.json')
  assert digest(pred['payload'])==pred['sha256']
  assert sha(ROOT/f'data/july_inputs/{day}.json')==pred['input_sha256']
 pred=read(f'results/july_predictions/{DAY}.json');scores=read(f'results/july_scores/{DAY}.json');inp=read(f'data/july_inputs/{DAY}.json')
 assert scores['input_sha256']==pred['input_sha256']
 assert scores['candidates'][:10]==pred['payload']['predictions']
 assert not gate(pred['payload']['evidence'],DAY+'T08:30:00+09:00')['rejected']
 assert (len(scores['candidates']),len(scores['rejected_candidates']))==(98,9)
 source={r['code']:r for r in inp['candidates']}
 for r in scores['candidates']:
  raw=source[r['code']];ret=raw.get('previous_return_pct');material=0
  for e in r['events']:
   age=calendar.index(DAY)-calendar.index(e['first_eligible_session']);assert age>=0
   material=max(material,frozen['features']['material_base'].get(e['type'],0)*(1 if age==0 else .5 if age in (1,2) else 0))
  components=dict(material=material,momentum=0 if ret is None else max(-2,min(3,ret/10)),market=int(raw['market'] in ('S','G')),dilution=-int(bool(raw.get('dilution'))),negative=-4*int(bool(raw.get('negative_material'))),margin=-int(bool(raw.get('margin_restriction'))))
  assert components==r['components'] and round(sum(components.values()),8)==r['score']
 assert scores['candidates']==sorted(scores['candidates'],key=lambda r:(-r['score'],-(r['previous_return_pct'] if r['previous_return_pct'] is not None else -999),r['code']))
 for c in ['1382','5103']:assert next(r for r in scores['candidates'] if r['code']==c)['components']['negative']==-4
 check=read('data/july_batch08_comparison_checks.json');assert check['299A']['ordinary_profit_million_yen']==[745,910]
 q=check['7148'];assert q['current_q3']==q['current_ytd_3q']-q['current_ytd_2q']==5763 and q['previous_q3']==q['previous_ytd_3q']-q['previous_ytd_2q']==4358
 actual=read(f'data/july_actuals/{DAY}.json')['top10'];assert [r['code'] for r in actual]==EXPECTED
 ev=read(f'results/july_evaluations/{DAY}.json');assert ev['hits']==1 and ev['exact_rank_hits']==0
 assert {r['code'] for r in ev['missed_winners']}==set(EXPECTED)-{'6912'}
 for r in ev['predictions']:
  h=historical(r['code']);assert h[DAY]['volume']>0
  assert r['actual_close']==h[DAY]['close'] and r['previous_close']==h[PRIOR]['close']
  assert abs(100*(r['actual_close']/r['previous_close']-1)-r['actual_return_pct'])<1e-9
  assert (r['actual_rank'] is not None)==(r['code']=='6912') and r['price_status']=='traded_close'
 sec=texts(ROOT/'evidence/jb8_secondary31.json').split('#### 値下がり率上位')[0];quotes={}
 for m in re.finditer(r'L\d+: \d+\s*\|\s*([0-9A-Z]{4})\s*\|\s*[^|]+\|\s*([\d,.]+)\s*\|\s*([+\-\d,.]+)\s*\|',sec):quotes[m[1]]=(float(m[2].replace(',','')),float(m[3].replace(',','')))
 h=historical('6997');quotes['6997']=(h[DAY]['close'],h[DAY]['close']-h[PRIOR]['close'])
 for r in actual:assert quotes[r['code']]==(r['close'],r['change'])
 rank=ranking(texts(ROOT/'evidence'/RANK_FILE));assert len(rank)==330
 for r in rank:assert abs(100*r['change']/(r['close']-r['change'])-r['return_pct'])<.011
 assert (ROOT/f'results/july_predictions/{DAY}.json').stat().st_mtime<(ROOT/'evidence/jb8_actual31.json').stat().st_mtime
 month=read('results/july_month_summary.json');baseline=read('results/july_month_baseline.json')
 assert month['days']==days and month['prediction_count']==220 and month['hits']==27 and month['outside_top10']==193
 assert month['traded_close_count']==219 and month['no_regular_trade_count']==1 and not month['error_analysis_started']
 prior=[r for r in read('results/batch08_data.json') if r['date']=='2026-06-30'];prior.sort(key=lambda r:int(r['rank']))
 for day,b,d in zip(days,baseline['days'],month['daily']):
  a=read(f'data/july_actuals/{day}.json')['top10'];e=read(f'results/july_evaluations/{day}.json')
  assert b['predictions']==[r['code'] for r in prior] and b['hit_codes']==sorted({r['code'] for r in prior}&{r['code'] for r in a})
  assert b['hits']==len(b['hit_codes'])==d['baseline_hits'] and d['hits']==e['hits'] and d['exact_rank_hits']==e['exact_rank_hits'];prior=a
 assert month['baseline_hits']==baseline['hits']==sum(d['hits'] for d in baseline['days'])
 for n in range(3,9):
  for b in read(f'results/july_batch{n:02d}_baseline.json')['days']:
   assert b['hits']==next(x['hits'] for x in baseline['days'] if x['date']==b['date'])
 rows=list(csv.DictReader((ROOT/'results/july_month_predictions.csv').open(encoding='utf-8-sig')))
 assert len(rows)==220 and sum(bool(r['actual_rank']) for r in rows)==27
 missing=[r for r in rows if r['price_status']=='no_regular_trade'];assert len(missing)==1 and missing[0]['code']=='5078' and missing[0]['actual_close']==missing[0]['actual_return_pct']==''
 state=read('results/state.json');chat=read('results/chat_handoff_state.json')
 assert state['next_days']==NEXT and state['requires_user_continue'] and state['july_prediction_complete'] and not state['error_analysis_started']
 assert chat['completed_batches_in_chat']==3 and chat['next_authorized_batch']==[]
 redactions=[];ledger=[]
 for p in sorted((ROOT/'evidence').glob('jb8_*.json')):
  original=p.read_text();before=sha(p)
  clean=re.sub(r'([?&](?:amp;)?X-Amz-[A-Za-z-]+=)[^&\s)"<>\\]+',lambda m:m[1]+'REDACTED',original,flags=re.I)
  if clean!=original:
   p.write_text(clean);redactions.append(dict(file=str(p.relative_to(ROOT)),original_sha256=before,published_sha256=sha(p)))
  assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',clean),p.name
  ledger.append(dict(file=str(p.relative_to(ROOT)),saved_at_utc=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),sha256=sha(p)))
 if redactions:
  notes=read('PUBLICATION_NOTES.json');notes['sanitized_files']+=redactions;save(ROOT/'PUBLICATION_NOTES.json',notes)
 save(ROOT/'results/july_batch08_acquisition_ledger.json',dict(note='保存時刻は取得直後のファイルmtimeで、公表日時とは異なる。第三者による事前予測証明ではない。',files=ledger))
 audit=dict(old_manifest_file_checks=old,old_seals_unchanged=True,seal=pred['sha256'],input_sha256=pred['input_sha256'],cutoff_gate='passed',candidate_count=98,unverified_exclusions=9,all_score_components_verified=True,hits=1,exact_rank_hits=0,all_10_traded_closes_verified=True,top10_corroborated=10,ordinary_ranking_rows=330,month_sessions=22,month_predictions=220,month_hits=27,month_baseline_hits=baseline['hits'],month_traded_close_count=219,month_no_regular_trade_count=1,full_tse_universe=False,blind_test=False,new_evidence_secret_pattern_scan='passed',new_redactions=len(redactions),next_days=NEXT)
 save(ROOT/'results/july_batch08_audit.json',audit);manifest();print(json.dumps(audit,ensure_ascii=False))

if __name__=='__main__':run()
