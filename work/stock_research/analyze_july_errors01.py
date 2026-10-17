"""Post-hoc diagnostic review; never writes sealed forecasting artifacts."""
import csv,json,hashlib
from collections import Counter
from datetime import datetime,timezone
from prepare_july import ROOT,save

DAYS=['2026-07-01','2026-07-02','2026-07-03']
NEXT=['2026-07-06','2026-07-07','2026-07-08']

# These are research annotations, not revised model inputs or causal labels.
# References to an input below preserve its contemporaneous scope and limitations.
PRED_NOTES={
 '01':{
 '6522':('hit','RFID展開の初回材料3点と前日29.13%で採用、17.29%上昇し的中。翌日の反応や寄付での購入可能性まで保証しない。'),
 '192A':('rank_target','翌期経常149.5%増見通し・初配当という原材料は確認済み。11.60%上昇したが当日10位16.26%に未達。方向予測の失敗とは区別。'),
 '3494':('coarse_material','経常予想の増額は2.5%で、増額後も前年比減益。業績改善を一律5点とするため高順位だが、上昇は2.27%。小幅修正と大幅修正を同点にする設計上の区別不足。'),
 '4424':('earnings_quality','主因は新株予約権戻入益で営業改善ではない。固定ルールではearnings_up5点、14.63%上昇したが上位10外。補助対象採択も引け記事にあるが、寄与率は分離不能。'),
 '5967':('hit','業績上方修正・増配を確認し採用、19.23%上昇して的中。材料の存在が同点銘柄全ての的中を意味しない対照例。'),
 '7487':('coarse_material','経常670→808百万円への修正で5点。前日騰落率欠損のまま同点コード順で採用し、結果は1.02%上昇。期待との差や投資家反応を計測していない。'),
 '9253':('expectation_unknown','第1四半期経常3.8%増・通期修正なしに5点、結果は10.03%下落。高進捗から上方修正期待があったかは未計測で、失望売りとは断定しない。'),
 '2685':('expectation_unknown','第1四半期経常増益を5点としたが2.74%下落。コンセンサス・既存店動向等を比較しておらず、増益と株価サプライズを同一視できない。'),
 '2926':('coarse_material','復配3円を4点、市場1点で採用したが終値101円のまま。復配という分類は正しくても、配当の新規性・事前期待・売買需給は定量入力にない。'),
 '2975':('expectation_unknown','中間経常増益を5点で採用したが10.19%下落。利益の前年対比だけでは市場期待との差を説明できず、織り込みや利益確定は仮説に留める。'),
 },
 '02':{
 '5942':('reaction_lag','7/1 14:00発表後に当日16.26%上昇。翌朝に新鮮な材料5点と前日上昇点を重ねて1位としたが、7/2は9.37%下落。朝の初回採用日と市場の初回反応日が異なる設計上の問題。売却動機は不明。'),
 '9425':('reaction_lag','前日30.30%上昇の勢い3点と7/1のネクスト・セキュリティ基本合意2点で採用し2.33%下落。前日上昇の報道材料は6/30蓄電池権利取得で、別材料を混同しない。'),
 '464A':('earnings_quality','経常600→1100百万円だが補助金計上前倒し等で営業赤字は残る。5点で採用し3.93%上昇、上位10外。経常増額の質・継続性を分けない設計。'),
 '4918':('hit','経常200→330百万円への増額を初回5点で採用、18.98%上昇し的中。業績改善の全例が外れたわけではない。'),
 '7781':('rank_target','経常1349→1778百万円の増額を5点で採用。11.48%上昇したが10位15.28%に未達。良い方向と上位10の相対順位は別。'),
 '6573':('impact_scale','広告運用受託をcontract4点。原資料で業績影響軽微と確認していたが減点規則がなく、前日8%の勢いと併せ採用、結果7.41%下落。契約金額・利益寄与の区別不足。'),
 '5967':('continuation','前日の的中後、半減した材料2.5点と前日19.23%の勢いで再採用、3.23%下落。1日の継続仮定が外れた事実は確認できるが、反落の売却主体は不明。'),
 '4167':('rank_target','千葉信金のシステム採用をcontract4点とした。4.98%上昇したが15.28%の境界に未達。表の5%以上掲載基準と上位10判定も混同しない。'),
 '4496':('impact_scale','提携・サービス開始の最大4点を採用。業績影響軽微と確認していたが加点は同じで、上昇は1.32%。契約の存在と短期利益インパクトを分ける必要がある。'),
 '6239':('impact_scale','子会社受注約5.7億円、納期2027年4月をcontract4点で採用。0.23%上昇に留まる。将来納期・利益率・既存受注残対比は採点にない。'),
 },
 '03':{
 '7063':('reaction_lag','蓄電池設備の7/2 11:30発表と当日39.47%上昇を翌朝初回3点＋勢い上限3点で採用したが18.87%下落。場中反応済み材料を翌朝も全点とする問題を確認。'),
 '2438':('reaction_lag','7/2公式導入事例と10:54報道、当日18.65%上昇を受け採用し3.52%下落。入力は日付精度で7/2末だが、実際の報道は場中で初回反応済み。'),
 '7602':('acquisition_lag','7/1 17:20の契約を7/2には取得できず、7/3には半点2点と前日35.46%の勢いで採用して13.09%下落。取得の遅れと反応日のずれを分ける。'),
 '2493':('coarse_material','中間経常119.6%増・通期据置を5点。0.54%上昇に留まり、増益率だけでは上位10を予測できなかった。市場期待比は未取得。'),
 '3549':('rank_target','翌期増益・増配を5点。1.30%上昇したが10位16.40%に未達。原英語短信のTokyo Standardを保持し、市場区分を現在の思い込みで変更しない。'),
 '4918':('continuation','前日的中後、材料半点2.5と勢い1.898で再採用。0.57%上昇で上位10外。前日と同じ材料でも翌日の順位は続かなかった。'),
 '6522':('continuation','6/30公表RFID材料の半点1.5と前日25.64%の勢いで再採用、0.51%下落。短い継続モデルの限界であり、規制や買い戻しが原因とは未確認。'),
 '4187':('expectation_unknown','原英語資料の上期・通期増額で5点。0.17%下落し上位10外。市場期待・寄付価格・セクター調整後の超過収益を未取得。'),
 '4596':('hit','契約対価入金を4点で採用、52.63%上昇し実績1位。ただし返金条件があり即時収益確定と同義ではない。別のマイルストーン銘柄との値動き差は原因未確定。'),
 '4890':('impact_scale','最終マイルストーン達成だが業績織込済み・影響軽微を原資料で確認。contract4点で採用し1.24%下落。入金/開発進展の見出しだけでは利益サプライズを測れない。'),
 }}

