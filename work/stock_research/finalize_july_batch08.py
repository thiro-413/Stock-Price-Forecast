"""Evaluate the last sealed July prediction and aggregate all 22 sessions."""
import csv,hashlib,json,re
from datetime import datetime,timezone
from prepare_july import ROOT,save,texts,ranking
from research import digest,evaluate,gate,trading_days
DAY='2026-07-31';PRIOR='2026-07-30'
RANK_FILE='jb8_actual31_combined.json'
URL='https://kabu.kininew.net/fiveup/8104.html'
SECOND='https://uiblog.hatenablog.com/entry/2026/08/01/135734'
EXPECTED=['4052','2737','5367','4461','4220','4062','6912','6855','6752','6997']
NEXT=['2026-07-01','2026-07-02','2026-07-03']

def historical(code):
 path=ROOT/'evidence'/('jb8_hist_alt9709.json' if code=='9709' else f'jb8_hist_{code}.json');result={}
 for m in re.finditer(r'L\d+: (2026/07/(?:30|31))\s*\|\s*[\d,.]+\s*\|\s*[\d,.]+\s*\|\s*[\d,.]+\s*\|\s*([\d,.]+)\s*\|\s*([\d,]+)',texts(path)):
  result[m[1].replace('/','-')]={'close':float(m[2].replace(',','')),'volume':int(m[3].replace(',','')),'url':f'https://96ut.com/stock/jikei.php?code={code}'+('' if code=='9709' else '&year=2026'),'file':str(path.relative_to(ROOT))}
 return result

