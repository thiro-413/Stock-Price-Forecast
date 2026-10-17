"""Audit diagnostic coverage, original seals, timestamps, and publication files."""
import csv,json,re
from collections import Counter
from datetime import datetime,timezone
from prepare_july import ROOT,save,texts
from research import digest,gate,trading_days
from analyze_july_errors01 import DAYS,NEXT,read,sha

def run():
 old=0
 for n in range(1,9):
  m=read(f'results/july_batch{n:02d}_manifest.json')
  for name,h in m['files'].items():assert sha(ROOT/name)==h,(n,name)
  old+=len(m['files'])
 for p in ROOT.rglob('*.json'):json.loads(p.read_text())
 for day in trading_days(7):
  pred=read(f'results/july_predictions/{day}.json')
  assert digest(pred['payload'])==pred['sha256']
  assert sha(ROOT/f'data/july_inputs/{day}.json')==pred['input_sha256']
  assert not gate(pred['payload']['evidence'],day+'T08:30:00+09:00')['rejected']
 summary=read('results/july_error_batch01_summary.json');records=read('results/july_error_batch01_cases.json')['records'];src=read('results/july_error_batch01_sources.json')['sources']
 assert len(records)==60 and len({(r['date'],r['role'],r['code']) for r in records})==60
 assert Counter(r['status'] for r in records)=={'false_positive':26,'false_negative':26,'hit':8}
 count=Counter();directions=Counter();candidate_winners=0
 for day in DAYS:
  pred=read(f'results/july_predictions/{day}.json')['payload']['predictions'];ev=read(f'results/july_evaluations/{day}.json');actual=read(f'data/july_actuals/{day}.json')['top10'];s=read(f'results/july_scores/{day}.json');lookup={r['code']:(i+1,r) for i,r in enumerate(s['candidates'])};rr=[r for r in records if r['date']==day];pp=[r for r in rr if r['role']=='prediction'];aa=[r for r in rr if r['role']=='actual_top10']
  assert [r['code'] for r in pp]==[r['code'] for r in pred]
  assert [r['code'] for r in aa]==[r['code'] for r in actual]
  for r,p in zip(pp,ev['predictions']):
   c=lookup[r['code']][1];assert r['score']==c['score'] and r['components']==c['components'] and r['previous_return_pct']==c['previous_return_pct']
   assert r['actual_rank']==p['actual_rank'] and r['actual_return_pct']==p['actual_return_pct']
   assert abs(100*(p['actual_close']/p['previous_close']-1)-r['actual_return_pct'])<1e-9
   if r['status']=='false_positive':assert r['actual_rank'] is None;directions['up' if r['actual_return_pct']>0 else 'flat' if r['actual_return_pct']==0 else 'down']+=1
  for r,a in zip(aa,actual):
   assert r['actual_return_pct']==a['return_pct'] and abs(100*(a['close']/a['previous_close']-1)-a['return_pct'])<1e-9
   if r['code'] in lookup:
    rank,c=lookup[r['code']];assert r['candidate_rank']==rank and r['score']==c['score'] and r['components']==c['components'];candidate_winners+=1
   else:assert r['candidate_rank'] is None and r['score'] is None
   if r['status']=='false_negative':count[r['selection_stage']]+=1
  d=next(x for x in summary['daily'] if x['date']==day)
  assert d['eligible_winners']==sum(r['code'] in lookup for r in actual)
  assert d['hits']==sum(r['status']=='hit' for r in pp)
  assert d['top10_return_boundary_pct']==min(r['return_pct'] for r in actual)
  assert sum(r['missing_momentum'] for r in pp)==d['missing_momentum_in_predictions']
 for r in records:
  assert r['observation'] and r['hypothesis'] and r['economic_cause_status']=='not_identified'
  assert r['timing_applies_to_event_only']
  for p in r['evidence_files']:assert (ROOT/p).is_file(),p
  for k in r['source_ids']:assert k in src
 assert count==summary['missed_winner_stages']=={'eligible_below_top10':11,'absent_from_union':15}
 assert candidate_winners==summary['eligible_winners']==15 and summary['candidate_recall']==.5
 assert directions=={'up':12,'flat':1,'down':13}
 for k,s in src.items():assert (ROOT/s['file']).is_file(),k
 # Check the evidence actually contains the decisive identities, facts and times.
 assert '4833' in texts(ROOT/src['digest01']['file'])
 assert '2492' in texts(ROOT/src['digest03']['file'])
 assert '172' in texts(ROOT/src['def']['file']) and '2,513' in texts(ROOT/src['def']['file'])
 assert '7/1 15:00' in texts(ROOT/'evidence/je1_crg_index.json')
 assert '2026年6月30日 18時00分' in texts(ROOT/src['reyuu']['file'])
 assert '2026年7月2日 07時30分' in texts(ROOT/src['taiyo']['file'])
 assert '2026年7月2日 12時00分' in texts(ROOT/src['liberta']['file']) and '2026年5月' in texts(ROOT/src['liberta']['file'])
 assert '2026/07/02 16:01' in texts(ROOT/src['oasis']['file'])
 assert 'Zeo Next' in texts(ROOT/src['nakamura']['file']) and '業績に与える影響は軽微' in texts(ROOT/src['nakamura']['file'])
 calendar=trading_days(6)+trading_days(7);assert calendar.index('2026-07-03')-calendar.index('2026-06-29')==4
 for r in records:
  if r['identified_event_timing'] not in ['known_before_cutoff','after_cutoff']:continue
  stamps=[src[k]['published_at'] for k in r['source_ids'] if src[k]['published_at'] and 'T' in src[k]['published_at']]
  if not stamps:continue
  cutoff=datetime.fromisoformat(r['date']+'T08:30:00+09:00')
  if r['identified_event_timing']=='known_before_cutoff':assert all(datetime.fromisoformat(t)<=cutoff for t in stamps)
  else:assert any(datetime.fromisoformat(t)>cutoff for t in stamps)
 csvpath=ROOT/'results/july_error_batch01_cases.csv';assert csvpath.read_bytes().startswith(b'\xef\xbb\xbf') and b'\r\n' not in csvpath.read_bytes()
 csvrows=list(csv.DictReader(csvpath.open(encoding='utf-8-sig')));assert len(csvrows)==60
 for row,r in zip(csvrows,records):assert row['date']==r['date'] and row['role']==r['role'] and row['code']==r['code'] and row['observation']==r['observation']
 report=(ROOT/'results/july_error_batch01_report.md').read_text();assert '候補内11件・候補不在15件' in report and '15/30（50.00%）' in report
 state=read('results/state.json');chat=read('results/chat_handoff_state.json')
 assert state['next_days']==NEXT and state['requires_user_continue'] and state['error_analysis_completed_days']==DAYS and state['error_analysis_completed_batch']==1
 assert state['error_analysis_started'] and not state['screening_prompt_created'] and state['july_prediction_complete']
 assert chat['completed_batches_in_chat']==4 and len(chat['completed_batch_ids_in_chat'])==4 and not chat['next_authorized_batch']
 redactions=[];ledger=[]
 for p in sorted((ROOT/'evidence').glob('je1_*.json')):
  original=p.read_text();before=sha(p);clean=re.sub(r'([?&](?:amp;)?X-Amz-[A-Za-z-]+=)[^&\s)"<>\\]+',lambda m:m[1]+'REDACTED',original,flags=re.I)
  if clean!=original:
   p.write_text(clean);redactions.append(dict(file=str(p.relative_to(ROOT)),original_sha256=before,published_sha256=sha(p)))
  assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',clean),p.name
  ledger.append(dict(file=str(p.relative_to(ROOT)),saved_at_utc=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),sha256=sha(p)))
 if redactions:
  notes=read('PUBLICATION_NOTES.json');notes['sanitized_files']+=redactions;save(ROOT/'PUBLICATION_NOTES.json',notes)
 save(ROOT/'results/july_error_batch01_acquisition_ledger.json',dict(note='ファイル保存時刻。原公表時刻・ツール実行の厳密な取得時刻とは異なる。分析用の事後取得で第三者による事前予測証明ではない。',files=ledger))
 audit=dict(old_manifest_file_checks=old,all_22_seals_and_inputs_unchanged=True,original_model_and_month_summary_unchanged=True,days=DAYS,role_records=60,false_positive_count=26,false_negative_count=26,hits=4,eligible_winners=15,missed_eligible=11,missed_absent=15,all_original_prices_and_components_matched=True,decisive_event_timing_checks='passed',source_paths_and_csv_checks='passed',causal_attribution_proven=False,secret_pattern_scan='passed',redactions_this_run=len(redactions),next_days=NEXT)
 save(ROOT/'results/july_error_batch01_audit.json',audit)
 paths=[ROOT/'analyze_july_errors01.py',ROOT/'audit_july_errors01.py']+sorted((ROOT/'evidence').glob('je1_*.json'))+sorted((ROOT/'results').glob('july_error_batch01_*'))
 paths=[p for p in paths if p.name!='july_error_batch01_manifest.json']
 save(ROOT/'results/july_error_batch01_manifest.json',dict(created_at_utc=datetime.now(timezone.utc).isoformat(),files={str(p.relative_to(ROOT)):sha(p) for p in paths}))
 print(json.dumps(audit,ensure_ascii=False))

if __name__=='__main__':run()