# timing denotes the identified event only, not every possible signal for a stock.
WINNER_NOTES={
 '01':{
 '4833':('known_before_cutoff','material_capture','6/30 16:00の業績予想公表は当時の取得済みダイジェストにも載っていたが、入力には原開示・材料が未付与。今回原PDFで経常172～2513百万円を確認。勢いのみ2.212点では24位。情報未公開ではなく材料照合・反映漏れ。',['def','digest01']),
 '9425':('known_before_cutoff','universe_capture','6/30 18:00企業発信で蓄電池設備・土地の権利取得を確認したが当日候補に不在。長期保有運用目的ではなく権利譲渡による収益化であり、7/1・2の別会社株式取得MOUと区別。',['reyuu']),
 '7041':('after_cutoff','intraday_event','優待導入の原PDFは7/1日付、開示一覧15:00と当時15:50記事で場中公表を確認。08:30にはこの新材料は利用不可。他の予兆まで存在しなかったとは断定しない。',['crg']),
 '7815':('older_event_reported','material_capture','候補14位、前日26.14%の勢いのみ3.614点。6/26不動産売却・特別利益の当時報道はあるが入力に材料なし。原開示の独立再確認は未了で、材料不足と持続性の仮説を分ける。',['old_news']),
 '589A':('known_ipo_date_secondary','universe_design','6/30上場のIPO翌日。前日の初値・終値はあっても前々日の終値がなく、前日比5%以上表では拾いにくい。取得ニュース側も補完しなかった。IPO継続枠の網羅性不足、公開価格比を前日比へ代入しない。',['stop01']),
 '7063':('timing_unresolved','universe_unknown','候補不在。7/1の事務所設立について企業発信は確認できるが公開時刻未確定。7/2の蓄電池開示を1日の原因へ遡って使わない。1日の上昇原因・朝の利用可能性は未確定。',['birdman_old']),
 '3436':('timing_unresolved','sector_coverage','候補不在。引け後の材料表は半導体テーマへの波及と説明するが、朝の海外材料・セクター感応度を独立検証していない。テーマは事後仮説で買い需要の因果は不明。',['stop01']),
 '5942':('after_cutoff','intraday_event','7/1 14:00の業績修正を原開示・一覧・当時記事で確認。朝の入力外の場中材料。翌2日には取得できたが予測1位から反落した。',['filcon']),
 },
 '02':{
 '7063':('after_cutoff','intraday_event','候補20位、前日18.75%の勢いのみ2.875点。蓄電池設備完工・運用開始は7/2 11:30開示で当日朝には不可。候補内順位不足と場中新材料を分ける。',['birdman']),
 '7602':('known_before_cutoff','universe_capture','7/1 17:20契約開示は7/2朝に利用可能だったが候補不在。旧記録も取得漏れを明記しており、原開示は3日準備時に補完済み。翌朝公表不能ではない。',['redax']),
 '9941':('known_before_cutoff','universe_capture','7/2 07:30の企業発信で6/30決議後の堀江氏取締役就任を確認。候補不在で、朝の企業PRの取得範囲不足。就任の発生日と発信時刻を区別し、因果の全説明とはしない。',['taiyo']),
 '6522':('known_before_cutoff','freshness_rule','候補15位4.229点。RFID材料3点が翌日1.5点に減り、当日最下位採用5点を下回った。材料は確認済みで取得漏れではなく半減規則と選出順位の問題。',['asterisk']),
 '4935':('after_cutoff_reissued_product','intraday_event','候補不在。7/2 12:00の企業PRで電動ファンウェアを確認したが発売自体は5月から順次。朝にはこの発信は使えず、新発売の初報とも断定しない。上昇との因果は未確定。',['liberta']),
 '3070':('timing_unresolved','universe_unknown','候補不在。7/2付独占販売契約の検索結果はあるが、元の原開示本文・初回公表時刻を本回では確認できず、当日朝に使えたとの判定を留保する。',['search_contract']),
 '2438':('first_publication_unresolved_intraday_report','intraday_event','候補不在。7/2公式事例と当日10:54記事で採用の報道を確認。原ページは日付のみで初回公開時刻不明、少なくとも既存の朝入力適格性は未立証。翌朝には使用可。',['asukanet']),
 '7376':('timing_unresolved','universe_unknown','候補不在。確認した当日ストップ高表も材料不明。低時価総額という属性だけでは上昇原因を特定できず、買い煽り・踏み上げと断定しない。',['stop02']),
 '7878':('timing_unresolved','momentum_underweighted','候補48位1.657点、前日6.57%の勢い以外は材料なし。新規材料の初回時刻は確認できず、過去好業績・需給の説明は仮説。モデルがこの継続上昇を低く採点した事実を記録。',['search_misc']),
 },
 '03':{
 '3133':('timing_unresolved','universe_unknown','候補不在。個人集計に著名投資家への言及があるが、本人の当時投稿と時刻を確認していない。SNS起点の需給説を事実として採用しない。',['stop03']),
 '9425':('known_before_cutoff','taxonomy_weight','あいプロの非拘束MOUを2点、市場1点で候補17位3点。7/1のネクスト・セキュリティMOUと独立した発表。確定買収3点へ事後変更せず、MOU配点が相対順位を押し下げたことを記録。',['reyuu_mou']),
 '6634':('timing_unresolved','momentum_underweighted','候補47位1.806点、前日8.06%の勢いのみ。今回照合した資料で当日上昇の確定材料を同定できず、需給・心理の断定を保留。',[]),
 '2492':('known_before_cutoff_secondary','material_capture','候補150位0.526点。7/2 16:01提出・16:04記事のオアシス5.07%保有は取得済み朝ニュースにもあるが入力に未付与。原EDINET本文は本回未取得のため二次照合の暫定判定。義務発生日6/25を公表日としない。',['oasis','digest03']),
 '9444':('timing_unresolved','universe_unknown','候補不在。複数の当日表で上昇を確認できても、値動きを説明する日時付き原材料は今回未同定。情報不足のまま保持。',['stop03']),
 '504A':('known_before_cutoff','taxonomy_missing','FDAのIND審査完了・治験組入れ承認は原開示確認済みだが、製品販売承認ではなく専用分類がなくunknown0点。候補25位2.184点。分類の未整備と正しい承認段階の区別を両方保持。',['innova']),
 '4575':('timing_unresolved','universe_unknown','候補不在。6/30赤字拡大見通しは取得記事にあるが3日ニュース候補へ持ち越されず。当日材料表も不明。悪材料下の上昇を楽観・買い戻しで説明しない。',['digest01','stop03']),
 '4935':('known_before_cutoff','material_capture','候補15位3.32点、前日23.20%と市場点だけ。7/2正午の製品PRは翌朝には利用可能だったが材料未反映。ただし5月から発売の再告知で、固定ルールの新規材料加点対象かは未確定。',['liberta']),
 '6166':('known_before_cutoff','older_material_capture','候補23位2.431点、前日14.31%の勢いのみ。今回6/26原開示でZeo Nextと芝浦工大の研究を照合。7/3は初回適格6/29から4営業日経過し、仮に入力しても固定鮮度規則の加点0。取得補完だけで的中が増えるとはいえない。',['nakamura']),
 }}

