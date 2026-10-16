import json,re,hashlib,csv
from datetime import datetime
from prepare_july import ROOT,save,texts,ranking
from research import evaluate,gate,digest
DAYS=['2026-07-17','2026-07-21','2026-07-22']
RANK_FILES=['jb5_actual17.json','jb5_actual21_complete.json','jb5_actual22.json']
RANK_URLS=['https://kabu.kininew.net/fiveup/8023.html','https://kabu.kininew.net/fiveup/8033.html','https://kabu.kininew.net/fiveup/8044.html']
SECOND=['https://uiblog.hatenablog.com/entry/2026/07/19/164656','https://uiblog.hatenablog.com/entry/2026/07/21/211202','https://uiblog.hatenablog.com/entry/2026/07/22/204320']
EXPECTED=[['5242','150A','5216','7501','278A','7581','3697','2354','6573','1827'],['2354','150A','598A','2345','4762','9238','296A','285A','5242','5575'],['4052','4424','3907','4073','3803','6522','5575','6769','5242','1770']]
def history(code):
 out={}
 for name in ['jb5_hist_'+code+'.json','jb5_hist_retry_'+code+'.json']:
  path=ROOT/'evidence'/name
  if not path.exists():continue
  for section in re.split(r'\n-{20,}\n',texts(path)):
   m=re.search(r'https://96ut.com/stock/jikei\.php\?code='+code+r'(?:&year=2026)?(?=[)\s])',section)
   if not m:continue
   for line in section.splitlines():
    md=re.match(r'L\d+: (2026/07/(?:16|17|21|22))\s*\|(.+)',line)
    if md:
     out[md[1].replace('/','-')]={'close':float(md[2].split('|')[3].strip().replace(',','')),'url':m[0],'file':name}
 if code in ['438A','8707']:
  name='jb5_hist'+code+'_find.json'
  section=re.split(r'\n-{20,}\n',texts(ROOT/'evidence'/name))[0]
  url=re.search(r'https://finance.stockweather.co.jp/[^\s)]+',section)[0]
  for md in re.finditer(r'(2026/07/(?:16|17|21|22))\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)',section):
   out[md[1].replace('/','-')]={'close':float(md[5].replace(',','')),'url':url,'file':name,'verification':'日付付き検索保存版の対象銘柄OHLC表。後続検索結果の別表は使用しない。'}
 for day,prev in zip(DAYS,['2026-07-16','2026-07-17','2026-07-21']):
  if day in out and prev in out:out[day]['previous_close']=out[prev]['close']
 return out
allrows=[];evaluations=[];report=['# 7月予測検証 第5回：2026年7月17・21・22日','',
 '対象：東証普通株、前営業日終値から当日終値への上昇率上位10。各日08:30 JSTを締切とする過去再現。20日は海の日の休場。',
 '固定モデルv1と採点コードは変更なし。材料の初回適格日・経過日数を営業日で計算。封印後の候補や入力の補修は行わない。',
 '制約：候補は前日5%以上表と取得ニュース掲載株の部分集合。原開示を照合できないニュースのみ候補は除外。全東証網羅、長期OHLCV、板、PTS、浮動株、信用・貸借、マクロの定量入力は未達。',
 '予測入力は締切前の原資料と当時記事に限定。ただし調査時の動的な開示一覧に将来記事が偶発表示されているため非盲検。特に5074の原資料探索時に8/14の契約中止見出しが表示された。入力・採点には不使用だが、厳密な将来情報遮断を実証した検証とは呼べない。',
 '原開示照合：受注・採用・研究契約は契約、MOU・合弁は2点、製品発売は3点、実際の利益増・黒字転換・予想上方修正は5点。9439の子会社設立は正式な事業開始決定前のため契約加点なし。5074の受注は約60億円。',
 '7/21の前日ランキング取得表は途中で切れていたため、7/22の入力・予測封印前に末尾を補完。原表198行、東証普通株174行を確認し、部分取得ファイルも保持。封印済みの日付には遡及反映しない。',
 '7/21の5078は立会市場の出来高0、約定終値なしを別時系列で確認。0円や騰落率0%には変換せず終値・騰落率を欠損として記録。直前約定終値は4,870円。ランキング判定は上位10外。',
 '実績は丸め前の比率で並べる。二次表と市場除外・価格算術を照合。7/17別表のETF/ETNを除いた不足2銘柄は日付付き時系列で補完。SHIFTは別表の整数丸めを採用せず743.4円・前日比63.6円を維持。全東証原票からの独立再ソートではない。','']
