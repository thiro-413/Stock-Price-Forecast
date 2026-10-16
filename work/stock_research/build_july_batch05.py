"""July 17, 21, 22 inputs; fixed scoring and prior seals are immutable."""
import json,sys
from prepare_july import ROOT,save,build,price_url
from build_july_batch02 import pdfurl,release
from build_july_batch04 import PENALTIES

def run17():
 r=json.loads((ROOT/'data/july_releases_16.json').read_text());e=json.loads((ROOT/'data/july_events_16.json').read_text())
 types={'2158':'contract','2780':'acquisition','3798':'contract','4262':'jv_mou','438A':'contract','5132':'product','549A':'acquisition','7808':'earnings_up','8613':'earnings_up','9439':'unknown','9832':'acquisition','9941':'monthly_sales','6572':'earnings_up','7581':'earnings_up'}
 notes={'2158':'参天製薬でAI創薬支援サービスを利用する第2弾プロジェクトを開始。顧客採用としてcontract、金額不明。','2780':'ガレージバンク株式取得、取得額16.8億円。','3798':'サントリーへのAI開発基盤導入。業績予想変更なし。顧客採用としてcontract。','4262':'包括的パートナーシップの合意。具体的受注・商用提供開始の確証なし、jv_mou。別の先行トライアル記事を本合意の売上とは認定しない。','438A':'決済基盤に採用され7/16サービス開始。顧客採用contract。','5132':'AIオペレーター提供開始。product。','549A':'SPD&Company株式取得。既存企業の買収としてacquisition。','7808':'翌期経常増益予想。前期減益と区別。決算延期後7/16公表、短信に監査不表明の記載は確認されず。','8613':'1Q決算速報値。経常2067百万円、正式発表7/30の内容は使用しない。','9439':'新事業開始の正式決定に先駆けた子会社設立と明記。サービス開始・既存企業取得とは認定しないunknown。同日新株払込を一覧で確認し希薄化-1。','9832':'佐々木自動車全株取得済み。','9941':'6月売上速報前年比増加。','6572':'7/15短信の1Q経常134%増を今回補完。初回適格日は7/16のまま、7/16予測は補修せず7/17では継続半点。','7581':'7/15短信の3Q累計経常24.9%増を今回補完。初回適格日は7/16のまま、過去予測を変更しない。'}
 for c,typ in types.items():
  prior='2026-07-15' if c in ['6572','7581'] else '2026-07-16'
  at={'2158':'16:00','5132':'16:00','549A':'17:00','9439':'16:00','9941':'18:00','6572':'16:00'}.get(c,'15:30')
  first='2026-07-16' if c in ['6572','7581'] else '2026-07-17'
  r[c]=release(pdfurl('jb5_pdf17_'+c+'.json'),prior+'T'+at+':59+09:00',first,'日付付き原開示本文と転載時刻・当時記事を照合。'+notes[c]);e[c]=[typ]
 save(ROOT/'data/july_releases_17.json',r);save(ROOT/'data/july_events_17.json',e)
 price_url['2026-07-16']='https://kabu.kininew.net/fiveup/8015.html'
 build('2026-07-17','2026-07-16','jb4_actual16.json',['jb5_morning17.json','jb5_evening17.json'],r,e,{**PENALTIES,'9439':{'dilution':True}})

def run21():
 r=json.loads((ROOT/'data/july_releases_17.json').read_text());e=json.loads((ROOT/'data/july_events_17.json').read_text())
 types={'4929':'earnings_up','5074':'contract','3817':'buyback','4196':'product','5078':'buyback','5933':'earnings_up','6834':'jv_mou','7175':'earnings_up','8707':'earnings_up','2411':'buyback','9553':'buyback','6238':'monthly_sales','7685':'unknown','278A':'unknown'}
 notes={'4929':'1Q経常-12→51百万円の黒字転換。','5074':'子会社が系統用蓄電所EPCを約60億円受注。27/28年6月期売上予定。7/17原開示のみ採点。検索・転載一覧に将来8/14受注取消表題が偶発表示されたが入力には不採用。','3817':'96万株・43億円上限の自社株取得決議。7/21の実際の取得結果は締切後のため不使用。','4196':'戦略PR For AI提供開始、グループ内共同サービスでありproduct。','5078':'1万株・4870万円上限、7/21朝のToSTNeTで取得予定。結果は不使用。','5933':'1Q経常25.5%増。','6834':'連結子会社が中国企業との合弁会社設立を決議。新設JVとしてjv_mou2点、既存企業株式の取得ではない。','7175':'1Q経常速報776百万円、前年205百万円。正式発表の将来値不使用。','8707':'1Q経常速報4687百万円、前年比増益。正式発表の将来値不使用。','2411':'自社株買い70万株・3.5億円。1Q減益は予想の下方修正ではないため固定ルールの-4に該当しない。','9553':'自社株買いとCB発行を同日公表。原資料に潜在希薄化を明記、希薄化-1を適用。','6238':'6月売上速報前年比増。','7685':'出張訪問・店舗の仕入高増加。売上高とは区別しmonthly_salesの加点なし。','278A':'7/27の防衛戦略発表会の開催案内。新規受注・新製品提供開始は記載されずunknown。7/21 17時の別製品展開開示は不使用。'}
 for c,typ in types.items():
  at={'5074':'16:00','3817':'17:00','4196':'17:00','5078':'16:15','6834':'16:00','8707':'16:30','9553':'17:20','6238':'16:00'}.get(c,'15:30')
  r[c]=release(pdfurl('jb5_pdf21_'+c+'.json'),'2026-07-17T'+at+':59+09:00','2026-07-21','7/17原開示本文・日付と転載時刻、7/20・21記事を照合。'+notes[c]);e[c]=[typ]
 save(ROOT/'data/july_releases_21.json',r);save(ROOT/'data/july_events_21.json',e)
 price_url['2026-07-17']='https://kabu.kininew.net/fiveup/8023.html'
 build('2026-07-21','2026-07-17','jb5_actual17.json',['jb5_morning21.json','jb5_evening21.json'],r,e,{**PENALTIES,'9439':{'dilution':True},'9553':{'dilution':True}})

