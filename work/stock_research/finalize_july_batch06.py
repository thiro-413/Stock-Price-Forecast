"""Compare already sealed July 23, 24 and 27 forecasts with verified quotes."""
import csv,hashlib,json,re
from datetime import datetime,timezone
from prepare_july import ROOT,save,texts,ranking
from research import digest,evaluate,gate

DAYS=['2026-07-23','2026-07-24','2026-07-27']
PRIOR=['2026-07-22','2026-07-23','2026-07-24']
RANK_FILES=['jb6_actual23_try.json','jb6_actual24_find27.json','jb6_actual27_combined.json']
URLS=['https://kabu.kininew.net/fiveup/8052.html','https://kabu.kininew.net/fiveup/8060.html','https://kabu.kininew.net/fiveup/8070.html']
SECOND=['https://uiblog.hatenablog.com/entry/2026/07/23/191144','https://uiblog.hatenablog.com/entry/2026/07/24/195005','https://uiblog.hatenablog.com/entry/2026/07/27/195717']
EXPECTED=[['5103','2459','1518','5242','593A','6890','584A','6380','2354','4890'],['5240','4424','1518','1723','7034','6999','8541','2354','5242','4564'],['4052','5242','5253','6993','8995','5240','3445','4833','6330','7819']]

def historical(code):
 path=ROOT/f'evidence/jb6_hist_{code}.json';result={}
 if path.exists():
  for match in re.finditer(r'L\d+: (2026/07/(?:22|23|24|27))\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,]+)',texts(path)):
   result[match[1].replace('/','-')]={'close':float(match[5].replace(',','')),'volume':int(match[6].replace(',','')),'url':f'https://96ut.com/stock/jikei.php?code={code}&year=2026','file':str(path.relative_to(ROOT))}
 if code=='9478':
  # First search result is the named Traders historical table, not later search results.
  path=ROOT/'evidence/jb6_hist9478_search.json';section=texts(path).split('\n--------------------------------------------------------------------------------')[0]
  for day,value in [('2026/07/23',552),('2026/07/24',532)]:
   m=re.search(day+r'\s*\|\s*[\d,]+\s*\|\s*[\d,]+\s*\|\s*[\d,]+\s*\|\s*([\d,]+)',section)
   assert m and float(m[1].replace(',',''))==value
   result[day.replace('/','-')]={'close':value,'url':'https://www.traders.co.jp/stocks/62_9478/historical','file':str(path.relative_to(ROOT)),'verification':'日付付きTraders検索保存表。みずほ証券の同日終値532・前日552の検索保存版とも照合。現行ページ本文は未取得。'}
 return result

def manifest():
 paths=[ROOT/'july_predict.py',ROOT/'data/july_model_v1.json',ROOT/'data/july_model_frozen.json',ROOT/'build_july_batch06.py',ROOT/'finalize_july_batch06.py',ROOT/'audit_july_batch06.py',ROOT/'data/july_batch06_annotation_errata.json']
 paths+=sorted((ROOT/'evidence').glob('jb6_*.json'))
 paths+=sorted((ROOT/'results').glob('july_batch06_*'))
 paths=[p for p in paths if p.name!='july_batch06_manifest.json']
 for day in DAYS:
  paths += [ROOT/f'data/{g}/{day}.json' for g in ['july_inputs','july_actuals']]
  paths += [ROOT/f'results/{g}/{day}.json' for g in ['july_predictions','july_scores','july_evaluations']]
  paths += [ROOT/f'data/{g}_{day[-2:]}.json' for g in ['july_events','july_releases']]
 save(ROOT/'results/july_batch06_manifest.json',{'created_at_utc':datetime.now(timezone.utc).isoformat(),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}})

