import json,re
from prepare_july import *
r=json.loads((ROOT/'data/july_releases_01.json').read_text())
times={'9425':'16:00','2751':'16:30','464A':'16:00','4918':'16:00','7781':'17:20','6573':'15:30','5942':'14:00','6239':'17:00','4496':'15:30','7371':'15:30','4167':'15:30','6363':'15:30'}
notes={'9425':'非拘束の株式取得基本合意。確定買収として扱わずMOU2点。完了予定は将来。','2751':'経常増額と純利益減額が混在。上方修正5点と下方修正-4点を併用。','464A':'経常600→1100百万円。補助金計上前倒し等、営業赤字は残る。','4918':'経常200→330百万円。原材料確保・記念新製品発売見通し。','7781':'経常1349→1778百万円。受注・効率改善等。','6573':'広告運用受託。業績影響軽微の記載を保存。','5942':'場中14時上方修正。7/1朝には不可、初回入力7/2。','6239':'子会社の受注約5.7億円、納期2027年4月。','4496':'決済業務提携契約・サービス開始。業績影響軽微。','7371':'三十三銀行との人材紹介の業務提携契約。','4167':'千葉信金へのシステム採用・利用開始。','6363':'買収完了に伴う予想増額。負ののれん含む特別利益32億円。'}
for c,t in times.items():
 txt=texts(ROOT/f'evidence/j2pdf{c}.json');url=re.search(r'https://[^\s)]+\.pdf',txt).group(0)
 r[c]={'url':url,'at':'2026-07-01T'+t+':59+09:00','first':'2026-07-02','verified_by':'7/1原開示PDF本文・日付とTDnet転載一覧時刻を照合。'+notes[c]}
events={c:['earnings_up'] for c in ['192A','4424','5967','7487','3494','9253','2685','2935','2975','546A','2751','464A','4918','7781','5942','6363']}
events.update({'2926':['dividend_revival'],'6522':['product'],'9425':['jv_mou'],'6573':['contract'],'6239':['contract'],'4496':['contract','product'],'7371':['contract'],'4167':['contract']})
price_url['2026-07-01']='https://kabu.kininew.net/fiveup/7907.html'
save(ROOT/'data/july_releases_02.json',r);save(ROOT/'data/july_events_02.json',events)
build('2026-07-02','2026-07-01','july1_actualmain.json',['july2_digest_find.json','july2morning.json'],r,events,{'3133':{'negative_material':True},'2935':{'dilution':True},'2751':{'negative_material':True},'9256':{'margin_restriction':True}})
