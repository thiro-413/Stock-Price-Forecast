import json,re
from prepare_july import *
r=json.loads((ROOT/'data/july_releases_02.json').read_text());events=json.loads((ROOT/'data/july_events_02.json').read_text())
times={c:'15:30' for c in ['2493','3549','4187','6136','4890','4596','5242']};times.update({'504A':'16:00','9425':'16:00','7063':'11:30'})
notes={'2493':'中間経常144百万円119.6%増、通期修正なし。','3549':'翌期経常増益・増配。原開示でTokyo Standard確認。','4187':'日本語PDF文字化けのため同時開示英語原本で上期・通期増額確認。','6136':'中間経常10850→17100百万円。','4890':'最終マイルストーン達成、業績織込済み・影響軽微。','4596':'契約に基づく対価入金。即時の収益認識とは異なり返金条件あり。','504A':'FDAの治験組入れ承認、製品販売承認ではない。固定モデルに治験進展の専用項目がないためunknown=0。','9425':'あいプロ買収の非拘束基本合意。確定買収と区別しMOU=2点。','5242':'ファクタリング新サービス、影響軽微。','7063':'蓄電池設備完工と7/4運用開始予定。場中公表のため初回入力7/3。'}
for c,t in times.items():
 txt=texts(ROOT/f'evidence/j3pdf{c}.json');url=re.search(r'https://[^\s)]+\.pdf',txt).group(0)
 if c=='4187':url='https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260702/20260701585659.pdf'
 r[c]={'url':url,'at':'2026-07-02T'+t+':59+09:00','first':'2026-07-03','verified_by':'7/2原開示本文と開示一覧・当時記事を照合。'+notes[c]}
for c in ['2493','3549','4187','6136']:events[c]=['earnings_up']
for c in ['4596','4890']:events[c]=['contract']
events.update({'504A':['unknown'],'9425':['jv_mou'],'5242':['product'],'7063':['product'],'2438':['contract'],'7602':['contract']})
r['2438']={'url':'https://asukanet.co.jp/contents/news/2026/20260702.html','at':'2026-07-02T23:59:59+09:00','first':'2026-07-03','verified_by':'日付付き公式導入事例と7/2 10:54当時報道を照合。日付精度のみのため7/2末を採用。導入採用=contract。'}
r['7602']={'url':'https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260701/20260701586395.pdf','at':'2026-07-01T17:20:59+09:00','first':'2026-07-02','verified_by':'業務委託契約の原開示7/1と17:20一覧照合。7/2入力時には材料未収集のため不採用だった。今回補完、過去予測は変更しない。'}
price_url['2026-07-02']='https://kabu.kininew.net/fiveup/7915.html'
save(ROOT/'data/july_releases_03.json',r);save(ROOT/'data/july_events_03.json',events)
build('2026-07-03','2026-07-02','july2actual_combined.json',['july2actual_anddigest3.json','july2post1.json'],r,events,{'3133':{'negative_material':True},'2935':{'dilution':True},'2751':{'negative_material':True},'9256':{'margin_restriction':True}})
