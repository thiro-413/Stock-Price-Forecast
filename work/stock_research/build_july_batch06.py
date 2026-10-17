"""July 23, 24, 27 reconstruction; never alter the frozen scorer or prior seals."""
import json,sys
from prepare_july import ROOT,save,build,price_url
from build_july_batch02 import pdfurl,release
from build_july_batch04 import PENALTIES

def run23():
 r=json.loads((ROOT/'data/july_releases_22.json').read_text());e=json.loads((ROOT/'data/july_events_22.json').read_text())
 types={'1518':'earnings_up','3091':'earnings_up','4684':'earnings_up','4733':'earnings_up','5576':'earnings_up','6890':'earnings_up','4890':'contract','323A':'contract','9090':'capital_alliance','4053':'acquisition','6227':'contract','6862':'product','9250':'product','9166':'monthly_sales','2459':'product','6428':'product'}
 notes={'1518':'経常10000→10400百万円、年間配当74→130円。買収効果・株式譲渡益含む。最大材料点のみ。','3091':'通期経常3050→4020百万円。7/1分割は比較期間より前。','4684':'1Q経常17.7%増、通期据置。','4733':'1Q経常20.8%増、通期据置。','5576':'1Q経常120.8%増、通期据置。Yahoo取得失敗を株探転載原短信で補完。','6890':'18:30開示の同日19:35訂正を採用。経常36000→55000百万円（52.8%増額）。当時記事の61%増額は訂正前、原資料を優先。訂正を新たな予想下方修正として重複減点しない。','4890':'CSR提出に伴う契約マイルストーン対価受領確定。7/3の同社分類と同じcontract。試験全症例の主要評価項目未達は2/6公表済みで、新たな承認・試験成功とは認定しない。','323A':'相互送客とシステム利用料を伴う業務提携開始、影響軽微。','9090':'JPYC優先株約10億円の引受と資本業務提携を決定。文書は覚書だが払込額・株数・7/30期日を特定した資本参加決議のためcapital_alliance。','4053':'既存会社への追加出資で40→88%子会社化を決議。','6227':'はんだボールマウンタ約25億円の受注、2028/6期売上予定。','6862':'SerialTuneの7/29提供開始を7/22公表。共同新サービスの発売予定、未確定の受注とは区別。時刻出典に相違があるため日末を採用。','9250':'DZ Securityの取扱い開始、product。新規顧客受注額は未確認。','9166':'7月発行の進捗レポートは実際には6月度売上高34.2%増。記事の7月売上表現を原資料に従って修正。','2459':'ChatGPT広告7カ国の運用支援開始。OpenAIとの資本提携・公式認定を意味しない。','6428':'ホテル事業開始を正式決議、8/1開始予定。ホテル資産取得は既存企業株式取得ではなく新サービス展開product。'}
 for c,typ in types.items():
  at={'1518':'16:00','5576':'16:00','6890':'19:35','9090':'16:00','6227':'15:35','6428':'16:00','6862':'23:59'}.get(c,'15:30')
  r[c]=release(pdfurl('jb6_pdf23_'+c+'.json'),'2026-07-22T'+at+':59+09:00','2026-07-23','7/22原開示の社名・日付・本文を当時記事と照合、公表時刻は開示一覧等で確認。'+notes[c]);e[c]=[typ]
 save(ROOT/'data/july_releases_23.json',r);save(ROOT/'data/july_events_23.json',e)
 price_url['2026-07-22']='https://kabu.kininew.net/fiveup/8044.html'
 build('2026-07-23','2026-07-22','jb5_actual22.json',['jb6_morning23.json','jb6_evening23.json','jb6_ichioshi23.json'],r,e,{**PENALTIES,'9439':{'dilution':True},'9553':{'dilution':True}})

