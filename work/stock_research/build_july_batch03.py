import json,re,sys
from prepare_july import ROOT,save,texts,build,price_url
from build_july_batch02 import pdfurl,release
def run09():
 r=json.loads((ROOT/'data/july_releases_08.json').read_text());e=json.loads((ROOT/'data/july_events_08.json').read_text())
 types={'3490':'earnings_up','9720':'earnings_up','197A':'contract','2670':'earnings_up','3391':'earnings_up','6183':'earnings_up','9861':'earnings_up','2997':'acquisition','4381':'product','4833':'product','9348':'contract'}
 notes={'3490':'第1四半期経常272.9%増。7/8 16:00新株予約権発行の公表も同日転載一覧で確認し希薄化-1。後日行使状況PDFは入力に使用しない。','9720':'通期経常156.9%増額、固定資産権利変換益あり。','197A':'Craifとの契約締結、開発中製品の独占販売権、影響軽微。','2670':'1Q経常10.3%増、通期据置。','3391':'1Q経常87%増。ウエルシア連結等により前年比較の構成差あり。','6183':'1Q最終22.2%増、通期据置。','9861':'1Q経常125%増、通期据置。','2997':'TOB対象企業。買収関連acquisition3点、TOBプレミアム専用加点なし。','4381':'コンソーシアム発足と同日マーケットプレイス公開。契約受注とは認定せずproduct3点。','4833':'コンソーシアム参画と同日マーケットプレイスでサービス紹介開始。product3点。','9348':'SpaceXとの搭載枠購入契約。81億円は同社の受注売上ではなく支払契約総額。contract4点、規模加点なし。'}
 for c,typ in types.items():
  at={'3490':'16:00','9861':'16:00','2997':'18:30','4833':'16:00','9348':'15:50'}.get(c,'15:30')
  r[c]=release(pdfurl('jb3_pdf09_'+c+'.json'),'2026-07-08T'+at+':59+09:00','2026-07-09','日付付き原開示本文とTDnet転載一覧時刻・当時記事を照合。'+notes[c]);e[c]=[typ]
 r['2488']=release('https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260708/20260708589942.pdf','2026-07-08T17:00:59+09:00','2026-07-09','7/8原開示、転載時刻と記事を照合。コンソーシアムとマーケットプレイス公開、product分類。');e['2488']=['product']
 save(ROOT/'data/july_releases_09.json',r);save(ROOT/'data/july_events_09.json',e)
 price_url['2026-07-08']='https://kabu.kininew.net/fiveup/7953.html'
 build('2026-07-09','2026-07-08','jb2_actual08.json',['jb3_morning09.json','jb3_evening09_find.json'],r,e,{'3133':{'negative_material':True},'4575':{'negative_material':True},'2751':{'negative_material':True},'3490':{'dilution':True},'6522':{'margin_restriction':True}})
def run10():
 r=json.loads((ROOT/'data/july_releases_09.json').read_text());e=json.loads((ROOT/'data/july_events_09.json').read_text())
 notes={'2341':'1Q経常153.5%増。株式消却を新規買付とは扱わない。','2698':'1Q経常8.3%増、通期据置。','2735':'3Q累計経常39.3%増、通期据置。優待は採点項目なし。','5018':'1Q経常153.2%増、通期据置。','7544':'1Q経常15.4%増、通期据置。','8918':'1Q経常黒字転換、通期据置。','9414':'3Q単独経常25%増という当時記事と短信照合。累計は12.8%減。固定ルールは単独四半期増益もearnings_up。','9560':'旧個別経常1424百万円→新連結1440百万円。連結開始による比較範囲変更を伴う数字であり既存事業の上方修正とは認定しないが固定ルールの増益予想分類。','9903':'1Q経常32%増、通期据置。','6323':'1Q経常51.1%増、通期据置。','6227':'大口受注約180億円、売上計上2027/28年6月期。','4763':'通期経常3.9%増額、配当1円増額。'}
 for c,note in notes.items():
  r[c]=release(pdfurl('jb3_pdf10_'+c+'.json'),'2026-07-09T'+('16:00' if c in ['5018','7544'] else '15:30')+':59+09:00','2026-07-10','7/9原開示本文と日付、TDnet転載一覧・当時記事の公表時刻を照合。'+note);e[c]=['contract' if c=='6227' else 'earnings_up']
 save(ROOT/'data/july_releases_10.json',r);save(ROOT/'data/july_events_10.json',e)
 price_url['2026-07-09']='https://kabu.kininew.net/fiveup/7961.html'
 build('2026-07-10','2026-07-09','jb3_actual09.json',['jb3_morning10.json','jb3_evening10.json'],r,e,{'3133':{'negative_material':True},'4575':{'negative_material':True},'2751':{'negative_material':True},'3490':{'dilution':True},'6522':{'margin_restriction':True}})
def run13():
 r=json.loads((ROOT/'data/july_releases_10.json').read_text());e=json.loads((ROOT/'data/july_events_10.json').read_text())
 notes={'2669':'1Q経常142.8%増、通期据置。','2683':'1Q経常225.6%増、営業利益は減少、通期据置。','2999':'通期経常350→800百万円。','3454':'上期経常573.3%増、通期据置。','3996':'通期経常51→72百万円、記念配当5円復配。','4176':'3Q累計経常60.1%増、最終5.4%減、通期据置。','4829':'次年度経常106→160百万円、原資料49.9%増。記事51%と微差あるが分類に影響なし。','6668':'通期経常1350→2700百万円、為替差益も寄与。','7219':'通期経常380→600百万円。','7463':'1Q経常黒字転換、評価損益等を含む。','8244':'通期経常5200→5500百万円、中間1700→2700。','9270':'3Q累計経常319.1%増、通期据置。','4992':'上期経常17.6%増、通期据置。','5967':'翌期経常増益予想。','8908':'翌期経常2%増益予想。','8927':'通期経常30%増額。','4381':'クウジットとの事業提携契約の締結およびサービス提供開始を原資料で明記。contract4点。'}
 for c,note in notes.items():
  at={'3454':'17:00','9270':'16:00','4829':'16:00'}.get(c,'15:30')
  r[c]=release(pdfurl('jb3_pdf13_'+c+'.json'),'2026-07-10T'+at+':59+09:00','2026-07-13','7/10原開示本文と日付、公表時刻・週末記事を照合。'+note);e[c]=['contract'] if c=='4381' else ['earnings_up']
 save(ROOT/'data/july_releases_13.json',r);save(ROOT/'data/july_events_13.json',e)
 price_url['2026-07-10']='https://kabu.kininew.net/fiveup/7970.html'
 build('2026-07-13','2026-07-10','jb3_actual10.json',['jb3_morning13.json','jb3_evening13.json'],r,e,{'3133':{'negative_material':True},'4575':{'negative_material':True},'2751':{'negative_material':True},'3490':{'dilution':True},'6522':{'margin_restriction':True}})
if __name__=='__main__':
 if len(sys.argv)==1:run09()
 elif sys.argv[1]=='13':run13()
 else:run10()
