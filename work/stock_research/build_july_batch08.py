"""Final July session: verified pre-cutoff information; never regenerate old seals."""
import json
from prepare_july import ROOT,save,build,price_url,evidence
from build_july_batch02 import pdfurl,release
from build_july_batch07 import penalties,extra_events
DAY='2026-07-31'

def run():
 assert not (ROOT/f'results/july_predictions/{DAY}.json').exists(),'prediction already sealed'
 r=json.loads((ROOT/'data/july_releases_30.json').read_text());e=json.loads((ROOT/'data/july_events_30.json').read_text())
 codes=['299A','5333','5698','6471','6752','6754','6912','6946','6971','7575','8035','2914','4212','4308','4498','4661','6504','7148','7241','7976','8411','8424','2327','2579','3626','6080','6305','6371','6454','8174','8309','8425','9101','9709','9766']
 types={c:'earnings_up' for c in codes};types.update({'4092':'dividend_raise','6379':'dividend_raise','9621':'dividend_raise','4492':'acquisition','5449':'unknown','2811':'unknown'})
 files={c:'extra'+c for c in ['5333','5698','9101','9709','4092','6379','9621','5449']};files.update({'8174':'alt8174','4492':'final4492','2811':'retry2811'})
 times={'5333':'15:40','5698':'16:00','6912':'16:30','6946':'18:00','7575':'15:40','8035':'16:00','4212':'16:00','4661':'16:00','7148':'16:30','7241':'16:20','8424':'16:00','8309':'16:00','9709':'16:00','4092':'16:00','6379':'17:40','4492':'16:00','5449':'17:30','2811':'15:40'}
 notes={
 '299A':'当年連結経常910百万円、前年単体745百万円との比較で記事は約22%増。前年原短信を別証拠として照合。連結同士の同一母集団の成長率ではない。Non-GAAP営業利益18.5%増も原資料に明記。',
 '7148':'3Q累計経常は減益だが4-6月単独は増益。3Q累計17648/20186から既知中間11885/15828を引くと5763/4358百万円で約32%増。原中間短信を別証拠として保持。通期予想は据置。',
 '9709':'原短信1Q経常15.2%増。記事17%と相違するため原資料を優先。同じ利益改善分類。',
 '4308':'原短信1Q経常49.3%増。記事50%との丸め差を独自規模点にしない。',
 '4092':'未定だった期末を含む年間240円見込み、前期120円から増配。予想未定を無配からの復配としない。',
 '6379':'分割効力は10/1で7/31価格には未適用。分割前換算の年間117→118円で実質増配。',
 '9621':'年間配当予想78→110円。買戻しとの重複加算なし。',
 '4492':'クラステクノロジー全株取得を決議。経営統合等の他社・将来見出しを材料に混入しない。',
 '5449':'中間経常赤字への修正と通期経常減額。negative_material-4。',
 '2811':'通期最終予想13400→10500百万円へ下方修正、negative_material-4。',
 '2579':'中間最終黒字化。前年に大きな一時費用があり、その反動と持続的成長は区別。通期据置。',
 '6080':'3Q累計IFRS税引前利益増益、通期各利益の上方修正も原資料に記載。',
 '8411':'1Q経常・最終増益、通期最終予想上方修正。買戻し枠拡大は重複加算しない。',
 '8424':'1Q経常増益。共同事業化の株式取得は別の加点を足さず最大材料点のみ。',
 '8174':'Yahoo PDF503をJPX転載で補完。1Q経常増益と中間経常予想増額。',
 '6912':'中間・通期利益予想上方修正。',
 '7575':'1Q営業減益だが経常微増、通期予想下方修正ではない。',
 '6371':'1Q経常増益・最終減益。予想下方修正と区別。',
 '7241':'1Q経常増益・営業/最終減益。予想下方修正と区別。'}
 for c,typ in types.items():
  file='jb8_pdf31_'+files.get(c,c)+'.json'
  r[c]=release(pdfurl(file),'2026-07-30T'+times.get(c,'15:30')+':59+09:00',DAY,'日付付き原開示の社名・本文、公表時刻、当時記事を照合。'+notes.get(c,'原資料で利益改善・上方修正の方向を確認。複数材料は最大点のみ。'));e[c]=[typ]
 save(ROOT/'data/july_releases_31.json',r);save(ROOT/'data/july_events_31.json',e)
 p={**penalties(),'6663':{'negative_material':True},'4880':{'negative_material':True},'5449':{'negative_material':True},'2811':{'negative_material':True},'1382':{'negative_material':True},'5103':{'negative_material':True}}
 price_url['2026-07-30']='https://kabu.kininew.net/fiveup/8096.html'
 build(DAY,'2026-07-30','jb7_actual30_final.json',['jb8_morning31.json','jb8_evening31.json'],r,e,p)
 extra_events(DAY)
 path=ROOT/f'data/july_inputs/{DAY}.json';x=json.loads(path.read_text())
 supplement={
 '299A':('comparison_299A',pdfurl('jb8_pdf31_prior299A.json'),'2025-08-01T23:59:59+09:00','前年の原短信。dely（現クラシル）コード299A、1Q単体経常745百万円を確認。連結への移行を注記。'),
 '7148':('comparison_7148',pdfurl('jb8_pdf31_prior7148.json'),'2026-04-28T16:30:59+09:00','原中間短信。中間経常11885/15828百万円を3Q累計から差し引き、4-6月単独増益を照合。'),
 '1382':('supervision_1382','https://www.jpx.co.jp/news/1021/20260723-23.html','2026-07-23T23:59:59+09:00','JPX原発信で6/30公表の監理指定と7/23整理移行を確認。改善による解除ではないため監理に由来するnegative_materialを継続。上場廃止は将来の予定で、7/31の対象から除外しない。'),
 '5103':('supervision_5103','https://www.jpx.co.jp/news/1023/20260724-13.html','2026-07-24T23:59:59+09:00','JPX原発信で7/14監理指定、7/24整理移行を確認。改善解除ではなく上場廃止決定。negative_material-4を適用。過去の入力へ遡及反映しない。')}
 for code,(eid,url,at,note) in supplement.items():
  row=next((r for r in x['candidates'] if r['code']==code),None)
  if row:x['evidence'].append(evidence(eid,url,at,True,note));row['evidence_ids'].append(eid)
 x['coverage']['revision_archive_limit']+=' 夕方ダイジェストは訂正表題で訂正時刻未確認。記事を原資料の代用にせず、原資料と翌朝記事で材料方向を照合した項目だけ採用。'
 x['coverage']['future_exposure']+=' 動的サイドバーに31日09:03気配、JPX検索に31日引け後の監理指定見出しが偶発表示。締切後・将来情報として不採用。'
 save(path,x)
 save(ROOT/'data/july_batch08_comparison_checks.json',{'299A':{'previous_basis':'non-consolidated','current_basis':'consolidated','ordinary_profit_million_yen':[745,910],'note':'約22%増は同じ連結範囲での成長率ではない。原短信2件を照合。'},'7148':{'previous_ytd_3q':20186,'current_ytd_3q':17648,'previous_ytd_2q':15828,'current_ytd_2q':11885,'previous_q3':4358,'current_q3':5763,'growth_pct':100*(5763/4358-1)},'new_supervision_flags':['1382','5103'],'prior_seals_unchanged':True})
if __name__=='__main__':run()