for i,(day,file,url) in enumerate(zip(DAYS,RANK_FILES,RANK_URLS)):
 rows=ranking(texts(ROOT/'evidence'/file));rows.sort(key=lambda r:(-(r['change']/(r['close']-r['change'])),r['code']))
 actual=rows[:10];assert [r['code'] for r in actual]==EXPECTED[i]
 for r in rows:
  pct=100*r['change']/(r['close']-r['change']);assert abs(pct-r['return_pct'])<0.011
  r['reported_return_pct']=r['return_pct'];r['return_pct']=pct;r['previous_close']=r['close']-r['change'];r['url']=url
 obj={'date':day,'top10_verified':True,'verification_scope':'別集計表との市場・順位・価格算術照合。7/17は別表のETF/ETNを除き6573・1827を日付付き時系列で補完。SHIFT別表は丸め値のため主表の小数値を維持。全東証原票からの独立再ソートではない。','sources':[url,SECOND[i]]+(['https://96ut.com/stock/jikei.php?code=6573&year=2026','https://96ut.com/stock/jikei.php?code=1827&year=2026'] if i==0 else []),'top10':actual}
 save(ROOT/f'data/july_actuals/{day}.json',obj)
 pred=json.loads((ROOT/f'results/july_predictions/{day}.json').read_text());assert digest(pred['payload'])==pred['sha256']
 g=gate(pred['payload']['evidence'],day+'T08:30:00+09:00');assert not g['rejected']
 e=evaluate(pred,obj);look={r['code']:r for r in rows}
 report += [f'## {day}：{e["hits"]}/10','',f'候補：採用{len(json.loads((ROOT/f"results/july_scores/{day}.json").read_text())["candidates"])}、未確認除外{len(json.loads((ROOT/f"results/july_scores/{day}.json").read_text())["rejected_candidates"])}。','', '|予測順位|コード・銘柄|当日根拠|得点|前日終値→終値|実際の騰落率|実績順位|判定|','|---:|---|---|---:|---:|---:|---:|---|']
 for detail,p in zip(e['predictions'],pred['payload']['predictions']):
  code=p['code'];h=look.get(code)
  if h:quote={k:h[k] for k in ['close','previous_close','url']}
  elif code=='5078' and day=='2026-07-21':quote={'close':None,'previous_close':4870.0,'url':'https://www.traders.co.jp/stocks/62_5078/historical/2'}
  else:quote=history(code)[day]
  assert quote['previous_close']>0
  pct=None if quote['close'] is None else 100*(quote['close']/quote['previous_close']-1)
  if quote['close'] is not None:assert quote['close']>0
  detail.update(name=p['name'],score=p['score'],previous_close=quote['previous_close'],actual_close=quote['close'],actual_return_pct=pct,actual_source=quote['url'],material_types=[v['type'] for v in p.get('events',[])],missing_momentum=p['missing_momentum'],price_status='no_regular_trade' if pct is None else 'traded_close')
  allrows.append(dict(date=day,**detail));rank=detail['actual_rank'];result='的中' if rank else '上位10外'
  types=','.join(detail['material_types']) or '価格のみ'
  price_label=f'{quote["previous_close"]:g}→{quote["close"]:g}' if pct is not None else '4,870→約定終値なし'
  pct_label=f'{pct:+.2f}%' if pct is not None else '—（出来高0）'
  report.append(f'|{detail["predicted_rank"]}|{code} {p["name"]}|{types}|{p["score"]:g}|{price_label}|{pct_label}|{rank or "—"}|{result}|')
 report += ['','実際の上位10：','', '|実績順位|コード・銘柄|前日終値→終値|上昇率|予測上位10|','|---:|---|---:|---:|---|']
 selected={p['code'] for p in pred['payload']['predictions']}
 for j,r in enumerate(actual):report.append(f'|{j+1}|{r["code"]} {r["name"]}|{r["previous_close"]:g}→{r["close"]:g}|{r["return_pct"]:.2f}%|{"的中" if r["code"] in selected else "未選出"}|')
 report += ['',f'実績出典：{url} ／ {SECOND[i]}',f'封印SHA256：{pred["sha256"]}','']
 save(ROOT/f'results/july_evaluations/{day}.json',e);evaluations.append(e)