SOURCES={
 'def':('evidence/je1_primary_checks.json','https://tdnet-pdf.kabutan.jp/20260630/140120260626581691.pdf','2026-06-30T16:00:59+09:00','原PDF＋当時記事。レンジ中央値を確定値としない。'),
 'digest01':('evidence/july_start_j1_inputs02.json','https://s.kabutan.jp/news/n202606301113/','2026-06-30T20:00:59+09:00','保存済み当時ニュースで4833の掲載確認。'),
 'reyuu':('evidence/je1_primary_discovery.json','https://prtimes.jp/main/html/rd/p/000000091.000111823.html','2026-06-30T18:00:59+09:00','企業発信。TDnet一覧は16:00、ここでは確認したPR18:00を採用。'),
 'crg':('evidence/je1_timing_verification.json','https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260701/20260630584902.pdf','2026-07-01T15:00:59+09:00','原PDF＋取得一覧と当時記事。'),
 'old_news':('evidence/je1_market_context.json','https://s.kabutan.jp/news/n202606290017/','2026-06-29','当時記事による二次確認、原開示再照合未了。'),
 'stop01':('evidence/je1_context.json','https://kabu.kininew.net/stopdaka/7905.html','2026-07-01','当日後の個人集計。材料欄は因果の証明ではない。'),
 'stop02':('evidence/je1_context.json','https://kabu.kininew.net/stopdaka/7913.html','2026-07-02','当日後の個人集計、材料不明を保持。'),
 'stop03':('evidence/je1_followup_search.json','https://kabu.kininew.net/stopdaka/7921.html','2026-07-03','当日後の個人集計、SNS原投稿は未照合。'),
 'birdman_old':('evidence/je1_older_events.json','https://birdman.tokyo/news-category/entertainment-next/','2026-07-01 date only','企業ページで設立日確認。公開時刻と独立した初回本文版は不明。'),
 'taiyo':('evidence/je1_primary_bodies.json','https://prtimes.jp/main/html/rd/p/000000003.000186427.html','2026-07-02T07:30:59+09:00','企業発信。6/30決議と7/2公表を区別。'),
 'liberta':('evidence/je1_primary_bodies.json','https://prtimes.jp/main/html/rd/p/000000268.000052173.html','2026-07-02T12:00:59+09:00','企業発信。発売は5月から、7/2を発売初日としない。'),
 'oasis':('evidence/je1_timing_verification.json','https://s.kabutan.jp/news/n202607020904/','2026-07-02T16:04:59+09:00','同時代記事＋提出時刻別表、原EDINET未取得。義務発生日6/25とは別。'),
 'digest03':('evidence/july2post1.json','https://s.kabutan.jp/news/n202607030100/','2026-07-03T07:30:59+09:00','予測準備時に保存された朝ニュース。2492の見出しを確認。'),
 'search_contract':('evidence/je1_primary_links.json','https://finance.yahoo.co.jp/quote/3070.T/disclosure',None,'原契約本文・初回公表時刻未照合、検索候補のみ。'),
 'search_misc':('evidence/je1_market_context.json','https://news.livedoor.com/article/detail/31718292/',None,'当日の上昇確認、材料の確定には使わない。'),
 'nakamura':('evidence/je1_primary_bodies.json','https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260626/20260626581913.pdf','2026-06-26T15:30:59+09:00','原PDF＋開示一覧。初回適格日は6/29、7/3は年齢4で0点。'),
}
# Original evidence for these events was acquired during prediction work.
for key,day,code in [('filcon','02','5942'),('birdman','03','7063'),('redax','03','7602'),('asterisk','01','6522'),('asukanet','03','2438'),('reyuu_mou','03','9425'),('innova','03','504A')]:
 rel=json.loads((ROOT/f'data/july_releases_{day}.json').read_text())[code]
 SOURCES[key]=(f'data/july_releases_{day}.json',rel['url'],rel['at'],rel['verified_by'])