def run():
 evaluations=[];allrows=[];baseline=[]
 report=['# 7月予測検証 第6回：2026年7月23・24・27日','',
 '各日08:30 JSTまでの資料で固定モデルv1を採点し、当日の実績を意図的に取得する前に予測を封印した。固定モデル・採点コードと過去15日分の入力・封印は維持。',
 '候補は前営業日5%以上表と取得ニュース掲載株の部分集合。全東証を網羅した独立検証ではない。板・PTS・長期OHLCV・浮動株・信用貸借・マクロの定量入力は未取得・不使用。原開示未照合のニュースのみ候補は除外。',
 '調査中に検索結果や動的一覧から将来の見出し、週次・月次結果、場中記事が偶発表示されたため非盲検の参考検証。入力には採用せず、ルックアヘッド不存在の実証とは呼ばない。',
 '実績は第三者表からETF/ETN・地方単独上場を除外し、丸め前の比率を計算した。別表の不足は日付付き時系列で補完。全東証原票からの独立再ソートではない。上位10外の正確な順位は空欄。',
 '原資料の照合：6890は7/22 19:35訂正後の経常550億円を優先（記事の580億円は訂正前）。9166は7月発行資料の6月売上であり、7月実績と誤認しない。2334はMOU、6074は未確定の事業譲受基本合意。2693は経常上方修正と通期純利益下方修正が混在し-4点を併用。',
 '7175・8707の7/24正式決算の経常利益は、7/17速報で既知の776・4687百万円と同じ。既知数値の再掲で鮮度を更新せず、初回適格7/21を維持した。6522の規制は7/24から解除、過去の予測へ遡及反映しない。',
 '説明文の訂正：7/24封印後、24日実績の意図的取得前の数値再確認で6999・3242の転記誤りを検出。正しくはKOA通期経常3300→6040百万円・年間配当39→63円、アーバネット経常2850→3100百万円。data/july_batch06_annotation_errata.jsonに正誤を保存。分類・得点・選出への影響は0であり、封印済みファイルは書き換えない。7/27引継ぎ注記には正しい値を使用。','']
 for i,(day,prev,file,url) in enumerate(zip(DAYS,PRIOR,RANK_FILES,URLS)):
  rows=ranking(texts(ROOT/'evidence'/file));rows.sort(key=lambda r:(-r['change']/(r['close']-r['change']),r['code']))
  assert [r['code'] for r in rows[:10]]==EXPECTED[i]
  for r in rows:
   pct=100*r['change']/(r['close']-r['change']);assert abs(pct-r['return_pct'])<0.011
   r.update(reported_return_pct=r['return_pct'],return_pct=pct,previous_close=r['close']-r['change'],url=url)
  actual={'date':day,'top10_verified':True,'verification_scope':'別集計表の東証普通株と照合。不足の7/23=4890、7/24=4564、7/27=4833・6330・7819を日付付き時系列で補完。全原票からの独立再ソートではない。','sources':[url,SECOND[i]],'top10':rows[:10]}
  extra=[['4890'],['4564'],['4833','6330','7819']][i]
  actual['sources'] += [f'https://96ut.com/stock/jikei.php?code={c}&year=2026' for c in extra]
  save(ROOT/f'data/july_actuals/{day}.json',actual)
  pred=json.loads((ROOT/f'results/july_predictions/{day}.json').read_text());assert digest(pred['payload'])==pred['sha256']
  assert not gate(pred['payload']['evidence'],day+'T08:30:00+09:00')['rejected']
  ev=evaluate(pred,actual);lookup={r['code']:r for r in rows};scores=json.loads((ROOT/f'results/july_scores/{day}.json').read_text())
  report += [f'## {day}：{ev["hits"]}/10','',f'候補：採用{len(scores["candidates"])}、原開示未照合除外{len(scores["rejected_candidates"])}。','', '|予測順位|コード・銘柄|材料分類|得点|前日終値→終値|騰落率|実績順位|判定|','|---:|---|---|---:|---:|---:|---:|---|']
  for detail,p in zip(ev['predictions'],pred['payload']['predictions']):
   code=p['code']
   if code in lookup:q=lookup[code];before=q['previous_close'];close=q['close'];source=q['url']
   else:
    h=historical(code);q=h[day];before=h[prev]['close'];close=q['close'];source=q['url']
   assert before>0 and close>0
   pct=100*(close/before-1);types=[x['type'] for x in p.get('events',[])]
   detail.update(name=p['name'],score=p['score'],previous_close=before,actual_close=close,actual_return_pct=pct,actual_source=source,material_types=types,missing_momentum=p['missing_momentum'],price_status='traded_close')
   if code=='9478':detail['actual_source_note']='日付付き検索保存表で確認。現行本文の取得失敗を欠落と区別。'
   else:detail['actual_source_note']=''
   allrows.append(dict(date=day,**detail));rank=detail['actual_rank']
   report.append(f'|{detail["predicted_rank"]}|{code} {p["name"]}|{",".join(types) or "価格のみ"}|{p["score"]:g}|{before:g}→{close:g}|{pct:+.2f}%|{rank or "—"}|{"的中" if rank else "上位10外"}|')
  report += ['','実際の上位10：','', '|順位|コード・銘柄|前日終値→終値|上昇率|予測上位10|','|---:|---|---:|---:|---|']
  selected={p['code'] for p in pred['payload']['predictions']}
  for j,r in enumerate(actual['top10']):report.append(f'|{j+1}|{r["code"]} {r["name"]}|{r["previous_close"]:g}→{r["close"]:g}|{r["return_pct"]:.2f}%|{"的中" if r["code"] in selected else "未選出"}|')
  report += ['',f'出典：{url} ／ {SECOND[i]}',f'封印SHA256：{pred["sha256"]}','']
  save(ROOT/f'results/july_evaluations/{day}.json',ev);evaluations.append(ev)
  previous=json.loads((ROOT/f'data/july_actuals/{prev}.json').read_text())['top10']
  common=sorted({r['code'] for r in previous}&{r['code'] for r in actual['top10']})
  baseline.append(dict(date=day,predictions=[r['code'] for r in previous],hit_codes=common,hits=len(common)))
 hits=sum(e['hits'] for e in evaluations);exact=sum(e['exact_rank_hits'] for e in evaluations)
 old=json.loads((ROOT/'results/july_batch05_summary.json').read_text())
 summary=dict(days=DAYS,evaluations=evaluations,hits=hits,prediction_count=30,precision_at_10=hits/30,recall_at_10=hits/30,cumulative_hits=old['cumulative_hits']+hits,cumulative_prediction_count=180,cumulative_precision_at_10=(old['cumulative_hits']+hits)/180,exact_rank_hits=exact,full_tse_universe=False,blind_test=False,all_prediction_actual_statuses_verified=True,traded_close_count=30,no_regular_trade_count=0,annotation_errata_count=2,next_days=['2026-07-28','2026-07-29','2026-07-30'])
 save(ROOT/'results/july_batch06_summary.json',summary)
 save(ROOT/'results/july_batch06_baseline.json',dict(rule='前営業日の東証普通株上昇率上位10を継続選出',days=baseline,hits=sum(x['hits'] for x in baseline),precision_at_10=sum(x['hits'] for x in baseline)/30))
 report+=['## 集計','',f'上位10入り{hits}/30（{hits/30:.2%}）、上位10外{30-hits}件。同順位一致{exact}件。前日上位10継続の比較基準は各日{[x["hits"] for x in baseline]}、合計{sum(x["hits"] for x in baseline)}/30。',f'7月累計：18営業日、{summary["cumulative_hits"]}/180（{summary["cumulative_precision_at_10"]:.2%}）。的中率は売買収益率ではない。', '全30予測の前日終値・約定終値を確認。9478はTraders日付付き検索保存表とみずほ証券の同日データで補完。', '実績27日の原表は150行。初回取得の途中切断を補完し、東証普通株146行を保存。28日用にはjb6_actual27_combined.jsonを使用する。', '全7月比較後の詳細な不的中原因分析は未着手。次は7月28・29・30日の続行回答待ち。この新チャットでの処理完了回数は1/7。','']
 (ROOT/'results/july_batch06_report.md').write_text('\n'.join(report))
 with (ROOT/'results/july_batch06_predictions.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(allrows[0]),lineterminator='\n');w.writeheader();w.writerows(allrows)
 state=json.loads((ROOT/'results/state.json').read_text());state.update(phase='july_prediction',july_completed_batch=6,july_completed_days=sorted(set(state['july_completed_days']+DAYS)),next_days=summary['next_days'],requires_user_continue=True,error_analysis_started=False,screening_prompt_created=False);save(ROOT/'results/state.json',state)
 chat=json.loads((ROOT/'results/chat_handoff_state.json').read_text());chat.update(completed_batches_in_chat=1,completed_batch_ids_in_chat=['july_prediction_batch06'],counting_starts='current_new_chat',next_authorized_batch=[],handoff_prepared=False,note='引き継ぎ後の新チャットで7/23・24・27を完了し1回。次の7/28・29・30は続行回答待ち。予測比較・不的中原因分析をまたいで7回ごとに引き継ぐ。');save(ROOT/'results/chat_handoff_state.json',chat)
 manifest();print(json.dumps({k:v for k,v in summary.items() if k!='evaluations'},ensure_ascii=False))

if __name__=='__main__':run()
