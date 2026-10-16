import json,re,hashlib,csv
from datetime import datetime
from prepare_july import ROOT,save,texts,ranking
from research import evaluate,gate,digest
DAYS=['2026-07-06','2026-07-07','2026-07-08']
RANK_FILES=['jb2_actual06.json','jb2_actual07_digest08.json','jb2_actual08.json']
RANK_URLS=['https://kabu.kininew.net/fiveup/7937.html','https://kabu.kininew.net/fiveup/7945.html','https://kabu.kininew.net/fiveup/7953.html']
SECOND=['https://stock.f-frontier.com/2026/07/06/234302/','https://uiblog.hatenablog.com/entry/2026/07/07/232547','https://stock.f-frontier.com/2026/07/08/234329/']
EXPECTED=[['3133','4596','264A','4424','3656','584A','504A','4394','1447','278A'],['4591','6522','550A','584A','3625','4199','7360','505A','340A','7477'],['4265','4935','7815','4833','1447','6469','7921','4881','6522','6696']]
def history(code):
 out={}
 files=[ROOT/f'evidence/jb2hist_{code}.json',ROOT/'evidence/jb2_hist_base_retry.json',ROOT/'evidence/jb2_remainingverify.json']
 for file in files:
  if not file.exists():continue
  for section in re.split(r'\n-{20,}\n',texts(file)):
   m=re.search(r'https://96ut.com/stock/jikei\.php\?code='+code+r'(?:&year=2026)?(?=[)\s])',section)
   if not m:continue
   for line in section.splitlines():
    mday=re.match(r'L\d+: (2026/07/0[3678])\s*\|(.+)',line)
    if not mday:continue
    parts=mday[2].split('|');close=float(parts[3].strip().replace(',',''))
    day=mday[1].replace('/','-');out[day]={'close':close,'url':m[0],'file':file.name}
 for day,prev in [('2026-07-06','2026-07-03'),('2026-07-07','2026-07-06'),('2026-07-08','2026-07-07')]:
  if day in out and prev in out:out[day]['previous_close']=out[prev]['close']
 return out
allrows=[];evaluations=[];report=['# 7月予測検証 第2回：2026年7月6・7・8日','',
 '対象：東証普通株の前営業日終値→当日終値の上昇率上位10。各日08:30 JSTを入力締切とした過去再現。',
 '固定モデル：材料点（業績改善5、契約4、商品3、MOU2等）＋前日騰落率/10（-2〜3点）＋S/G市場1点−明示悪材料。材料は初回締切で全点、次の2営業日は半点。欠損前日騰落率は0点。',
 '制約：全東証を網羅せず、前日5%以上表と取得記事掲載株から候補を作成。記事のうち原開示照合未了の銘柄を除外。長期OHLCV・浮動株・板・PTS・マクロの定量採点なし。入力に締切後の情報は入れない。',
 '非盲検：検索結果で将来記事・週次結果が偶発表示された。全て予測入力から除外したが、厳密な未見検証とは言えない。日付付き原開示と当時記事を照合したが第三者の当時アーカイブによる改訂不存在の完全証明ではない。',
 '監査：7/7締切前の6522製品展開リリースは7/7入力で取得漏れ。7/8作業で収集し、7/7の保存済み予測は変更していない。7/8ではproduct分類を初回適格7/7として半点採用。','']
for i,(day,file,url) in enumerate(zip(DAYS,RANK_FILES,RANK_URLS)):
 rows=ranking(texts(ROOT/'evidence'/file));rows.sort(key=lambda r:-(r['change']/(r['close']-r['change'])))
 actual=rows[:10];assert [r['code'] for r in actual]==EXPECTED[i]
 for r in rows:
  pct=100*r['change']/(r['close']-r['change']);assert abs(pct-r['return_pct'])<0.011
  r['reported_return_pct']=r['return_pct'];r['return_pct']=pct;r['previous_close']=r['close']-r['change'];r['url']=url
 obj={'date':day,'top10_verified':True,'verification_scope':'二次集計表の市場・順位・算術を確認。別集計表と照合。7/6は9170除外後278Aを別表で補充、7/8は9170除外後6696を別表で補充。7/7は別表に全市場10位までしかなく340A・7477の価格を別日足表でも確認。全東証原票の再ソートではない。','sources':[url,SECOND[i]],'top10':actual}
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
report+=['## 集計','',f'延べ30予測中{hits}件的中、上位10外{30-hits}件、Precision@10={hits/30:.2%}。順位まで一致0件。的中率は売買収益率ではない。','全30予測の当日終値・前日終値・騰落率を取得。上位10外の正確な全市場順位は未取得として空欄。', '全7月を終えた後に行う詳細な誤差原因分析・改善ルール作成は未着手。次回：7月9・10・13日。']
save(ROOT/'results/july_batch02_summary.json',dict(days=DAYS,evaluations=evaluations,hits=hits,prediction_count=30,precision_at_10=hits/30,cumulative_hits=4+hits,cumulative_prediction_count=60,cumulative_precision_at_10=(4+hits)/60,exact_rank_hits=sum(sum(p["predicted_rank"]==p["actual_rank"] for p in ev["predictions"]) for ev in evaluations),full_tse_universe=False,blind_test=False,all_prediction_actual_prices_retrieved=True,next_days=['2026-07-09','2026-07-10','2026-07-13']))
(ROOT/'results/july_batch02_report.md').write_text('\n'.join(report)+'\n')
with (ROOT/'results/july_batch02_predictions.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
state=json.loads((ROOT/'results/state.json').read_text());state.update(phase='july_prediction',july_completed_batch=2,july_completed_days=sorted(set(state.get('july_completed_days',[])+DAYS)),next_days=['2026-07-09','2026-07-10','2026-07-13'],requires_user_continue=True,july_predictions_created=True,model_status='frozen',screening_prompt_created=False,error_analysis_started=False);save(ROOT/'results/state.json',state)
files=[ROOT/'data/july_model_frozen.json',ROOT/'data/july_model_v1.json',ROOT/'july_predict.py',ROOT/'results/july_batch02_report.md',ROOT/'results/july_batch02_summary.json',ROOT/'results/july_batch02_predictions.csv']
for day in DAYS:
 for group in ['july_predictions','july_scores','july_evaluations']:files.append(ROOT/f'results/{group}/{day}.json')
 files.append(ROOT/f'data/july_inputs/{day}.json');files.append(ROOT/f'data/july_actuals/{day}.json')
save(ROOT/'results/july_batch02_manifest.json',{'created_at_utc':datetime.now().astimezone().isoformat(),'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}})
print(json.dumps({'hits':hits,'total':30,'pct':hits/30,'all_prices':True,'rows':allrows,'cumulative_hits':4+hits,'cumulative_count':60},ensure_ascii=False))
