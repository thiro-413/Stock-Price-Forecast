"""Evaluate the sealed July 28–30 batch; no forecast regeneration."""
import csv,hashlib,json,re
from datetime import datetime,timezone
from prepare_july import ROOT,save,texts,ranking
from research import digest,evaluate,gate
DAYS=['2026-07-28','2026-07-29','2026-07-30']
PRIOR=['2026-07-27','2026-07-28','2026-07-29']
RANK_FILES=['jb7_actual28.json','jb7_actual29_final.json','jb7_actual30_final.json']
URLS=['https://kabu.kininew.net/fiveup/8078.html','https://kabu.kininew.net/fiveup/8087.html','https://kabu.kininew.net/fiveup/8096.html']
SECOND=['https://uiblog.hatenablog.com/entry/2026/07/28/191951','https://uiblog.hatenablog.com/entry/2026/07/29/180402','https://uiblog.hatenablog.com/entry/2026/07/30/213445']
SECOND_FILES=['jb7_secondary28.json','jb7_secondary29.json','jb7_actual30.json']
EXPECTED=[['7063','2767','8995','3054','9441','7069','9337','4370','3697','3778'],['3907','2767','9697','504A','6337','9227','9766','8218','5285','6522'],['7740','2737','6364','4461','6862','6349','6337','8254','5103','3997']]
EXTRA=[['4370','3697','3778'],['6522'],[]]

def historical(code):
 file={'3969':'jb7_hist_alt3969.json','4370':'jb7_hist_alt4370.json','4888':'jb7_hist_alt4888.json','3842':'jb7_hist_final3842.json','3697':'jb7_verify3697.json'}.get(code,f'jb7_hist_{code}.json')
 path=ROOT/'evidence'/file;t=texts(path);result={}
 # Minkabu daily_bar has an additional adjusted-close column; 96ut does not.
 adjusted=code in ['3842','3697']
 pattern=r'L\d+: (2026/07/(?:27|28|29|30))\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*'+(r'[\d,.]+\s*\|\s*' if adjusted else '')+r'([\d,]+)'
 for m in re.finditer(pattern,t):
  result[m[1].replace('/','-')]={'close':float(m[5].replace(',','')),'volume':int(m[6].replace(',','')),'url':f'https://minkabu.jp/stock/{code}/daily_bar?page=3'+('&selected_platform=pc' if code=='3842' else '') if adjusted else f'https://96ut.com/stock/jikei.php?code={code}'+('' if '_alt' in file else '&year=2026'),'file':str(path.relative_to(ROOT))}
 return result

def manifest():
 paths=[ROOT/p for p in ['july_predict.py','data/july_model_v1.json','data/july_model_frozen.json','build_july_batch07.py','finalize_july_batch07.py','audit_july_batch07.py','data/july_batch07_additional_events.json']]
 paths+=sorted((ROOT/'evidence').glob('jb7_*.json'))
 paths+=sorted((ROOT/'results').glob('july_batch07_*'))
 paths=[p for p in paths if p.name!='july_batch07_manifest.json']
 for day in DAYS:
  paths += [ROOT/f'data/{g}/{day}.json' for g in ['july_inputs','july_actuals']]
  paths += [ROOT/f'results/{g}/{day}.json' for g in ['july_predictions','july_scores','july_evaluations']]
  paths += [ROOT/f'data/{g}_{day[-2:]}.json' for g in ['july_events','july_releases']]
 save(ROOT/'results/july_batch07_manifest.json',{'created_at_utc':datetime.now(timezone.utc).isoformat(),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}})