def run24():
 r=json.loads((ROOT/'data/july_releases_23.json').read_text());e=json.loads((ROOT/'data/july_events_23.json').read_text())
 types={'6999':'earnings_up','9478':'earnings_up','3242':'earnings_up','7962':'earnings_up','7970':'earnings_up','6146':'earnings_up','2334':'jv_mou','3624':'contract','1436':'contract','2418':'contract','504A':'contract','4373':'contract','4832':'contract','4845':'acquisition','5592':'acquisition','5618':'acquisition','6027':'contract','6074':'jv_mou','6159':'buyback','7172':'acquisition','3856':'buyback','3687':'jv_mou'}
 notes={'6999':'中間・通期予想上方修正、通期経常4900→8800百万円、年間配当50→74円。','9478':'1Q経常64.1%増。自社株取得との複数材料は最大点のみ。','3242':'前期経常予想5400→5900百万円。','7962':'経常予想32.5%増額。','7970':'非開示だった通期経常14.2%増益予想を開示。','6146':'非開示だった中間経常32%増益予想と1Q経常42.5%増益。原資料は短信と別の業績差異資料で確認。新株・新株予約権も同時開示、希薄化-1。','2334':'戦略的協業は原文でMOUと明記。拘束力ある新規受注とせずjv_mou2点。','3624':'TCBグループとの業務提携契約を当日締結。','1436':'京都の蓄電所工事を追加受注、業績影響軽微。','2418':'雅叙園東京の婚礼事業を受託、予約開始は秋。7/27営業開始と公表7/23を区別。','504A':'EVERSANAとの米国市場展開契約。医薬品販売承認ではない。','4373':'JALへのシステム導入。','4832':'松浪硝子へのシステム導入、金額未確認。','4845':'テラ80%取得を決議。一次発信PR TIMES7/23 17:30を保守的公表時刻として使用。','5592':'blankpad全株取得決議。','5618':'NEW PHASE80%取得、4300万円。','6027':'3社間連携提供開始とJAいちかわへの6/1導入を7/23公表。従来の採用事例分類に従いcontract、6/1公表と誤認しない。','6074':'原開示は事業譲受の基本合意のみで実行未確定と明記。記事の取得表現を確定買収とせずMOU2点。','6159':'7/24朝のToSTNeT-3取得予定、結果は不使用。','7172':'キーサイド全株取得、実行7/29予定。','3856':'既存買戻し枠100→400万株・5→20億円へ拡大。','3687':'ドローン開発・PoCで連携開始。確定受注・販売開始とは認定せず提携の合意としてjv_mou2点。'}
 files={'9478':'retry9478','6146':'retry6146','1436':'retry1436','2418':'official2418','5618':'retry5618','6074':'official6074','3687':'retry3687'}
 for c,typ in types.items():
  url='https://prtimes.jp/main/html/rd/p/000000193.000012894.html' if c=='4845' else pdfurl('jb6_pdf24_'+files.get(c,c)+'.json')
  at={'7962':'16:00','6146':'16:00','2334':'16:00','1436':'15:35','2418':'17:30','504A':'16:30','4845':'17:30','5618':'16:30','6074':'16:00','6159':'16:20','3856':'16:00','3687':'16:00'}.get(c,'15:30')
  r[c]=release(url,'2026-07-23T'+at+':59+09:00','2026-07-24','日付付き原発信の本文と当時記事・公表時刻を照合。'+notes[c]);e[c]=[typ]
 save(ROOT/'data/july_releases_24.json',r);save(ROOT/'data/july_events_24.json',e)
 price_url['2026-07-23']='https://kabu.kininew.net/fiveup/8052.html'
 penalties={**PENALTIES,'9439':{'dilution':True},'9553':{'dilution':True},'6146':{'dilution':True},'278A':{'margin_restriction':True}}
 penalties.pop('6522') # 7/23 16:50公開、7/24売買から解除。過去予測は変更しない。
 build('2026-07-24','2026-07-23','jb6_actual23_try.json',['jb6_morning24.json','jb6_evening24.json'],r,e,penalties)
 from prepare_july import evidence
 path=ROOT/'data/july_inputs/2026-07-24.json';x=json.loads(path.read_text())
 x['evidence'].append(evidence('margin_20260723','https://s.kabutan.jp/news/n202607231302/','2026-07-23T16:50:59+09:00',True,'当時の規制・解除記事。278A規制、6522と4935解除。日々公表と増担保を区別。'))
 save(path,x)

