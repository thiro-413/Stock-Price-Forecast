import json,re,hashlib,csv
from datetime import datetime
from prepare_july import ROOT,save,texts,ranking
from research import evaluate,gate,digest
DAYS=['2026-07-01','2026-07-02','2026-07-03']
RANK_FILES=['july1_actualmain.json','july2actual_combined.json','july3actual_first.json']
RANK_URLS=['https://kabu.kininew.net/fiveup/7907.html','https://kabu.kininew.net/fiveup/7915.html','https://kabu.kininew.net/fiveup/7923.html']
SECOND=['https://uiblog.hatenablog.com/entry/2026/07/01/183242','https://uiblog.hatenablog.com/entry/2026/07/02/205304','https://uiblog.hatenablog.com/entry/2026/07/04/104206']
EXPECTED=[['4833','9425','7041','7815','589A','5967','7063','3436','6522','5942'],['7063','7602','9941','6522','4935','3070','4918','2438','7376','7878'],['4596','3133','9425','6634','2492','9444','504A','4575','4935','6166']]
def history(file):
 text=texts(ROOT/'evidence'/file);out={}
 for line in text.splitlines():
  if not re.match(r'L\d+:',line):continue
  parts=re.sub(r'^L\d+:\s*','',line).split('|')
  if not re.fullmatch(r'2026/(?:07/0[123]|06/30)',parts[0].strip()) or len(parts)<6:continue
  vals=[]
  for p in parts[1:]:
   p=p.strip().replace(',','').replace('±','').replace('株','')
   try:vals.append(float(p.rstrip('%')))
   except ValueError:vals.append(None)
  day=parts[0].strip().replace('/','-');source='https://www.traders.co.jp/stocks/62_3494/historical' if file=='july_prices_trial2.json' else re.search(r'https://[^\s)]+',text).group(0)
  out[day]={'close':vals[3],'url':source,'file':file}
  if len(parts)>=9 and vals[4] is not None:out[day]['previous_close']=vals[3]-vals[4]
 for day,prev in [('2026-07-01','2026-06-30'),('2026-07-02','2026-07-01'),('2026-07-03','2026-07-02')]:
  if day in out and 'previous_close' not in out[day] and prev in out:out[day]['previous_close']=out[prev]['close']
 return out
HIST={c:'96hist_'+c+'.json' for c in ['7487','9253','2926','6239','6573','5967','4167','2438']}
HIST.update({c:'histclicked_'+c+'.json' for c in ['2685','2975','464A','7063','7602','2493','3549','6522','4187']})
HIST.update({c:'actualhist2_'+c+'.json' for c in ['5942','9425','4918','4890']})
HIST.update({'3494':'july_prices_trial2.json','4496':'histbase_4496.json'})
allrows=[];evaluations=[];report=['# 7月予測検証 第1回：2026年7月1・2・3日','',
 '対象：東証普通株の前営業日終値→当日終値の上昇率上位10。各日08:30 JSTを入力締切とした過去再現。',
 '固定モデル：材料点（業績改善5、契約4、商品3、MOU2等）＋前日騰落率/10（-2〜3点）＋S/G市場1点−明示悪材料。材料は初回締切で全点、次の2営業日は半点。欠損前日騰落率は0点。',
 '制約：全東証を網羅せず、前日5%以上表と取得記事掲載株から候補を作成。記事のうち原開示照合未了の銘柄を除外。長期OHLCV・浮動株・板・PTS・マクロの定量採点なし。入力に締切後の情報は入れない。',
 '非盲検：検索結果で将来記事・週次結果が偶発表示された。全て予測入力から除外したが、厳密な未見検証とは言えない。日付付き原開示と当時記事を照合したが第三者の当時アーカイブによる改訂不存在の完全証明ではない。',
 '監査：7/3の価格取得窓で先頭6銘柄が欠けたため、7/3実績取得前に補完して予測を再保存。無効な旧封印も保持。モデルの採点式は変更なし。7/2の7602材料は取得漏れ、7/3に初収集したが7/2予測は変更していない。','']