def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 records=[];daily=[];all_refs=set();observed=Counter()
 for day in DAYS:
  short=day[-2:];inp=read(f'data/july_inputs/{day}.json');s=read(f'results/july_scores/{day}.json');ev=read(f'results/july_evaluations/{day}.json');actual=read(f'data/july_actuals/{day}.json')['top10']
  lookup={r['code']:(i+1,r) for i,r in enumerate(s['candidates'])};rejected={r['code'] for r in s['rejected_candidates']};boundary=min(r['return_pct'] for r in actual);threshold=s['candidates'][9]['score'];fp=[r for r in ev['predictions'] if r['actual_rank'] is None]
  present=sum(r['code'] in lookup for r in actual);miss=Counter()
  for r in ev['predictions']:
   c=lookup[r['code']][1];kind,note=PRED_NOTES[short][r['code']];is_hit=r['actual_rank'] is not None
   status='hit' if is_hit else 'false_positive';observed[status]+=1
   records.append(dict(date=day,role='prediction',status=status,code=r['code'],name=r['name'],predicted_rank=r['predicted_rank'],actual_rank=r['actual_rank'],candidate_rank=lookup[r['code']][0],score=c['score'],components=c['components'],previous_return_pct=c['previous_return_pct'],missing_momentum=c['missing_momentum'],actual_return_pct=r['actual_return_pct'],top10_return_boundary_pct=boundary,return_gap_to_boundary_pct=r['actual_return_pct']-boundary,mechanism=kind,observation=note,identified_event_timing='see_sealed_evidence',timing_applies_to_event_only=True,economic_cause_status='not_identified',hypothesis='材料種別・鮮度・期待差・市場反応の区別が必要。売却動機と寄与率は未確定。',evidence_files=[f'data/july_inputs/{day}.json',f'results/july_evaluations/{day}.json'],source_ids=[],sources=[e for e in inp['evidence'] if e['id'] in c['evidence_ids']]))
  for rank,r in enumerate(actual,1):
   cr,c=lookup.get(r['code'],(None,None));is_hit=cr is not None and cr<=10
   stage='selected' if is_hit else 'eligible_below_top10' if c else 'rejected_unverified' if r['code'] in rejected else 'absent_from_union'
   if not is_hit:miss[stage]+=1;observed['false_negative']+=1
   if is_hit:timing='known_before_cutoff';kind,note=PRED_NOTES[short][r['code']];refs=[]
   else:timing,kind,note,refs=WINNER_NOTES[short][r['code']]
   all_refs.update(refs)
   records.append(dict(date=day,role='actual_top10',status='hit' if is_hit else 'false_negative',code=r['code'],name=r['name'],predicted_rank=cr if is_hit else None,actual_rank=rank,candidate_rank=cr,score=c['score'] if c else None,components=c['components'] if c else None,previous_return_pct=c['previous_return_pct'] if c else None,missing_momentum=c['missing_momentum'] if c else None,actual_return_pct=r['return_pct'],top10_return_boundary_pct=boundary,score_gap_to_tenth=threshold-c['score'] if c else None,selection_stage=stage,mechanism=kind,observation=note,identified_event_timing=timing,timing_applies_to_event_only=True,economic_cause_status='not_identified',hypothesis='未取得情報・場中材料・分類不足・需給/地合いを区別し、未照合の因果は保留。',evidence_files=[f'data/july_inputs/{day}.json',f'results/july_scores/{day}.json',f'data/july_actuals/{day}.json']+[SOURCES[k][0] for k in refs],source_ids=refs,sources=[dict(url=SOURCES[k][1],published_at=SOURCES[k][2],verification=SOURCES[k][3]) for k in refs]))
  daily.append(dict(date=day,hits=ev['hits'],false_positives=len(fp),false_negatives=10-ev['hits'],eligible_winners=present,candidate_recall=present/10,missed_winner_stages=dict(miss),score_threshold=threshold,top10_return_boundary_pct=boundary,false_positive_up=sum(r['actual_return_pct']>0 for r in fp),false_positive_flat=sum(r['actual_return_pct']==0 for r in fp),false_positive_down=sum(r['actual_return_pct']<0 for r in fp),missing_momentum_in_predictions=sum(lookup[r['code']][1]['missing_momentum'] for r in ev['predictions'])))
 summary=dict(days=DAYS,analysis_batch=1,analyzed_sessions=3,prediction_count=30,hits=4,false_positives=26,false_negatives=26,error_records=52,record_count=len(records),eligible_winners=sum(d['eligible_winners'] for d in daily),candidate_recall=sum(d['eligible_winners'] for d in daily)/30,missed_winner_stages=dict(sum((Counter(d['missed_winner_stages']) for d in daily),Counter())),false_positive_up=sum(d['false_positive_up'] for d in daily),false_positive_flat=sum(d['false_positive_flat'] for d in daily),false_positive_down=sum(d['false_positive_down'] for d in daily),daily=daily,model_modified=False,sealed_artifacts_modified=False,causal_attribution_proven=False,full_tse_universe=False,blind_test=False,screening_prompt_created=False,next_days=NEXT)
 save(ROOT/'results/july_error_batch01_cases.json',dict(note='予測30件と実績上位10の30件を役割別に記録。的中4件は両方に現れ、誤りはFP26＋FN26＝52件。candidate_rankは部分母集団の採点順位であり全市場順位ではない。',records=records))
 save(ROOT/'results/july_error_batch01_summary.json',summary)
 save(ROOT/'results/july_error_batch01_sources.json',dict(note='分析時に新取得した資料は診断専用。原公表日時と取得時刻を区別し、予測へ遡及投入しない。検索結果・AI要約だけで原開示照合済みとしない。',sources={k:dict(file=v[0],url=v[1],published_at=v[2],verification=v[3]) for k,v in SOURCES.items()}))
 flat=[]
 for r in records:
  flat.append({k:(json.dumps(r[k],ensure_ascii=False) if isinstance(r[k],(dict,list)) else r[k]) for k in ['date','role','status','code','name','predicted_rank','actual_rank','candidate_rank','score','components','previous_return_pct','missing_momentum','actual_return_pct','top10_return_boundary_pct','mechanism','identified_event_timing','economic_cause_status','observation','evidence_files','source_ids']})
 with (ROOT/'results/july_error_batch01_cases.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(flat[0]),lineterminator='\n');w.writeheader();w.writerows(flat)
 report=['# 7月不的中原因分析 第1回：7月1・2・3日','',
 '全7月予測比較の完了後に行った事後診断。各日の予測10件と実績上位10を全件レビューし、上位10外26件（FP）と見逃し26件（FN）を保存。的中は既存の4/30（13.33%）のまま。モデル・入力・封印・実績・月間集計は変更しない。',
 '確定できるのは選出過程と材料の日時・内容であり、価格を動かした投資家の動機や寄与率ではない。織り込み・失望・利益確定・踏み上げ・SNS買い等は証拠がなければ不明とする。場中新材料も、その株が朝に予測不可能だったことを意味しない。','',
 '## 確認した結果','',
 '|日付|的中|候補内の実績上位株|候補内で採点落ち|候補不在|上位10外：上昇/横ばい/下落|','|---|---:|---:|---:|---:|---:|']
 for d in daily:report.append(f'|{d["date"]}|{d["hits"]}/10|{d["eligible_winners"]}/10|{d["missed_winner_stages"].get("eligible_below_top10",0)}|{d["missed_winner_stages"].get("absent_from_union",0)}|{d["false_positive_up"]}/{d["false_positive_flat"]}/{d["false_positive_down"]}|')
 report += ['', '見逃し26件は候補内11件・候補不在15件。原資料未照合として除外された候補からの見逃しは0件だった。ただし価格表由来の採用候補でも、4833のようにニュース原資料未照合で材料点が抜ける例がある。候補集合に実績上位株15/30（50.00%）しか含まれず、採点を完璧にしても同じ候補集合では日別4・4・7件が的中上限になる。この値は事後的な候補被覆率で、改善モデルの成績ではない。',
 '上位10外26件中12件は上昇、1件横ばい、13件下落。上昇方向を当てることと上昇率上位10に入ることを分ける。当日の10位境界は7/1=16.2602%、7/2=15.2760%、7/3=16.3955%。全市場の正確な圏外順位は推定しない。','',
 '## 誤りが起きた過程','',
 '1. **材料取得と入力への反映**：4833の6/30業績見通しは取得済み記事に掲載されていたが、材料点が入らず候補24位。9425の6/30権利取得、7602の7/1契約、9941の7/2朝PRも各日の候補に不在。2492の7/2大量保有報告は取得済み朝ニュースにあるが材料未付与（原EDINET未取得の二次確認）。単純なウェイト調整では候補不在を直せない。',
 '2. **場中発表と朝の制約**：7041の7/1 15:00優待導入、5942の同日14:00修正、7063の7/2 11:30蓄電池発表は各日08:30後。2438は7/2 10:54報道まで確認できるが原ページ初回時刻不明。4935の7/2正午PRも当日朝の入力外で、発売自体は5月から。公開後の情報を朝に持ち込んで改善成績を作らない。',
 '3. **初回採用日と初回反応日のずれ**：5942と7063/2438は場中に株価が動き、翌朝は材料全点と前日勢いを重ねたが反落。6522は7/2には半減規則で候補15位に落ちたのに上昇し、7/3は前日勢いで再採用して下落。固定の鮮度減衰と勢いが反応の持続・反転を区別していない。これは確認できる構造であり、反落を利益確定売りと断定する証拠ではない。',
 '4. **材料の質と規模を捨てる採点**：3494の小幅経常増額も大幅修正も業績改善5点。4424の戻入益・464Aの補助金など、本業利益との区別が得点へ反映されない。6573・4496・4890は原資料の影響軽微/織込済みを確認しても契約4点。対照的に4596は同じ4点で大幅高となり、利益影響の弱さだけで一律除外できるとの結論も出せない。',
 '5. **分類と母集団設計**：504Aの治験進展は製品承認でなくunknown0点、9425の非拘束MOUは2点。正しい段階区分を守りつつ分類不足を今後の研究課題とする。589AのIPO翌日は前日比表だけでは取得しにくい。6166の6/26研究開示を今回補完しても、7/3は鮮度年齢4で固定規則の材料0点となる。',
 '6. **データ品質と識別限界**：固定コードの算術と価格を再照合し、今回の対象で修正を要する価格不整合は検出していない。既存の7/3不完全窓による無効旧封印・補完経緯は第1回報告書どおり保持。取得漏れを後知恵で埋めず、7/24説明文正誤も保持。順位を付けられることは経済的原因が判明したことを意味しない。','',
 '## 地合い・需給・心理','',
 '引け後の別集計によると7/1は日経平均上昇でも東証プライム値上がり677対値下がり831、7/2は日経平均下落でもTOPIX上昇・値上がり1215対値下がり314、7/3は値上がり1226対値下がり291。指数一つで全銘柄の失敗を説明できない。これは事後の参考情報で、当日朝の入力にしない。出典：[7/1](https://uiblog.hatenablog.com/entry/2026/07/01/183242)・[7/2](https://uiblog.hatenablog.com/entry/2026/07/02/205304)・[7/3](https://uiblog.hatenablog.com/entry/2026/07/04/104206)（evidence/je1_market_context.json・je1_final_checks.json）。独立した指数原票の再計算は未実施。',
 '海帆の著名投資家言及やSUMCOの半導体テーマは二次表の説明に留まる。投資主体、浮動株、信用残の時点別データ、板・寄付、出来高の平常比、海外材料との時刻整合を網羅していないため、需給・心理・マクロを確定原因にしない。BCC・トーシン・CANBAS等の原因不明も記録する。約定終値は全30予測で既存確認済みだが、ストップ高銘柄の寄付購入可能性や費用後収益は未検証。','']
 for day in DAYS:
  report += [f'## {day}：予測10件','', '|予測順位|コード・銘柄|得点|騰落率|実績|診断|','|---:|---|---:|---:|---|---|']
  for r in records:
   if r['date']==day and r['role']=='prediction':report.append(f'|{r["predicted_rank"]}|{r["code"]} {r["name"]}|{r["score"]:g}|{r["actual_return_pct"]:+.2f}%|{r["actual_rank"] or "上位10外"}|{r["observation"]}|')
  report += ['', '### 実績上位10と見逃しの内訳','', '|実績順位|コード・銘柄|候補内採点順位・得点|判定|診断と時刻|','|---:|---|---|---|---|']
  for r in records:
   if r['date']!=day or r['role']!='actual_top10':continue
   candidate=f'{r["candidate_rank"]}位 / {r["score"]:g}点' if r['candidate_rank'] else '候補不在';refs=' '.join('['+k+']('+SOURCES[k][1]+')' for k in r['source_ids'])
   report.append(f'|{r["actual_rank"]}|{r["code"]} {r["name"]}|{candidate}|{"的中" if r["status"]=="hit" else "見逃し"}|{r["observation"]} {refs}|')
  report.append('')
 report += ['## 今後検証する仮説（未実装）','',
 'まず原開示・企業PR・EDINET・IPOを日付で網羅照合し、記事にはあるが材料点がない銘柄を検知する。取得不能・分類対象外・本当の候補不在を別フラグにする。次に、公表から最初の場中反応までの時間と翌朝までの累積反応を保持し、初回朝採用だけで鮮度を決める方法と比較する。材料の利益段階・反復性・影響軽微・通期据置・非拘束性を記述する。',
 'これらは今回の結果を見て得た仮説で、同じ7月期間で調整し改善を実証したとはしない。7月の全分析後に候補ルールを明文化し、新しい期間で別途評価する。現行モデル・封印・成績は固定する。スクリーニング用プロンプトは未作成。','',
 '## 保存と次回','',
 'july_error_batch01_cases.json / CSVは60役割行（FP26・FN26・的中4×2）、summary.jsonは日別集計、sources.jsonは出典と未確認範囲、audit.json / manifest.jsonは整合性監査。各行のsourcesには当時の予測根拠または診断用出典を保存。新規取得の保存時刻はacquisition_ledgerに分離。',
 '今回で不的中原因分析は3/22営業日完了。このチャットの処理完了回数4/7。次は7/6・7・8の分析で続行回答待ち。','']
 (ROOT/'results/july_error_batch01_report.md').write_text('\n'.join(report))
 state=read('results/state.json');state.update(phase='july_error_analysis',requires_user_continue=True,error_analysis_started=True,error_analysis_completed_batch=1,error_analysis_completed_days=DAYS,next_days=NEXT,screening_prompt_created=False);save(ROOT/'results/state.json',state)
 chat=read('results/chat_handoff_state.json');chat.update(completed_batches_in_chat=4,completed_batch_ids_in_chat=['july_prediction_batch06','july_prediction_batch07','july_prediction_batch08','july_error_analysis_batch01'],next_authorized_batch=[],handoff_prepared=False,note='予測第6・7・8回と原因分析第1回を完了し4/7。次は7/6・7・8の原因分析で続行回答待ち。');save(ROOT/'results/chat_handoff_state.json',chat)
 print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':run()