def write_csv(path,rows):
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def month():
 days=trading_days(7);rows=[];daily=[];base=[]
 prior=[r for r in json.loads((ROOT/'results/batch08_data.json').read_text()) if r['date']=='2026-06-30'];prior.sort(key=lambda r:int(r['rank']));assert len(prior)==10
 for day in days:
  ev=json.loads((ROOT/f'results/july_evaluations/{day}.json').read_text());actual=json.loads((ROOT/f'data/july_actuals/{day}.json').read_text())['top10']
  common=sorted({r['code'] for r in prior}&{r['code'] for r in actual});base.append(dict(date=day,predictions=[r['code'] for r in prior],hit_codes=common,hits=len(common)));prior=actual
  daily.append(dict(date=day,hits=ev['hits'],prediction_count=10,precision_at_10=ev['hits']/10,exact_rank_hits=ev['exact_rank_hits'],baseline_hits=len(common)))
  for r in ev['predictions']:
   row={k:r.get(k) for k in ['predicted_rank','code','name','score','material_types','previous_close','actual_close','actual_return_pct','actual_rank','result','missing_momentum','actual_source']}
   row['price_status']=r.get('price_status','traded_close' if r['actual_close'] is not None else 'unknown');rows.append(dict(date=day,**row))
 hits=sum(d['hits'] for d in daily);exact=sum(d['exact_rank_hits'] for d in daily);baseline=sum(d['baseline_hits'] for d in daily)
 summary=dict(period='2026-07',days=days,completed_sessions=len(days),prediction_count=len(rows),hits=hits,outside_top10=len(rows)-hits,precision_at_10=hits/len(rows),recall_at_10=hits/len(rows),exact_rank_hits=exact,baseline_rule='前営業日の東証普通株上昇率上位10継続。7/1の前日は検証済み6/30のbatch08_data.jsonを使用。',baseline_hits=baseline,baseline_prediction_count=len(rows),baseline_precision_at_10=baseline/len(rows),traded_close_count=sum(r['price_status']=='traded_close' for r in rows),no_regular_trade_count=sum(r['price_status']=='no_regular_trade' for r in rows),full_tse_universe=False,blind_test=False,error_analysis_started=False,screening_prompt_created=False,daily=daily,next_phase='july_error_analysis',next_days=NEXT)
 save(ROOT/'results/july_month_summary.json',summary);save(ROOT/'results/july_month_baseline.json',dict(rule=summary['baseline_rule'],days=base,hits=baseline,prediction_count=len(rows),precision_at_10=baseline/len(rows)))
 write_csv(ROOT/'results/july_month_predictions.csv',rows)
 report=['# 2026年7月：固定モデルによる22営業日の予測比較','',f'全{len(days)}営業日・{len(rows)}予測の比較を完了。上位10入りは**{hits}/{len(rows)}（{hits/len(rows):.2%}）**、上位10外{len(rows)-hits}件。同順位一致{exact}件。',f'前日上位10継続の比較基準は{baseline}/{len(rows)}（{baseline/len(rows):.2%}）。7/1用の6/30は6月最終回の検証済み普通株10件を利用し、7/2以降は保存済み前日実績を使用。',
 '全東証の完全母集団ではなく、前日5%以上表と取得ニュース掲載株からの部分母集団検証。原資料未照合のニュースのみ候補は除外。固定モデルは6月事例から作った定性的な規則であり、7月結果に合わせて変更していない。',
 '検索・動的一覧に将来情報が偶発表示された非盲検の過去再現。締切後の情報は予測入力へ採用していないが、厳密なルックアヘッド不存在を実証したものではない。',
 '実績上位10は第三者表と別表・時系列を照合したもの。全原票の独立再ソートは未達。上位10外の正確な全市場順位は記録していない。',
 f'約定終値を確認できたのは{summary["traded_close_count"]}件。7/21の5078は立会出来高0で約定終値なし、終値・騰落率はnull。0円・0%へ置き換えない。的中率と売買収益率は異なり、購入可能性・費用・寄付後収益は未検証。','',
 '|対象日|上位10的中|同順位一致|前日上位10継続|','|---|---:|---:|---:|']
 report += [f'|{d["date"]}|{d["hits"]}/10|{d["exact_rank_hits"]}|{d["baseline_hits"]}/10|' for d in daily]
 report += ['', '7/24の説明文転記誤りは既存のjuly_batch06_annotation_errata.jsonに保存されており、分類・スコア・順位への影響はない。封印済み入力を保持。',
 '最終日の資料照合で1382・5103の監理→整理移行を補完し、31日の既定減点へ反映した。取得漏れの発見を過去予測へ遡及反映しない。',
 '詳細な不的中原因分析は未着手。次の処理単位は7/1・2・3の分析で、ユーザーの続行回答を待つ。スクリーニング用プロンプトも未作成。','']
 (ROOT/'results/july_month_report.md').write_text('\n'.join(report));return summary

def manifest():
 paths=[ROOT/p for p in ['july_predict.py','data/july_model_v1.json','data/july_model_frozen.json','build_july_batch08.py','finalize_july_batch08.py','audit_july_batch08.py','data/july_batch08_comparison_checks.json']]
 paths+=sorted((ROOT/'evidence').glob('jb8_*.json'))+sorted((ROOT/'results').glob('july_batch08_*'))+sorted((ROOT/'results').glob('july_month_*'))
 paths=[p for p in paths if p.name!='july_batch08_manifest.json']
 paths += [ROOT/f'data/{g}/{DAY}.json' for g in ['july_inputs','july_actuals']]+[ROOT/f'results/{g}/{DAY}.json' for g in ['july_predictions','july_scores','july_evaluations']]+[ROOT/f'data/{g}_31.json' for g in ['july_events','july_releases']]
 save(ROOT/'results/july_batch08_manifest.json',{'created_at_utc':datetime.now(timezone.utc).isoformat(),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}})

