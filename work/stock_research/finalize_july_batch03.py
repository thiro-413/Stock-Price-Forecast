import json,re,hashlib,csv
from datetime import datetime
from prepare_july import ROOT,save,texts,ranking
from research import evaluate,gate,digest
DAYS=['2026-07-09','2026-07-10','2026-07-13']
RANK_FILES=['jb3_actual09.json','jb3_actual10.json','jb3_actual13.json']
RANK_URLS=['https://kabu.kininew.net/fiveup/7961.html','https://kabu.kininew.net/fiveup/7970.html','https://kabu.kininew.net/fiveup/7982.html']
SECOND=['https://uiblog.hatenablog.com/entry/2026/07/09/205230','https://uiblog.hatenablog.com/entry/2026/07/12/092445','https://stock.f-frontier.com/2026/07/13/234366/']
EXPECTED=[['9399','4381','7314','584A','218A','9348','2997','4424','6668','7128'],['5240','4381','4424','4833','2997','5018','9399','6327','6227','472A'],['4381','5240','4199','7453','6573','6814','195A','6227','9331','3168']]
def history(code):
 out={}
 if code=='2683':
  t=texts(ROOT/'evidence/jb3_uoki_search.json').split('--------------------------------------------------------------------------------')[0]
  assert '株価(07/13)' in t and '2026/07/14' in t
  close=float(re.search(r'年高値\s+([0-9,.]+) 円',t)[1].replace(',',''))
  prev=float(re.search(r'前日終値\s*\|\s*([0-9,.]+)円\s*\|\s*07/10',t)[1].replace(',',''))
  return {'2026-07-13':{'close':close,'previous_close':prev,'url':'https://minkabu.jp/stock/2683/chart','file':'jb3_uoki_search.json','verification':'検索保存版の7/13日付終値。現在開くと8月版となるため混同しない。別の調整後終値表でも1013円を照合。'}}
 files=[ROOT/f'evidence/jb3_hist_{code}.json',ROOT/f'evidence/jb3_hist_retry_{code}.json']
 for file in files:
  if not file.exists():continue
  for section in re.split(r'\n-{20,}\n',texts(file)):
   m=re.search(r'https://96ut.com/stock/jikei\.php\?code='+code+r'(?:&year=2026)?(?=[)\s])',section)
   if not m:continue
   for line in section.splitlines():
    mday=re.match(r'L\d+: (2026/07/(?:0[89]|1[03]))\s*\|(.+)',line)
    if not mday:continue
    parts=mday[2].split('|');close=float(parts[3].strip().replace(',',''))
    day=mday[1].replace('/','-');out[day]={'close':close,'url':m[0],'file':file.name}
 for day,prev in [('2026-07-09','2026-07-08'),('2026-07-10','2026-07-09'),('2026-07-13','2026-07-10')]:
  if day in out and prev in out:out[day]['previous_close']=out[prev]['close']
 return out
allrows=[];evaluations=[];report=['# 7月予測検証 第3回：2026年7月9・10・13日','',
 '対象：東証普通株の前営業日終値→当日終値の上昇率上位10。各日08:30 JSTを入力締切とした過去再現。',
 '固定モデル：材料点（業績改善5、契約4、商品3、MOU2等）＋前日騰落率/10（-2〜3点）＋S/G市場1点−明示悪材料。材料は初回締切で全点、次の2営業日は半点。欠損前日騰落率は0点。',
 '制約：全東証を網羅せず、前日5%以上表と取得記事掲載株から候補を作成。記事のうち原開示照合未了の銘柄を除外。長期OHLCV・浮動株・板・PTS・マクロの定量採点なし。入力に締切後の情報は入れない。',
 '非盲検：検索結果で将来記事・週次結果が偶発表示された。全て予測入力から除外したが、厳密な未見検証とは言えない。日付付き原開示と当時記事を照合したが第三者の当時アーカイブによる改訂不存在の完全証明ではない。',
 '監査：採点式・コードは変更なし。コンソーシアムのサービス公開はproduct、拘束力のある事業提携はcontractに分類。TOB専用加点なし。予測入力に当日引け価格は不使用。検索で7/13HKS記事など将来・締切後の記述が偶発表示され、不採用として非盲検に記録。魚喜の終値補完は日付付き検索保存版と別の終値表を照合。','']