hits=sum(e['hits'] for e in evaluations)
baseline=[]
for day,prev,ev in zip(DAYS,['2026-07-16','2026-07-17','2026-07-21'],evaluations):
 previous=json.loads((ROOT/f'data/july_actuals/{prev}.json').read_text())['top10']
 actual=json.loads((ROOT/f'data/july_actuals/{day}.json').read_text())['top10']
 common=sorted({r['code'] for r in previous}&{r['code'] for r in actual})
 baseline.append(dict(date=day,predictions=[r['code'] for r in previous],hit_codes=common,hits=len(common)))
save(ROOT/'results/july_batch05_baseline.json',dict(rule='前営業日の東証普通株上昇率上位10をそのまま予測に使用。実行規約に記録済みの比較基準。',days=baseline,hits=sum(r['hits'] for r in baseline),precision_at_10=sum(r['hits'] for r in baseline)/30))
report+=['## 集計','',f'延べ30予測中{hits}件的中、上位10外{30-hits}件、Precision@10={hits/30:.2%}。順位まで一致{sum(e["exact_rank_hits"] for e in evaluations)}件。的中率は売買収益率ではない。','30件すべてのランキング判定を完了。29件は当日終値と前日終値を取得、1件は立会出来高0で約定終値なし。上位10外の正確な全市場順位は未取得として空欄。', '全7月を終えた後に行う詳細な誤差原因分析・改善ルール作成は未着手。次回：7月23・24・27日。']
report += ['',f'比較基準（前日上位10を継続選出）：各日{[r["hits"] for r in baseline]}件、合計{sum(r["hits"] for r in baseline)}/30。固定モデルの変更には使わない。']
save(ROOT/'results/july_batch05_summary.json',dict(days=DAYS,evaluations=evaluations,hits=hits,prediction_count=30,precision_at_10=hits/30,cumulative_hits=14+hits,cumulative_prediction_count=150,cumulative_precision_at_10=(14+hits)/150,exact_rank_hits=sum(sum(p["predicted_rank"]==p["actual_rank"] for p in ev["predictions"]) for ev in evaluations),full_tse_universe=False,blind_test=False,all_prediction_actual_statuses_verified=True,traded_close_count=29,no_regular_trade_count=1,next_days=['2026-07-23','2026-07-24','2026-07-27']))
(ROOT/'results/july_batch05_report.md').write_text('\n'.join(report)+'\n')
with (ROOT/'results/july_batch05_predictions.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]),lineterminator="\n");w.writeheader();w.writerows(allrows)
state=json.loads((ROOT/'results/state.json').read_text());state.update(phase='july_prediction',july_completed_batch=5,july_completed_days=sorted(set(state.get('july_completed_days',[])+DAYS)),next_days=['2026-07-23','2026-07-24','2026-07-27'],requires_user_continue=True,july_predictions_created=True,model_status='frozen',screening_prompt_created=False,error_analysis_started=False);save(ROOT/'results/state.json',state)
files=[ROOT/'data/july_model_frozen.json',ROOT/'data/july_model_v1.json',ROOT/'july_predict.py',ROOT/'results/july_batch05_report.md',ROOT/'results/july_batch05_summary.json',ROOT/'results/july_batch05_predictions.csv',ROOT/'results/july_batch05_baseline.json']
for day in DAYS:
 for group in ['july_predictions','july_scores','july_evaluations']:files.append(ROOT/f'results/{group}/{day}.json')
 files.append(ROOT/f'data/july_inputs/{day}.json');files.append(ROOT/f'data/july_actuals/{day}.json')
files += [ROOT/'build_july_batch05.py',ROOT/'audit_july_batch05.py',ROOT/'finalize_july_batch05.py']
if (ROOT/'results/july_batch05_audit.json').exists():files.append(ROOT/'results/july_batch05_audit.json')
files += sorted((ROOT/'evidence').glob('jb5_*.json'))
for suffix in ['17','21','22']:
 for group in ['july_releases_','july_events_']:files.append(ROOT/f'data/{group}{suffix}.json')
save(ROOT/'results/july_batch05_manifest.json',{'created_at_utc':datetime.now().astimezone().isoformat(),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
print(json.dumps({'hits':hits,'total':30,'pct':hits/30,'traded_closes':29,'no_regular_trade':1,'cumulative_hits':14+hits,'cumulative_count':150},ensure_ascii=False))