def run():
 rows=ranking(texts(ROOT/'evidence'/RANK_FILE));rows.sort(key=lambda r:(-r['change']/(r['close']-r['change']),r['code']))
 assert [r['code'] for r in rows[:10]]==EXPECTED
 for r in rows:
  pct=100*r['change']/(r['close']-r['change']);assert abs(pct-r['return_pct'])<0.011
  r.update(reported_return_pct=r['return_pct'],return_pct=pct,previous_close=r['close']-r['change'],url=URL)
 actual={'date':DAY,'top10_verified':True,'verification_scope':'別集計表からETN2033を除外し、不足6997を7/30→31時系列で照合。全原票からの独立再ソートではない。','sources':[URL,SECOND,historical('6997')[DAY]['url']],'top10':rows[:10]};save(ROOT/f'data/july_actuals/{DAY}.json',actual)
 pred=json.loads((ROOT/f'results/july_predictions/{DAY}.json').read_text());assert digest(pred['payload'])==pred['sha256'];assert not gate(pred['payload']['evidence'],DAY+'T08:30:00+09:00')['rejected']
 ev=evaluate(pred,actual);lookup={r['code']:r for r in rows};allrows=[];scores=json.loads((ROOT/f'results/july_scores/{DAY}.json').read_text())
 report=['# 7月予測検証 第8回（最終1日）：2026年7月31日','',
 '各日08:30 JSTを仮定した過去再現の最終日。固定モデル・コード・過去21営業日分の入力/封印は変更せず、予測を封印してから31日実績を意図的に取得した。',
 '候補は前日5%以上表＋取得ニュース掲載普通株の部分集合で全東証を網羅しない。原資料未照合のニュースのみ候補は除外。板・PTS・長期OHLCV・浮動株・信用貸借・マクロの定量入力は不使用。欠損前日騰落率は採点0点だが0%とは扱わない。',
 '動的欄に31日09:03気配や検索結果に31日引け後の監理指定等が偶発表示。締切後の情報として入力には不採用。非盲検で厳密な将来情報遮断の実証ではない。',
 '夕方記事は訂正表題だが訂正時刻未確認。原資料と翌朝記事で材料を照合し、訂正後の記事を原資料の代用にしない。9709は経常15.2%増（記事17%）、4308は49.3%増（記事50%）を原資料優先とした。',
 '299Aは前年単体745百万円と当年連結910百万円との比較であり、同一連結範囲の22%成長とは解釈しない。7148は3Q累計減益だが、原中間短信との差から4-6月経常5763対4358百万円の増益を照合。',
 '6379の分割効力は10/1。7/31の価格には未適用で、配当は分割前換算117→118円で比較。4092の未定配当決定を無配からの復配と誤認しない。8174のYahoo503をJPX転載で補完。',
 '1382・5103の監理指定と整理移行をJPX日付付き原発信で補完し、改善による解除ではないため既定negative_material-4を適用。31日時点は上場中のため母集団から除外しない。過去予測へ遡及反映しない。','',
 f'候補：採用{len(scores["candidates"])}、原開示未照合除外{len(scores["rejected_candidates"])}。','',
 '|予測順位|コード・銘柄|得点|前日終値→終値|騰落率|実績順位|判定|','|---:|---|---:|---:|---:|---:|---|']
 for detail,p in zip(ev['predictions'],pred['payload']['predictions']):
  c=p['code']
  if c in lookup:q=lookup[c];before=q['previous_close'];close=q['close'];source=URL
  else:
   h=historical(c);before=h[PRIOR]['close'];close=h[DAY]['close'];assert h[DAY]['volume']>0;source=h[DAY]['url']
  detail.update(name=p['name'],score=p['score'],previous_close=before,actual_close=close,actual_return_pct=100*(close/before-1),actual_source=source,material_types=[v['type'] for v in p['events']],missing_momentum=p['missing_momentum'],price_status='traded_close')
  allrows.append(dict(date=DAY,**detail));rank=detail['actual_rank']
  report.append(f'|{detail["predicted_rank"]}|{c} {p["name"]}|{p["score"]:g}|{before:g}→{close:g}|{detail["actual_return_pct"]:+.2f}%|{rank or "—"}|{"的中" if rank else "上位10外"}|')
 save(ROOT/f'results/july_evaluations/{DAY}.json',ev);write_csv(ROOT/'results/july_batch08_predictions.csv',allrows)
 previous=json.loads((ROOT/f'data/july_actuals/{PRIOR}.json').read_text())['top10'];common=sorted({r['code'] for r in previous}&set(EXPECTED));baseline=dict(date=DAY,predictions=[r['code'] for r in previous],hit_codes=common,hits=len(common))
 save(ROOT/'results/july_batch08_baseline.json',dict(rule='前営業日の東証普通株上昇率上位10を継続選出',days=[baseline],hits=len(common),precision_at_10=len(common)/10))
 m=month();summary=dict(days=[DAY],evaluations=[ev],hits=ev['hits'],prediction_count=10,precision_at_10=ev['hits']/10,recall_at_10=ev['hits']/10,exact_rank_hits=ev['exact_rank_hits'],cumulative_hits=m['hits'],cumulative_prediction_count=220,cumulative_precision_at_10=m['precision_at_10'],all_july_sessions_completed=True,full_tse_universe=False,blind_test=False,all_prediction_actual_statuses_verified=True,traded_close_count=10,no_regular_trade_count=0,next_phase='july_error_analysis',next_days=NEXT)
 save(ROOT/'results/july_batch08_summary.json',summary)
 report+=['','実際の上位10：','', '|順位|コード・銘柄|前日終値→終値|上昇率|予測上位10|','|---:|---|---:|---:|---|']
 selected={p['code'] for p in pred['payload']['predictions']}
 for i,r in enumerate(actual['top10']):report.append(f'|{i+1}|{r["code"]} {r["name"]}|{r["previous_close"]:g}→{r["close"]:g}|{r["return_pct"]:.2f}%|{"的中" if r["code"] in selected else "未選出"}|')
 report+=['',f'出典：{URL} ／ {SECOND} ／ 6997の日付付き時系列',f'封印SHA256：{pred["sha256"]}','',
 f'上位10入り{ev["hits"]}/10（{ev["hits"]/10:.2%}）、同順位一致{ev["exact_rank_hits"]}件。前日上位10継続は{len(common)}/10。全10予測の約定終値・前日終値を確認。',
 '当日5%以上表は初回取得が途中で切れたため追加窓を統合し、原表361行・東証普通株330行を保存。実績上位10のETN2033を除外し6997を繰上げ、別時系列で照合した。上位10外の正確な順位は空欄。',
 f'7月全22営業日：{m["hits"]}/220（{m["precision_at_10"]:.2%}）。詳細はjuly_month_report.mdと全220予測CSVを参照。',
 'このチャットの完了回数は3/7。次は7/1・2・3の詳細な不的中原因分析で、続行回答待ち。スクリーニング用プロンプトは未作成。','']
 (ROOT/'results/july_batch08_report.md').write_text('\n'.join(report))
 state=json.loads((ROOT/'results/state.json').read_text());state.update(phase='july_error_analysis',july_completed_batch=8,july_completed_days=trading_days(7),july_prediction_complete=True,next_days=NEXT,requires_user_continue=True,error_analysis_started=False,error_analysis_completed_days=[],screening_prompt_created=False);save(ROOT/'results/state.json',state)
 chat=json.loads((ROOT/'results/chat_handoff_state.json').read_text());chat.update(completed_batches_in_chat=3,completed_batch_ids_in_chat=['july_prediction_batch06','july_prediction_batch07','july_prediction_batch08'],next_authorized_batch=[],handoff_prepared=False,note='第6・7回と最終7/31の第8回を完了し3/7。次は7/1・2・3の不的中原因分析、続行回答待ち。段階をまたいで7回ごとに引き継ぐ。');save(ROOT/'results/chat_handoff_state.json',chat)
 manifest();print(json.dumps({k:v for k,v in summary.items() if k!='evaluations'},ensure_ascii=False));print(json.dumps({k:v for k,v in m.items() if k not in ['days','daily']},ensure_ascii=False))
if __name__=='__main__':run()
