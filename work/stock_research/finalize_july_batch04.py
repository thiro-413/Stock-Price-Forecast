import json,re,hashlib,csv
from datetime import datetime
from prepare_july import ROOT,save,texts,ranking
from research import evaluate,gate,digest
DAYS=['2026-07-14','2026-07-15','2026-07-16']
RANK_FILES=['jb4_actual14.json','jb4_actual15.json','jb4_actual16.json']
RANK_URLS=['https://kabu.kininew.net/fiveup/7994.html','https://kabu.kininew.net/fiveup/8006.html','https://kabu.kininew.net/fiveup/8015.html']
SECOND=['https://uiblog.hatenablog.com/entry/2026/07/14/200205','https://uiblog.hatenablog.com/entry/2026/07/15/201932','https://uiblog.hatenablog.com/entry/2026/07/16/210716']
EXPECTED=[['3996','4418','6836','4174','4381','4199','3177','3133','3810','4819'],['4586','3133','278A','1407','581A','5575','7888','9326','4439','5817'],['9238','150A','2354','6572','6505','157A','7581','6033','7138','175A']]
def history(code):
 out={}
 for name in ['jb4_hist_'+code+'.json','jb4_hist_retry_'+code+'.json']:
  file=ROOT/'evidence'/name
  if not file.exists():continue
  t=texts(file)
  for section in re.split(r'\n-{20,}\n',t):
   m=re.search(r'https://96ut.com/stock/jikei\.php\?code='+code+r'(?:&year=2026)?(?=[)\s])',section)
   if not m:continue
   for line in section.splitlines():
    md=re.match(r'L\d+: (2026/07/1[3-6])\s*\|(.+)',line)
    if not md:continue
    close=float(md[2].split('|')[3].strip().replace(',',''))
    out[md[1].replace('/','-')]={'close':close,'url':m[0],'file':name}
 if code in ['2186','3080','464A']:
  extra={'2186':[('jb4_hist2186_find.json','https://minkabu.jp/stock/2186/daily_bar?page=3',True)],'3080':[('jb4_hist_alt_3080.json','https://www.traders.co.jp/stocks/62_3080/historical',False),('jb4_hist3080_find.json','https://www.traders.co.jp/stocks/62_3080/historical',True)],'464A':[('jb4_hist464A_find.json','https://kabumatome.com/stockinfo/464A/',False)]}[code]
  for name,url,first in extra:
   t=texts(ROOT/'evidence'/name)
   if first:t=re.split(r'\n-{20,}\n',t)[0]
   pattern=r'(2026/07/1[3-6])\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)\s*\|\s*([\d,.]+)'
   for md in re.finditer(pattern,t):
    out[md[1].replace('/','-')]={'close':float(md[5].replace(',','')),'url':url,'file':name,'verification':'取得失敗・日付の古い表示を排除し、日付付き保存版のOHLC列から終値を抽出。検索保存版で補完した行は更新後の現行表示と区別。'}
 for day,prev in [('2026-07-14','2026-07-13'),('2026-07-15','2026-07-14'),('2026-07-16','2026-07-15')]:
  if day in out and prev in out:out[day]['previous_close']=out[prev]['close']
 return out
allrows=[];evaluations=[];report=['# 7月予測検証 第4回：2026年7月14・15・16日','',
 '対象：東証普通株の前営業日終値→当日終値の上昇率上位10。各日08:30 JSTを入力締切とした過去再現。',
 '固定モデル：材料点（業績改善5、契約4、商品3、MOU2等）＋前日騰落率/10（-2〜3点）＋S/G市場1点−明示悪材料。材料は初回締切で全点、次の2営業日は半点。欠損前日騰落率は0点。',
 '制約：全東証を網羅せず、前日5%以上表と取得記事掲載株から候補を作成。記事のうち原開示照合未了の銘柄を除外。長期OHLCV・浮動株・板・PTS・マクロの定量採点なし。入力に締切後の情報は入れない。',
 '非盲検：検索結果で将来記事・週次結果が偶発表示された。全て予測入力から除外したが、厳密な未見検証とは言えない。日付付き原開示と当時記事を照合したが第三者の当時アーカイブによる改訂不存在の完全証明ではない。',
 '実績順位は丸め前の騰落率で比較。7/16の7138と175Aは表示上15.97%だが23/144>95/595のためTORICOを9位とする。ETF・地方単独株を除外し、他表の10位圏外から必要銘柄を補完。',
 '監査：採点式とモデルは変更なし。サンリオ共同開発は契約締結を原開示で確認。赤字縮小専用の加点は設けない。東京衡機の監理指定は3月解除済み。記事と短信の数値差は原資料を優先し、材料分類の判断記録を保存。検索結果の将来記事・関連欄・全月結果は予測入力に不採用。','']