def run22():
 r=json.loads((ROOT/'data/july_releases_21.json').read_text());e=json.loads((ROOT/'data/july_events_21.json').read_text())
 types={'278A':'product','3803':'contract','4820':'earnings_up','6200':'earnings_up','6769':'earnings_up','7602':'contract','9274':'buyback','3840':'contract','4889':'contract','3951':'buyback','4073':'contract','4415':'contract','6045':'monthly_sales','6083':'acquisition','6193':'product','8708':'earnings_up','9820':'acquisition','3121':'jv_mou','4404':'asset_gain','6088':'asset_gain'}
 notes={'278A':'自律迎撃ドローン市場展開開始。受注額は未確認、product3点。7/17開催案内とは別の7/21新開示。','3803':'fonfunとの業務提携契約を7/21締結。','4820':'中間連結経常予想を上方修正。通期・配当は据置。','6200':'3Q累計経常4.6%増、当時記事の単独3Q増益も確認。通期据置。','6769':'中間最終赤字縮小、通期最終利益予想増額。通期営業・経常は据置。','7602':'SuperXグループとの業務委託基本契約と運送委託契約を締結。売上規模・業績への寄与確度の加点なし。','9274':'自社株取得枠を300→600万株、36→72億円に拡大。既存の枠だが増額の新開示としてbuyback。','3840':'東京医科大学との共同研究契約締結決定。売上受注ではなく支出を伴い得る研究契約、固定contract分類で規模加点なし。','4889':'KAIMRCとClinical Trial Agreementを締結し第1相試験開始。従来のMOUから契約へ移行を原資料で確認。','3951':'自社株買い58万株・5億円上限。','4073':'キャッシュレス端末リプレイス案件463百万円受注、27年6月期計上予定。','4415':'AlbaLinkと業務提携契約を締結。','6045':'6月売上前年比1157.1%。子会社の連結範囲拡大を含み既存事業の同条件成長とは区別。規模加点なし。','6083':'カーボンフリーコンサルティングの株式取得、任意開示。','6193':'CRMソフトと音声認識のAPI連携に対応、利用可能。新受注ではなくproduct。','8708':'1Q最終速報が前年同期比増益。Yahoo403をJPX転載で補完。正式発表の将来値不使用。','9820':'ネクスト全株式取得で子会社化決議。','3121':'AI防犯カメラの合弁会社新設を合意・取締役会決議。jv_mou2点。','4404':'株式売却益541百万円、通期予想に織込済み。','6088':'株式売却益528百万円、通期予想に織込済み。'}
 for c,typ in types.items():
  at={'278A':'17:00','4820':'16:00','6200':'17:00','7602':'16:30','9274':'19:00','3840':'16:30','3951':'16:30','4415':'16:00','8708':'16:30','3121':'16:30','4404':'16:30','6088':'16:00'}.get(c,'15:30')
  file='jb5_pdf22_retry8708.json' if c=='8708' else 'jb5_pdf22_'+c+'.json'
  r[c]=release(pdfurl(file),'2026-07-21T'+at+':59+09:00','2026-07-22','7/21原開示本文・日付、転載時刻と当時記事を照合。'+notes[c]);e[c]=[typ]
 save(ROOT/'data/july_releases_22.json',r);save(ROOT/'data/july_events_22.json',e)
 price_url['2026-07-21']='https://kabu.kininew.net/fiveup/8033.html'
 build('2026-07-22','2026-07-21','jb5_actual21_complete.json',['jb5_morning22.json','jb5_evening22.json'],r,e,{**PENALTIES,'9439':{'dilution':True},'9553':{'dilution':True}})

if __name__=='__main__':globals()['run'+sys.argv[1]]()