def run27():
 r=json.loads((ROOT/'data/july_releases_24.json').read_text());e=json.loads((ROOT/'data/july_events_24.json').read_text())
 # Correct annotations prospectively, leaving July 24 sealed artifacts untouched.
 r['6999']['verified_by']='7/23原資料・時刻・当時記事を照合。通期経常3300→6040百万円、年間配当39→63円。7/24入力説明文の転記誤りは別紙正誤表を参照。'
 r['3242']['verified_by']='7/23原資料・時刻・当時記事を照合。前期経常2850→3100百万円。7/24入力説明文の転記誤りは別紙正誤表を参照。'
 types={'3386':'earnings_up','2693':'earnings_up','2804':'earnings_up','4063':'earnings_up','4519':'earnings_up','6629':'earnings_up','6653':'earnings_up','6858':'earnings_up','8060':'earnings_up','9029':'earnings_up','9107':'earnings_up','2656':'jv_mou','4833':'product','4169':'acquisition','4829':'jv_mou','6420':'jv_mou','2911':'asset_gain','8541':'jv_mou','4776':'monthly_sales'}
 notes={'3386':'中間・通期経常予想を上方修正。','2693':'中間と通期の経常上方修正だが通期純利益170→50百万円は下方修正。earnings_upとnegative_material-4を併用。','2804':'1Q経常増益、最終は減益。新たな予想下方修正とは区別。','4063':'非開示だった通期増益予想と増配を発表。','4519':'IFRS中間利益19.2%増、通期据置。','6629':'原短信1Q利益を確認。記事は黒字転換、PDF抽出では前年の負符号が欠落し得る。改善方向は共通。','6653':'通期経常予想5.9%増額、増配。','6858':'中間経常は前年-38→573百万円、通期据置。','8060':'中間経常増益、通期経常640億円へ修正。','9029':'1Q経常28.5%増、通期据置。','9107':'通期経常1000→1350億円、35%上方修正。','2656':'Blue Goatsとの基本合意。8月の本契約予定を確定受注とは扱わない。','4833':'AIエージェント支援の新サービス提供開始。','4169':'ダーウィン全株取得の補足原資料。顧客受注とは区別。','4829':'蓄電池事業の合弁会社を新設決議、jv_mou。','6420':'インドに新設JVを決議。既存会社の買収とは区別。','2911':'有価証券売却益の計上見込み、asset_gain。','8541':'経営統合に向けた基本合意、最終契約未締結。確定買収と区別。','4776':'6月連結売上高前年比14.1%増、速報値。'}
 files={'2693':'retry2693','4519':'retry4519','6629':'retry6629','6858':'final6858','8060':'alt8060','9029':'alt9029','4776':'alt4776'}
 for c,typ in types.items():
  at={'2804':'16:30','4519':'16:00','6629':'16:00','6653':'17:00','2656':'16:40','4833':'16:00','4829':'17:00','6420':'16:00'}.get(c,'15:30')
  r[c]=release(pdfurl('jb6_pdf27_'+files.get(c,c)+'.json'),'2026-07-24T'+at+':59+09:00','2026-07-27','7/24原発信の社名・日付・本文を当時記事と照合、公表時刻を転載一覧等で確認。'+notes[c]);e[c]=[typ]
 # Formal July 24 results match the July 17 preliminary ordinary profits exactly.
 # Do not rejuvenate an already-public numerical event merely because a formal report followed.
 save(ROOT/'data/july_releases_27.json',r);save(ROOT/'data/july_events_27.json',e)
 price_url['2026-07-24']='https://kabu.kininew.net/fiveup/8060.html'
 penalties={**PENALTIES,'9439':{'dilution':True},'9553':{'dilution':True},'6146':{'dilution':True},'278A':{'margin_restriction':True},'2693':{'negative_material':True}}
 penalties.pop('6522')
 build('2026-07-27','2026-07-24','jb6_actual24_find27.json',['jb6_morning27.json','jb6_evening27.json'],r,e,penalties)

if __name__=='__main__':globals()['run'+sys.argv[1]]()