for i,(day,file,url) in enumerate(zip(DAYS,RANK_FILES,RANK_URLS)):
 rows=ranking(texts(ROOT/'evidence'/file));rows.sort(key=lambda r:-(r['change']/(r['close']-r['change'])))
 actual=rows[:10];assert [r['code'] for r in actual]==EXPECTED[i]
 for r in rows:
  pct=100*r['change']/(r['close']-r['change']);assert abs(pct-r['return_pct'])<0.011
  r['reported_return_pct']=r['return_pct'];r['return_pct']=pct;r['previous_close']=r['close']-r['change'];r['url']=url
 obj={'date':day,'top10_verified':True,'verification_scope':'二次集計表の市場・順位・算術を別集計表と照合。7/13別表の名証単独3808とETN2068を除外して9331・3168を補充し確認。9399は東証外国普通株として対象内。全東証原票の再ソートではない。','sources':[url,SECOND[i]],'top10':actual}
 save(ROOT/f'data/july_actuals/{day}.json',obj)
 pred=json.loads((ROOT/f'results/july_predictions/{day}.json').read_text());assert digest(pred['payload'])==pred['sha256']
 g=gate(pred['payload']['evidence'],day+'T08:30:00+09:00');assert not g['rejected']
 e=evaluate(pred,obj);look={r['code']:r for r in rows}
 report += [f'## {day}：{e["hits"]}/10','',f'候補：採用{len(json.loads((ROOT/f"results/july_scores/{day}.json").read_text())["candidates"])}、未確認除外{len(json.loads((ROOT/f"results/july_scores/{day}.json").read_text())["rejected_candidates"])}。','', '|予測順位|コード・銘柄|当日根拠|得点|前日終値→終値|実際の騰落率|実績順位|判定|','|---:|---|---|---:|---:|---:|---:|---|']
 for detail,p in zip(e['predictions'],pred['payload']['predictions']):
  code=p['code'];h=look.get(code)
  if h:quote={k:h[k] for k in ['close','previous_close','url']}
  else:quote=history(code)[day]
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
baseline=[]
for day,prev,ev in zip(DAYS,['2026-07-08','2026-07-09','2026-07-10'],evaluations):
 previous=json.loads((ROOT/f'data/july_actuals/{prev}.json').read_text())['top10']
 actual=json.loads((ROOT/f'data/july_actuals/{day}.json').read_text())['top10']
 common=sorted({r['code'] for r in previous}&{r['code'] for r in actual})
 baseline.append(dict(date=day,predictions=[r['code'] for r in previous],hit_codes=common,hits=len(common)))
save(ROOT/'results/july_batch03_baseline.json',dict(rule='前営業日の東証普通株上昇率上位10をそのまま予測に使用。実行規約に記録済みの比較基準。',days=baseline,hits=sum(r['hits'] for r in baseline),precision_at_10=sum(r['hits'] for r in baseline)/30))
report+=['## 集計','',f'延べ30予測中{hits}件的中、上位10外{30-hits}件、Precision@10={hits/30:.2%}。順位まで一致1件。的中率は売買収益率ではない。','全30予測の当日終値・前日終値・騰落率を取得。上位10外の正確な全市場順位は未取得として空欄。', '全7月を終えた後に行う詳細な誤差原因分析・改善ルール作成は未着手。次回：7月14・15・16日。']
report += ['',f'比較基準（前日上位10を継続選出）：各日{[r["hits"] for r in baseline]}件、合計{sum(r["hits"] for r in baseline)}/30。固定モデルの変更には使わない。']
save(ROOT/'results/july_batch03_summary.json',dict(days=DAYS,evaluations=evaluations,hits=hits,prediction_count=30,precision_at_10=hits/30,cumulative_hits=8+hits,cumulative_prediction_count=90,cumulative_precision_at_10=(8+hits)/90,exact_rank_hits=sum(sum(p["predicted_rank"]==p["actual_rank"] for p in ev["predictions"]) for ev in evaluations),full_tse_universe=False,blind_test=False,all_prediction_actual_prices_retrieved=True,next_days=['2026-07-14','2026-07-15','2026-07-16']))
(ROOT/'results/july_batch03_report.md').write_text('\n'.join(report)+'\n')
with (ROOT/'results/july_batch03_predictions.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
state=json.loads((ROOT/'results/state.json').read_text());state.update(phase='july_prediction',july_completed_batch=3,july_completed_days=sorted(set(state.get('july_completed_days',[])+DAYS)),next_days=['2026-07-14','2026-07-15','2026-07-16'],requires_user_continue=True,july_predictions_created=True,model_status='frozen',screening_prompt_created=False,error_analysis_started=False);save(ROOT/'results/state.json',state)
files=[ROOT/'data/july_model_frozen.json',ROOT/'data/july_model_v1.json',ROOT/'july_predict.py',ROOT/'results/july_batch03_report.md',ROOT/'results/july_batch03_summary.json',ROOT/'results/july_batch03_predictions.csv',ROOT/'results/july_batch03_baseline.json']
for day in DAYS:
 for group in ['july_predictions','july_scores','july_evaluations']:files.append(ROOT/f'results/{group}/{day}.json')
 files.append(ROOT/f'data/july_inputs/{day}.json');files.append(ROOT/f'data/july_actuals/{day}.json')
save(ROOT/'results/july_batch03_manifest.json',{'created_at_utc':datetime.now().astimezone().isoformat(),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
print(json.dumps({'hits':hits,'total':30,'pct':hits/30,'all_prices':True,'rows':allrows,'cumulative_hits':8+hits,'cumulative_count':90},ensure_ascii=False))