for i,(day,file,url) in enumerate(zip(DAYS,RANK_FILES,RANK_URLS)):
 rows=ranking(texts(ROOT/'evidence'/file));rows.sort(key=lambda r:(-(r['change']/(r['close']-r['change'])),r['code']))
 actual=rows[:10];assert [r['code'] for r in actual]==EXPECTED[i]
 for r in rows:
  pct=100*r['change']/(r['close']-r['change']);assert abs(pct-r['return_pct'])<0.011
  r['reported_return_pct']=r['return_pct'];r['return_pct']=pct;r['previous_close']=r['close']-r['change'];r['url']=url
 obj={'date':day,'top10_verified':True,'verification_scope':'二次集計表の市場・順位・算術を別集計表と照合。7/14別表のETF600Aを除外し4819を追加記事で補完。7/16福証9388を除外し7138を日付付き時系列で補完。7138と175Aの表示15.97%同率は丸め前の23/144>95/595で7138が上。全東証原票の再ソートではない。','sources':[url,SECOND[i]]+(['https://note.com/rich_weasel6914/n/n83ae744242e5'] if i==0 else ['https://www.traders.co.jp/stocks/63_7138/historical'] if i==2 else []),'top10':actual}
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
 report += ['',f'実績出典：{url} ／ {SECOND[i]}','補完出典：'+('https://note.com/rich_weasel6914/n/n83ae744242e5' if i==0 else 'https://www.traders.co.jp/stocks/63_7138/historical' if i==2 else '追加不要'),f'封印SHA256：{pred["sha256"]}','']
 save(ROOT/f'results/july_evaluations/{day}.json',e);evaluations.append(e)
hits=sum(e['hits'] for e in evaluations)
baseline=[]
for day,prev,ev in zip(DAYS,['2026-07-13','2026-07-14','2026-07-15'],evaluations):
 previous=json.loads((ROOT/f'data/july_actuals/{prev}.json').read_text())['top10']
 actual=json.loads((ROOT/f'data/july_actuals/{day}.json').read_text())['top10']
 common=sorted({r['code'] for r in previous}&{r['code'] for r in actual})
 baseline.append(dict(date=day,predictions=[r['code'] for r in previous],hit_codes=common,hits=len(common)))
save(ROOT/'results/july_batch04_baseline.json',dict(rule='前営業日の東証普通株上昇率上位10をそのまま予測に使用。実行規約に記録済みの比較基準。',days=baseline,hits=sum(r['hits'] for r in baseline),precision_at_10=sum(r['hits'] for r in baseline)/30))
report+=['## 集計','',f'延べ30予測中{hits}件的中、上位10外{30-hits}件、Precision@10={hits/30:.2%}。順位まで一致{sum(e["exact_rank_hits"] for e in evaluations)}件。的中率は売買収益率ではない。','全30予測の当日終値・前日終値・騰落率を取得。上位10外の正確な全市場順位は未取得として空欄。', '全7月を終えた後に行う詳細な誤差原因分析・改善ルール作成は未着手。次回：7月17・21・22日（20日は海の日で休場）。']
report += ['',f'比較基準（前日上位10を継続選出）：各日{[r["hits"] for r in baseline]}件、合計{sum(r["hits"] for r in baseline)}/30。固定モデルの変更には使わない。']
save(ROOT/'results/july_batch04_summary.json',dict(days=DAYS,evaluations=evaluations,hits=hits,prediction_count=30,precision_at_10=hits/30,cumulative_hits=11+hits,cumulative_prediction_count=120,cumulative_precision_at_10=(11+hits)/120,exact_rank_hits=sum(sum(p["predicted_rank"]==p["actual_rank"] for p in ev["predictions"]) for ev in evaluations),full_tse_universe=False,blind_test=False,all_prediction_actual_prices_retrieved=True,next_days=['2026-07-17','2026-07-21','2026-07-22']))
(ROOT/'results/july_batch04_report.md').write_text('\n'.join(report)+'\n')
with (ROOT/'results/july_batch04_predictions.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]),lineterminator="\n");w.writeheader();w.writerows(allrows)
state=json.loads((ROOT/'results/state.json').read_text());state.update(phase='july_prediction',july_completed_batch=4,july_completed_days=sorted(set(state.get('july_completed_days',[])+DAYS)),next_days=['2026-07-17','2026-07-21','2026-07-22'],requires_user_continue=True,july_predictions_created=True,model_status='frozen',screening_prompt_created=False,error_analysis_started=False);save(ROOT/'results/state.json',state)
files=[ROOT/'data/july_model_frozen.json',ROOT/'data/july_model_v1.json',ROOT/'july_predict.py',ROOT/'results/july_batch04_report.md',ROOT/'results/july_batch04_summary.json',ROOT/'results/july_batch04_predictions.csv',ROOT/'results/july_batch04_baseline.json']
for day in DAYS:
 for group in ['july_predictions','july_scores','july_evaluations']:files.append(ROOT/f'results/{group}/{day}.json')
 files.append(ROOT/f'data/july_inputs/{day}.json');files.append(ROOT/f'data/july_actuals/{day}.json')
files += [ROOT/'build_july_batch04.py',ROOT/'audit_july_batch04.py',ROOT/'finalize_july_batch04.py',ROOT/'results/july_batch04_audit.json']
files += sorted((ROOT/'evidence').glob('jb4_*.json'))
for suffix in ['14','15','16']:
 for group in ['july_releases_','july_events_']:files.append(ROOT/f'data/{group}{suffix}.json')
save(ROOT/'results/july_batch04_manifest.json',{'created_at_utc':datetime.now().astimezone().isoformat(),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
print(json.dumps({'hits':hits,'total':30,'pct':hits/30,'all_prices':True,'cumulative_hits':11+hits,'cumulative_count':120},ensure_ascii=False))
