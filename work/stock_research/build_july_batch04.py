"""July 14–16 inputs. The frozen model and earlier sealed predictions stay unchanged."""
import json,sys
from prepare_july import ROOT,save,build,price_url
from build_july_batch02 import pdfurl,release

PENALTIES={'3133':{'negative_material':True},'4575':{'negative_material':True},'2751':{'negative_material':True},'3490':{'dilution':True},'6522':{'margin_restriction':True}}

def run14():
 r=json.loads((ROOT/'data/july_releases_13.json').read_text());e=json.loads((ROOT/'data/july_events_13.json').read_text())
 notes={'1401':'前期経常40.6%増、翌期非開示。増益実績を分類。','2186':'1Q経常2.6%増、最終8.8%減、通期据置。','2305':'1Q経常6.3%増、最終29%減。','3075':'1Q経常46.9%増。','3080':'1Q経常6%増、最終3.6%減。','3168':'通期経常2607→4557百万円、74.8%上方修正。銅価格転嫁、米国子会社等が寄与。','3236':'翌期経常増益予想。連結化で前期との比較範囲の差あり。','3900':'営業利益予想-1000～0→0～300百万円。前期比ではなく従来予想からの上方修正。','4076':'翌期経常増益予想、増配。','463A':'翌期経常増益予想。持株会社移行前の比較範囲に注意。','6159':'3Q累計経常28.5%増、営業93.3%減。為替等を含む経常増益を固定分類。','4199':'サンリオとの共同開発契約を本日締結と原開示に明記。効力発生日6/1だが公表は7/13。業績影響軽微。赤字縮小自体には専用加点せずcontract4点。'}
 for c,note in notes.items():
  at={'1401':'16:00','3080':'16:00','3236':'15:40','6159':'15:40'}.get(c,'15:30')
  r[c]=release(pdfurl('jb4_pdf14_'+c+'.json'),'2026-07-13T'+at+':59+09:00','2026-07-14','7/13原開示本文・日付、TDnet転載一覧時刻、当時記事を照合。'+note)
  e[c]=['contract'] if c=='4199' else ['earnings_up']
 save(ROOT/'data/july_releases_14.json',r);save(ROOT/'data/july_events_14.json',e)
 price_url['2026-07-13']='https://kabu.kininew.net/fiveup/7982.html'
 build('2026-07-14','2026-07-13','jb3_actual13.json',['jb4_morning14.json','jb4_evening14.json'],r,e,PENALTIES)

def run15():
 r=json.loads((ROOT/'data/july_releases_14.json').read_text());e=json.loads((ROOT/'data/july_events_14.json').read_text())
 notes={'1434':'3Q累計経常122.5%増。','156A':'3Q累計経常49.2%増。','3030':'1Q経常42%増、最終24.2%減。','3083':'1Q経常-24→54百万円の黒字転換、最終赤字拡大。','365A':'1Q経常-238→293百万円、為替差益を含む。','3760':'翌期経常1550百万円・最終1200百万円の黒字転換予想。前期赤字実績とは区別。','4616':'中間経常210百万円、前年18百万円、予想超過。当時記事は黒字浮上との表現だが原短信の前年は正。増益分類は原資料に従い、矛盾を記録。','464A':'翌期営業-833→300百万円黒字予想。持株会社化による比較範囲の差あり。','505A':'翌期経常増益予想。','5246':'通期経常-100～100→200～300百万円に上方修正。','5575':'翌期経常増益予想。Yahoo PDF403をJPX転載の同じ原開示で補完。','5885':'翌期経常増益予想。','6083':'翌期経常増益予想、増配。','7083':'中間経常予想12→実績51百万円、前年38。通期据置。','7673':'翌期経常9.4%増予想。','9326':'1Q経常-44→76百万円黒字転換。Yahoo PDF403をJPX転載で補完。','9812':'翌期経常47→80百万円、67%増。記事70%は丸め前後差。復配0.5円。'}
 for c,note in notes.items():
  at={'3083':'16:00','464A':'16:30','505A':'16:00','5246':'16:00','9326':'16:00'}.get(c,'15:30')
  file=('jb4_pdf15_retry'+c if c in ['5575','9326'] else 'jb4_pdf15_'+c)+'.json'
  r[c]=release(pdfurl(file),'2026-07-14T'+at+':59+09:00','2026-07-15','7/14原開示本文・日付、TDnet転載一覧時刻、当時記事を照合。'+note);e[c]=['earnings_up']
 save(ROOT/'data/july_releases_15.json',r);save(ROOT/'data/july_events_15.json',e)
 price_url['2026-07-14']='https://kabu.kininew.net/fiveup/7994.html'
 build('2026-07-15','2026-07-14','jb4_actual14.json',['jb4_morning15.json','jb4_evening15.json'],r,e,PENALTIES)

def run16():
 r=json.loads((ROOT/'data/july_releases_15.json').read_text());e=json.loads((ROOT/'data/july_events_15.json').read_text())
 notes={'1418':'1Q経常76.7%増。同日BBTへの自己株式処分は新株発行ではなく希薄化専用減点なし。','150A':'通期経常予想を上方修正。','205A':'翌期経常増益予想。','2404':'3Q累計経常81.2%増、記事82%と微差。','2437':'翌期経常-161→150百万円黒字転換予想。前期実績の下振れを新年度予想の下方修正とは混同しない。','2934':'翌期最終黒字転換予想、前期経常79.3%増。','3449':'通期経常予想48%増額、増配。','3479':'1Q経常42.7%増。','3547':'通期経常上方修正。','3558':'1Q経常62.1%増。','3645':'翌期経常増益予想、前期経常99.8%増。','372A':'翌期経常増益予想、増配。社員持株会への自己株式処分は新株発行ではない。','4412':'通期経常148→218百万円、46.9%増額。','4490':'1Q経常40.9%増。','7610':'1Q経常309.5%増。','7719':'1Q経常678.2%増、記事8.2倍と差あり原短信優先。監理銘柄指定はJPXの2026/3/25公表により3/26解除済み、https://www.jpx.co.jp/news/1021/20260325-21.html と照合し減点しない。','7997':'通期最終40→90百万円、営業・経常据置。','8887':'翌期経常増益予想。持株会社への移行に伴う比較範囲に留意。','9252':'3Q累計最終73.1%増。','9978':'3Q累計経常15.4%増。'}
 for c,note in notes.items():
  at={'1418':'16:00','150A':'16:00','3547':'16:30','7610':'16:00','7719':'16:00','9252':'16:00'}.get(c,'15:30')
  r[c]=release(pdfurl('jb4_pdf16_'+c+'.json'),'2026-07-15T'+at+':59+09:00','2026-07-16','7/15原開示本文・日付、TDnet転載一覧時刻または当時記事・会社公表日を照合。'+note);e[c]=['earnings_up']
 save(ROOT/'data/july_releases_16.json',r);save(ROOT/'data/july_events_16.json',e)
 price_url['2026-07-15']='https://kabu.kininew.net/fiveup/8006.html'
 build('2026-07-16','2026-07-15','jb4_actual15.json',['jb4_morning16.json','jb4_evening16.json'],r,e,PENALTIES)

if __name__=='__main__':
 globals()['run'+sys.argv[1]]()
