"""July 28–30 inputs; fixed model and prior seals are immutable."""
import json,sys
from prepare_july import ROOT,save,build,price_url
from build_july_batch02 import pdfurl,release
from build_july_batch04 import PENALTIES

def penalties():
 p={**PENALTIES,'9439':{'dilution':True},'9553':{'dilution':True},'6146':{'dilution':True},'278A':{'margin_restriction':True},'2693':{'negative_material':True},'2311':{'negative_material':True}}
 p.pop('6522');return p

def run28():
 r=json.loads((ROOT/'data/july_releases_27.json').read_text());e=json.loads((ROOT/'data/july_events_27.json').read_text())
 types={'2767':'earnings_up','2311':'earnings_up','7299':'earnings_up','3635':'earnings_up','4644':'earnings_up','4765':'earnings_up','4956':'earnings_up','5911':'earnings_up','7177':'earnings_up','7751':'earnings_up','7949':'earnings_up','9081':'earnings_up','2984':'acquisition','340A':'product','3733':'buyback','3823':'product','3842':'contract','4379':'jv_mou','438A':'product','4579':'unknown','4888':'contract','6199':'buyback','9424':'contract','4978':'contract','278A':'contract','4373':'earnings_up','3151':'asset_gain'}
 notes={'2767':'通期経常予想を上方修正。','2311':'中間・通期経常上方修正と中間純利益下方修正が混在。純利益187→173百万円、-4を併用。','7299':'中間経常1250→1400百万円。1Q経常増益、通期据置。','3635':'1Q経常増益。','4644':'1Q営業黒字浮上、経常も増益。','4765':'1Q経常増益。将来の合併基本合意は最大材料点を上乗せしない。','4956':'1Q経常増益。買戻しとの複数材料は最大点のみ。','5911':'1Q経常微増、最終減益だが予想下方修正ではない。','7177':'中間決算速報で経常増益予想を新たに開示。8/5正式発表を使用しない。','7751':'中間税引前増益・通期利益予想修正。','7949':'1Q経常増益。','9081':'中間経常予想上方修正。','2984':'ホームズ・安住コーポレーション株式取得決議。','340A':'WorldShopping BIZ Growth提供開始。','3733':'翌朝ToSTNeT-3自己株式取得を決議。翌朝結果は使用しない。','3823':'WHY HOW Cardの8月提供開始予定を公表。','3842':'原文でEnour CallAssistantの販売代理店契約締結、contract。','4379':'年内の共同機能開発と提供を目指す段階、MOU相当2点。','438A':'Xard与信・保証オプション提供開始。','4579':'既存製品の韓国適応症追加。新規契約・製品発売を確認しておらずunknown、既存契約ロイヤルティを新契約としない。','4888':'岡山大学との再委託研究開発契約を締結。','6199':'7/27決議の自己株式取得方法。翌朝結果不使用。','9424':'ドコモとの相互接続協定締結。サービス開始予定日と公表日を区別。','4978':'WEIPUとの戦略的協業契約締結。細胞製品・製造サービスを相互に提供、基本合意との記載なし。','278A':'ベルギー国防省UTM導入を受注、実施は今後。規制-1も併用。','4373':'1Q IFRS税引前・最終増益。新サービスの点数は重複加算しない。','3151':'保有有価証券売却益見込み、通期予想は据置。'}
 files={c:'extra'+c for c in ['7299','4765','7751','278A','4373','3151']};files.update({c:'retry'+c for c in ['4978','4956','7949']})
 times={'7299':'16:00','3635':'16:00','4644':'15:31','7177':'15:31','2984':'18:00','3733':'16:25','3823':'16:00','3842':'16:00','6199':'16:30','9424':'15:31','278A':'18:02','3151':'16:00'}
 for c,typ in types.items():
  r[c]=release(pdfurl('jb7_pdf28_'+files.get(c,c)+'.json'),'2026-07-27T'+times.get(c,'15:30')+':59+09:00','2026-07-28','原開示の会社・日付・本文、当時記事、公表時刻を照合。'+notes[c]);e[c]=[typ]
 save(ROOT/'data/july_releases_28.json',r);save(ROOT/'data/july_events_28.json',e)
 price_url['2026-07-27']='https://kabu.kininew.net/fiveup/8070.html'
 build('2026-07-28','2026-07-27','jb6_actual27_combined.json',['jb7_morning28.json','jb7_tail28_search.json','jb7_evening28_retry.json'],r,e,penalties())

