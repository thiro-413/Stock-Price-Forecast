"""Batch2 inputs. Model and sealed earlier days are never modified."""
import json,re,sys
from prepare_july import ROOT,save,texts,build,price_url
def pdfurl(file):
 t=texts(ROOT/'evidence'/file);return re.search(r'https://[^\s)]+\.pdf',t).group(0)
def release(url,at,first,note):
 return dict(url=url,at=at,first=first,verified_by=note)
def initial():
 r=json.loads((ROOT/'data/july_releases_03.json').read_text());e=json.loads((ROOT/'data/july_events_03.json').read_text())
 urls={c:pdfurl('b206pdf'+c+'.json') for c in ['7975','3377','6264','9948','3612']}
 urls.update({'4394':'https://www2.jpx.co.jp/disc/43940/140120260625581014.pdf','265A':'https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260703/20260702586756.pdf','2678':'https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260703/20260703587650.pdf','340A':'https://prtimes.jp/main/html/rd/p/000000342.000018480.html'})
 for c,url in urls.items():
  r[c]=release(url,'2026-07-03T'+('10:00' if c=='340A' else '15:30')+':59+09:00','2026-07-06','7/3原開示本文と日付・当時記事内容・TDnet転載時刻を照合。'+{'3377':'経常は中間0.3%増、3-5月31%増、通期修正なし。','4394':'中間経常29.5%増、優待は固定ルールに点数項目なし。','6264':'3Q累計経常85.7%増、通期修正なし。','7975':'1Q経常289.5%増。','2678':'翌期最終黒字予想と増配。','3612':'1Q最終24.7%増。','9948':'1Q経常5.6%増。','265A':'販売体制強化と共同提案。','340A':'台湾子会社の商業連携。'}[c])
  e[c]=['contract'] if c in ['265A','340A'] else ['earnings_up']
 save(ROOT/'data/july_releases_06.json',r);save(ROOT/'data/july_events_06.json',e)
 price_url['2026-07-03']='https://kabu.kininew.net/fiveup/7923.html'
 build('2026-07-06','2026-07-03','july3actual_first.json',['jb2_digest06.json'],r,e,{'3133':{'negative_material':True},'4575':{'negative_material':True},'2751':{'negative_material':True}})
def july07():
 r=json.loads((ROOT/'data/july_releases_06.json').read_text());e=json.loads((ROOT/'data/july_events_06.json').read_text())
 types={'6093':'earnings_up','9972':'earnings_up','3186':'earnings_up','4591':'contract','241A':'contract','4284':'contract','2501':'capital_alliance','5131':'product','265A':'contract'}
 for c,typ in types.items():
  t={'9972':'16:30','5131':'16:00'}.get(c,'15:30')
  r[c]=release(pdfurl('b207pdf'+c+'.json'),'2026-07-06T'+t+':59+09:00','2026-07-07','7/6の原開示本文と日付、当時記事・Yahoo転載一覧の公表時刻を照合。'+{'6093':'第1四半期経常175.2%増、通期修正なし。','9972':'中間経常黒字化、通期修正なし。','3186':'通期経常13%増額。','4591':'CDMO業務提携契約。','241A':'AI面接官の採用、影響軽微。','4284':'PoC後の本契約への移行を明記。','2501':'資本業務提携、許認可等の条件あり。','5131':'API連携製品の金融機関での利用開始。','265A':'Voice Digestライセンス契約、相手先・金額非開示。'}[c]);e[c]=[typ]
 save(ROOT/'data/july_releases_07.json',r);save(ROOT/'data/july_events_07.json',e)
 price_url['2026-07-06']='https://kabu.kininew.net/fiveup/7937.html'
 build('2026-07-07','2026-07-06','jb2_actual06.json',['jb2_after06.json','b207evening.json','b207extra.json'],r,e,{'3133':{'negative_material':True},'4575':{'negative_material':True},'2751':{'negative_material':True}})
def july08():
 r=json.loads((ROOT/'data/july_releases_07.json').read_text());e=json.loads((ROOT/'data/july_events_07.json').read_text())
 for c in ['6469','9651','2408','3396','2734','9740','2726','3625','6522']:
  typ='product' if c in ['3625','6522'] else 'earnings_up'
  at=('2026-07-06T21:00:59+09:00' if c=='6522' else '2026-07-07T'+{'6469':'16:00','9651':'16:30','3625':'11:00'}.get(c,'15:30')+':59+09:00')
  r[c]=release(pdfurl('b208pdf'+c+'.json'),at,'2026-07-07' if c=='6522' else '2026-07-08','原開示本文の日付・内容、Yahoo転載一覧時刻、当時記事を照合。'+{'6469':'通期経常21.7%増額。','9651':'新年度経常10.5%増。','2408':'通期経常4.7%増額、投資有価証券売却益あり。','3396':'第1四半期経常黒字転換、営業赤字拡大、通期据置。','2734':'通期経常11.9%増額。','9740':'第1四半期経常6%増、純利益30.3%減、通期据置。','2726':'第1四半期経常1.1%増、通期据置。','3625':'点検DXのサービス展開。6月提供開始を7/7公表、受注額確認できずproduct分類。','6522':'米国RFID製品販売本格展開、拘束力ある新受注とは認定せずproduct分類。7/7予測時には取得漏れ、保存済み予測に遡及反映しない。'}[c]);e[c]=[typ]
 r['5243']=release('https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260707/20260707588967.pdf','2026-07-07T15:30:59+09:00','2026-07-08','原開示と日付、Yahoo一覧時刻、当時記事を照合。経常61.4%増額、売上0.8%増額、主に費用抑制。');e['5243']=['earnings_up']
 r['340A']=release('https://finance-frontend-pc-dist.west.edge.storage-yahoo.jp/disclosure/20260707/20260707588917.pdf','2026-07-07T15:30:59+09:00','2026-07-08','原開示本文と日付・Yahoo一覧時刻を照合。STORESとの越境EC業務提携、7/7提供開始。');e['340A']=['contract']
 save(ROOT/'data/july_releases_08.json',r);save(ROOT/'data/july_events_08.json',e)
 price_url['2026-07-07']='https://kabu.kininew.net/fiveup/7945.html'
 build('2026-07-08','2026-07-07','jb2_actual07_digest08.json',['jb2_actual07_digest08.json','b208evening.json'],r,e,{'3133':{'negative_material':True},'4575':{'negative_material':True},'2751':{'negative_material':True}})
if __name__=='__main__':
 if len(sys.argv)==1: initial()
 elif sys.argv[1]=='08': july08()
 else: july07()