def run():
 evaluations=[];allrows=[];baseline=[]
 report=['# 7月予測検証 第7回：2026年7月28・29・30日','',
 '各日08:30 JSTまでに公表された原資料と当時記事を照合し、固定モデルv1の予測を封印してから当日実績ランキングを意図的に取得した。過去18営業日分の入力・封印、固定モデル・採点コードは変更していない。',
 '候補は前営業日5%以上表と取得ニュース掲載普通株の部分集合。原開示未照合のニュースのみ候補は除外。全東証の網羅検証ではない。板・PTS・長期OHLCV・浮動株・信用貸借・マクロの定量値は入力に使用していない。欠損前日騰落率は得点0だが0%とは記録しない。',
 '検索結果・動的な開示一覧に将来記事・週次結果・当日引け記事の見出し等が偶発表示された。とくに28日封印後の資料探索で29日の決算インパクト記事と29日上位表が表示された。入力には不採用だが非盲検であり、厳密な将来情報遮断を実証した検証ではない。',
 '実績は第三者表から地方単独上場・ETF/ETNを除外し、丸め前の比率で比較。別集計表の不足は時系列で補完。全東証原票から独自に再ソートした結果ではない。上位10外の正確な全市場順位は未取得のため空欄。',
 '分類の照合：2311は中間純利益下方修正を含み-4を併用。6663は利益上方修正と売上予想下方修正が混在し-4を併用。6822は最終上方修正で営業・経常据置。3636は連結通期据置でセグメント別修正を連結下方修正としない。',
 '4888は7/27の岡山大学研究契約と7/28のQST病院基本合意を別証拠・別鮮度で保持。後者を新しい研究契約と誤認しない。9227の試作装置・特許は販売開始を確認できずunknown。190Aの部会了承を正式指定・製造販売承認や新発売としない。',
 '7102の原PDFはテキストなし、6042は文字化けのため原PDF第1ページ画像で照合。6501のYahoo403はJPX転載で補完。9698の原資料の経常増益率61.5%を記事の63%表現より優先した。','']
 for i,(day,prev,file,url) in enumerate(zip(DAYS,PRIOR,RANK_FILES,URLS)):
  rows=ranking(texts(ROOT/'evidence'/file));rows.sort(key=lambda r:(-r['change']/(r['close']-r['change']),r['code']))
  assert [r['code'] for r in rows[:10]]==EXPECTED[i]
  for r in rows:
   pct=100*r['change']/(r['close']-r['change']);assert abs(pct-r['return_pct'])<0.011
   r.update(reported_return_pct=r['return_pct'],return_pct=pct,previous_close=r['close']-r['change'],url=url)
  actual={'date':day,'top10_verified':True,'verification_scope':'別集計表と照合。7/28の名証3260・ETF1366/1357、7/29のETN2034を除外し、不足3/1銘柄を日付付き時系列で補完。7/30は別表10件一致。全原票独自再ソートではない。','sources':[url,SECOND[i]]+[historical(c)[day]['url'] for c in EXTRA[i]],'top10':rows[:10]}
  save(ROOT/f'data/july_actuals/{day}.json',actual)
  pred=json.loads((ROOT/f'results/july_predictions/{day}.json').read_text());assert digest(pred['payload'])==pred['sha256']
  assert not gate(pred['payload']['evidence'],day+'T08:30:00+09:00')['rejected']
  ev=evaluate(pred,actual);lookup={r['code']:r for r in rows};scores=json.loads((ROOT/f'results/july_scores/{day}.json').read_text())
  report += [f'## {day}：{ev["hits"]}/10','',f'候補：採用{len(scores["candidates"])}、原開示未照合除外{len(scores["rejected_candidates"])}。','', '|予測順位|コード・銘柄|材料分類|得点|前日終値→終値|騰落率|実績順位|判定|','|---:|---|---|---:|---:|---:|---:|---|']
  for detail,p in zip(ev['predictions'],pred['payload']['predictions']):
   code=p['code']
   if code in lookup:q=lookup[code];before=q['previous_close'];close=q['close'];source=q['url']
   else:
    h=historical(code);q=h[day];before=h[prev]['close'];close=q['close'];source=q['url'];assert q['volume']>0
   assert before>0 and close>0
   pct=100*(close/before-1);types=[x['type'] for x in p.get('events',[])]
   detail.update(name=p['name'],score=p['score'],previous_close=before,actual_close=close,actual_return_pct=pct,actual_source=source,material_types=types,missing_momentum=p['missing_momentum'],price_status='traded_close',actual_source_note='日付付き時系列の原値。3842はみんかぶで照合。' if code=='3842' else '')
   allrows.append(dict(date=day,**detail));rank=detail['actual_rank']
   report.append(f'|{detail["predicted_rank"]}|{code} {p["name"]}|{",".join(types) or "価格のみ"}|{p["score"]:g}|{before:g}→{close:g}|{pct:+.2f}%|{rank or "—"}|{"的中" if rank else "上位10外"}|')
  report += ['','実際の上位10：','', '|順位|コード・銘柄|前日終値→終値|上昇率|予測上位10|','|---:|---|---:|---:|---|']
  selected={p['code'] for p in pred['payload']['predictions']}
  for j,r in enumerate(actual['top10']):report.append(f'|{j+1}|{r["code"]} {r["name"]}|{r["previous_close"]:g}→{r["close"]:g}|{r["return_pct"]:.2f}%|{"的中" if r["code"] in selected else "未選出"}|')
  report += ['',f'出典：{url} ／ {SECOND[i]}',f'封印SHA256：{pred["sha256"]}','']
  save(ROOT/f'results/july_evaluations/{day}.json',ev);evaluations.append(ev)
  previous=json.loads((ROOT/f'data/july_actuals/{prev}.json').read_text())['top10'];common=sorted({r['code'] for r in previous}&{r['code'] for r in actual['top10']})
  baseline.append(dict(date=day,predictions=[r['code'] for r in previous],hit_codes=common,hits=len(common)))
 hits=sum(e['hits'] for e in evaluations);exact=sum(e['exact_rank_hits'] for e in evaluations);old=json.loads((ROOT/'results/july_batch06_summary.json').read_text())
 summary=dict(days=DAYS,evaluations=evaluations,hits=hits,prediction_count=30,precision_at_10=hits/30,recall_at_10=hits/30,cumulative_hits=old['cumulative_hits']+hits,cumulative_prediction_count=210,cumulative_precision_at_10=(old['cumulative_hits']+hits)/210,exact_rank_hits=exact,full_tse_universe=False,blind_test=False,all_prediction_actual_statuses_verified=True,traded_close_count=30,no_regular_trade_count=0,next_days=['2026-07-31'])
 save(ROOT/'results/july_batch07_summary.json',summary)
 save(ROOT/'results/july_batch07_baseline.json',dict(rule='前営業日の東証普通株上昇率上位10を継続選出',days=baseline,hits=sum(x['hits'] for x in baseline),precision_at_10=sum(x['hits'] for x in baseline)/30))
 report+=['## 集計','',f'上位10入り{hits}/30（{hits/30:.2%}）、上位10外{30-hits}件。同順位一致{exact}件。前日上位10継続の比較基準は各日{[x["hits"] for x in baseline]}、合計{sum(x["hits"] for x in baseline)}/30。',f'7月累計：21営業日、{summary["cumulative_hits"]}/210（{summary["cumulative_precision_at_10"]:.2%}）。的中率は売買収益率ではない。','全30予測の前日終値・約定終値を確認。SHIFTの二次時系列は整数丸めを避け、みんかぶの882.2→950.0円で28日実績を補完。','30日の5%以上表は原表63行・東証普通株59行。次回31日の候補用にはjb7_actual30_final.jsonを使う。','7月の残りは31日の1営業日。詳細な不的中原因分析は全22日比較後に別途進める。今回の新チャットでの完了回数は2/7。次の最終1日単位はユーザーの続行回答待ち。','']
 (ROOT/'results/july_batch07_report.md').write_text('\n'.join(report))
 with (ROOT/'results/july_batch07_predictions.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(allrows[0]),lineterminator='\n');w.writeheader();w.writerows(allrows)
 state=json.loads((ROOT/'results/state.json').read_text());state.update(phase='july_prediction',july_completed_batch=7,july_completed_days=sorted(set(state['july_completed_days']+DAYS)),next_days=summary['next_days'],requires_user_continue=True,error_analysis_started=False,screening_prompt_created=False);save(ROOT/'results/state.json',state)
 chat=json.loads((ROOT/'results/chat_handoff_state.json').read_text());chat.update(completed_batches_in_chat=2,completed_batch_ids_in_chat=['july_prediction_batch06','july_prediction_batch07'],next_authorized_batch=[],handoff_prepared=False,note='新チャットで第6・7回を完了し2/7。次の7/31（最終1日）は続行回答待ち。予測比較・不的中原因分析をまたいで7回ごとに引き継ぐ。');save(ROOT/'results/chat_handoff_state.json',chat)
 manifest();print(json.dumps({k:v for k,v in summary.items() if k!='evaluations'},ensure_ascii=False))
if __name__=='__main__':run()