for i,(day,file,url) in enumerate(zip(DAYS,RANK_FILES,RANK_URLS)):
 rows=ranking(texts(ROOT/'evidence'/file));rows.sort(key=lambda r:-(r['change']/(r['close']-r['change'])))
 actual=rows[:10];assert [r['code'] for r in actual]==EXPECTED[i]
 for r in rows:
  pct=100*r['change']/(r['close']-r['change']);assert abs(pct-r['return_pct'])<0.011
  r['reported_return_pct']=r['return_pct'];r['return_pct']=pct;r['previous_close']=r['close']-r['change'];r['url']=url
 obj={'date':day,'top10_verified':True,'verification_scope':'二次集計表の市場・順位・算術と別表を照合。全原票再ソートではない。7/1別表は地方単独3260を除外し5942を補充、5942は別の日足データも照合。','sources':[url,SECOND[i]],'top10':actual}
 save(ROOT/f'data/july_actuals/{day}.json',obj)
 pred=json.loads((ROOT/f'results/july_predictions/{day}.json').read_text());assert digest(pred['payload'])==pred['sha256']
 g=gate(pred['payload']['evidence'],day+'T08:30:00+09:00');assert not g['rejected']
 e=evaluate(pred,obj);look={r['code']:r for r in rows}
 report += [f'## {day}：{e["hits"]}/10','',f'候補：採用{len(json.loads((ROOT/f"results/july_scores/{day}.json").read_text())["candidates"])}、未確認除外{len(json.loads((ROOT/f"results/july_scores/{day}.json").read_text())["rejected_candidates"])}。','', '|予測順位|コード・銘柄|当日根拠|得点|前日終値→終値|実際の騰落率|実績順位|判定|','|---:|---|---|---:|---:|---:|---:|---|']
 for detail,p in zip(e['predictions'],pred['payload']['predictions']):
  code=p['code'];h=look.get(code)
  if h:quote={k:h[k] for k in ['close','previous_close','url']}
  else:quote=history(HIST[code])[day]
  assert quote['close']>0 and quote['previous_close']>0
  pct=100*(quote['close']/quote['previous_close']-1)
  detail.update(name=p['name'],score=p['score'],previous_close=quote['previous_close'],actual_close=quote['close'],actual_return_pct=pct,actual_source=quote['url'],material_types=[v['type'] for v in p.get('events',[])],missing_momentum=p['missing_momentum'])
  allrows.append(dict(date=day,**detail));rank=detail['actual_rank'];result='的中' if rank else '上位10外'
  types=','.join(detail['material_types']) or '価格のみ'
  report.append(f'|{detail["predicted_rank"]}|{code} {p["name"]}|{types}|{p["score"]:g}|{quote["previous_close"]:g}→{quote["close"]:g}|{pct:+.2f}%|{rank or "—"}|{result}|')
 report += ['','実際の上位10：','', '|実績順位|コード・銘柄|前日終値→終値|上昇率|予測上位10|','|---:|---|---:|---:|---|']
 selected={p['code'] for p in pred['payload']['predictions']}
 for j,r in enumerate(actual):report.append(f'|{j+1}|{r["code"]} {r["name"]}|{r["previous_close"]:g}→{r["close"]:g}|{r["return_pct"]:.2f}%|{"的中" if r["code"] in selected else "未選出"}|')
 report += ['',f'実績出典：{url} ／ {SECOND[i]}',f'封印SHA256：{pred["sha256"]}','']
 save(ROOT/f'results/july_evaluations/{day}.json',e);evaluations.append(e)
hits=sum(e['hits'] for e in evaluations)
report+=['## 集計','',f'延べ30予測中{hits}件的中、上位10外{30-hits}件、Precision@10={hits/30:.2%}。順位まで一致0件。的中率は売買収益率ではない。','全30予測の当日終値・前日終値・騰落率を取得。上位10外の正確な全市場順位は未取得として空欄。', '全7月を終えた後に行う詳細な誤差原因分析・改善ルール作成は未着手。次回：7月6・7・8日。']
save(ROOT/'results/july_batch01_summary.json',dict(days=DAYS,evaluations=evaluations,hits=hits,prediction_count=30,precision_at_10=hits/30,full_tse_universe=False,blind_test=False,all_prediction_actual_prices_retrieved=True,next_days=['2026-07-06','2026-07-07','2026-07-08']))
(ROOT/'results/july_batch01_report.md').write_text('\n'.join(report)+'\n')
with (ROOT/'results/july_batch01_predictions.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
state=json.loads((ROOT/'results/state.json').read_text());state.update(phase='july_prediction',july_completed_batch=1,july_completed_days=DAYS,next_days=['2026-07-06','2026-07-07','2026-07-08'],requires_user_continue=True,july_predictions_created=True,model_status='frozen',screening_prompt_created=False,error_analysis_started=False);save(ROOT/'results/state.json',state)
files=[ROOT/'data/july_model_frozen.json',ROOT/'data/july_model_v1.json',ROOT/'july_predict.py',ROOT/'results/july_batch01_report.md',ROOT/'results/july_batch01_summary.json',ROOT/'results/july_batch01_predictions.csv']
for day in DAYS:
 for group in ['july_predictions','july_scores','july_evaluations']:files.append(ROOT/f'results/{group}/{day}.json')
 files.append(ROOT/f'data/july_inputs/{day}.json');files.append(ROOT/f'data/july_actuals/{day}.json')
save(ROOT/'results/july_batch01_manifest.json',{'created_at_utc':datetime.now().astimezone().isoformat(),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
print(json.dumps({'hits':hits,'total':30,'pct':hits/30,'all_prices':True,'rows':allrows},ensure_ascii=False))