def run29():
 r=json.loads((ROOT/'data/july_releases_28.json').read_text());e=json.loads((ROOT/'data/july_events_28.json').read_text())
 types={c:'earnings_up' for c in ['4290','6337','6861','4894','5471','7102','7309','8218','9697','4479','6988','7191','7735','8367','9267','9782','5532']}
 types.update({'1418':'asset_gain','4015':'monthly_sales','4493':'product','4769':'asset_gain','4819':'contract','6193':'product','6918':'asset_gain','9227':'unknown','3771':'dividend_raise','190A':'unknown'})
 files={c:'retry'+c for c in ['4290','4479','9267','1418','4493']};files.update({c:'extra'+c for c in ['4015','4769','4819','6193','6918','9227','3771','190A']})
 times={'4290':'16:00','6861':'16:00','4894':'16:45','5471':'16:00','7102':'15:40','9697':'15:40','6988':'16:00','7735':'15:35','8367':'17:00','1418':'16:00','4015':'17:00','4769':'17:10','3771':'15:45'}
 notes={'4894':'通期損失予想縮小、earnings_up。','5532':'3Q累計経常増益、4-6月赤字だが通期予想据置。予想下方修正と区別。','3771':'年間配当70→80円。1Q減益だが通期予想据置。','4015':'原資料の指標は6月MRR成長率。記事のMMRは表記相違。monthly_salesを月次経常収益に適用。103%を売上高2倍との断定には使用しない。','9227':'装置を製作し実証試験で活用する開発段階、販売開始・確定受注の記載なし。unknown。','190A':'希少疾病用医薬品指定の部会了承、正式指定・製造販売承認ではない。新契約や発売は確認できずunknown。','7102':'原PDFは画像のみ。1ページ目を画像で確認、1Q経常1594→2851百万円（78.8%増）。','4819':'京都銀行向け請求書カード払い機能の提供・組込み開始、導入事例contract。','4493':'AIアプリケーション診断サービス提供開始、product。'}
 for c,typ in types.items():
  r[c]=release(pdfurl('jb7_pdf29_'+files.get(c,c)+'.json'),'2026-07-28T'+times.get(c,'15:30')+':59+09:00','2026-07-29','7/28原資料の会社・日付・本文、公表時刻、当時記事を照合。'+notes.get(c,'当時記事の利益改善・材料方向を原資料で確認。複数材料は最大点のみ。'));e[c]=[typ]
 save(ROOT/'data/july_releases_29.json',r);save(ROOT/'data/july_events_29.json',e)
 save(ROOT/'data/july_batch07_additional_events.json',{'4888':{'url':pdfurl('jb7_pdf29_extra4888.json'),'at':'2026-07-28T15:30:59+09:00','first':'2026-07-29','verified_by':'QST病院との原開示は共同研究契約締結の検討を目的とした基本合意。jv_mou2点。7/27公表の岡山大学研究契約4点は独立して鮮度を計算。'}})
 price_url['2026-07-28']='https://kabu.kininew.net/fiveup/8078.html'
 build('2026-07-29','2026-07-28','jb7_actual28.json',['jb7_morning29.json','jb7_evening29.json'],r,e,penalties())
 extra_events('2026-07-29')

def extra_events(day):
 from prepare_july import evidence
 p=ROOT/f'data/july_inputs/{day}.json';x=json.loads(p.read_text())
 for code,rel in json.loads((ROOT/'data/july_batch07_additional_events.json').read_text()).items():
  row=next((r for r in x['candidates'] if r['code']==code),None)
  if row:
   eid='additional_'+code+'_'+rel['first'];x['evidence'].append(evidence(eid,rel['url'],rel['at'],True,rel['verified_by']));row['evidence_ids'].append(eid);row['events'].append({'evidence_id':eid,'type':'jv_mou','first_eligible_session':rel['first']})
 save(p,x)

def run30():
 r=json.loads((ROOT/'data/july_releases_29.json').read_text());e=json.loads((ROOT/'data/july_events_29.json').read_text())
 codes=['1944','1946','2175','2359','2664','2760','3793','3850','3969','4362','4461','4812','5609','6042','6349','6370','6501','6524','6586','6663','6701','6822','6857','6955','6961','7551','7995','8137','8572','8604','9307','9698','3636']
 types={c:'earnings_up' for c in codes};types.update({'4262':'acquisition','9166':'capital_alliance','4722':'acquisition','4880':'unknown'})
 files={c:'extra'+c for c in ['4362','6370','7551','4262','9166','4722','4880']};files.update({'6501':'alt6501','6042':'alt6042'})
 times={'4362':'16:30','4461':'16:00','6524':'16:30','6955':'16:00','7551':'16:30','3636':'16:00','4262':'17:30','4722':'17:30'}
 notes={'6663':'中間利益上方修正だが売上予想2150→1782百万円を下方修正。固定ルールのforecast reductionとしてnegative_material-4を併用。','6822':'中間最終赤字→黒字、通期純利益も550百万円増額。営業・経常据置を経常上方修正と誤認しない。','3636':'3Q累計経常増益。セグメント別予想の増減は相殺、連結通期据置。個別セグメント減額で連結予想下方修正とはしない。','6042':'文字化け原PDFをJPX転載第1ページ画像で照合。中間経常400→600百万円、通期650→750百万円。','6501':'Yahoo PDF403をJPX原資料転載で補完。1Q最終減益だが通期最終上方修正。','9698':'原短信1Q経常61.5%増。記事の63%表現は原資料を優先し、同じearnings_up。','9166':'SBIと資本業務提携契約を締結する決議。新株発行ではなく市場買付で株式取得を予定、希薄化認定なし。','4722':'TOB/MBO対象。過去2997と同じacquisition3点、プレミアム専用加点はなし。','4262':'レプリス全株取得決議。','4880':'連結子会社吸収で非連結へ移行。原資料で経常損失予想164→210百万円へ拡大を確認、negative_material-4。特別利益65百万円はasset_gainの有価証券売却益とは区別。'}
 for c,typ in types.items():
  r[c]=release(pdfurl('jb7_pdf30_'+files.get(c,c)+'.json'),'2026-07-29T'+times.get(c,'15:30')+':59+09:00','2026-07-30','7/29日付付き原資料の会社・本文、当時記事、公表時刻を照合。'+notes.get(c,'利益改善または予想上方修正を原資料で確認。複数材料は最大点のみ。'));e[c]=[typ]
 save(ROOT/'data/july_releases_30.json',r);save(ROOT/'data/july_events_30.json',e)
 price_url['2026-07-29']='https://kabu.kininew.net/fiveup/8087.html'
 build('2026-07-30','2026-07-29','jb7_actual29_final.json',['jb7_morning30.json','jb7_evening30.json'],r,e,{**penalties(),'6663':{'negative_material':True},'4880':{'negative_material':True}})
 extra_events('2026-07-30')

if __name__=='__main__':globals()['run'+sys.argv[1]]()
