import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def texts(p):
 x=json.loads(p.read_text());x=x.get('value',x)
 return '\n'.join(c.get('text','') for c in x.get('content',[]))
def ranking(text):
 rows=[]
 for line in text.splitlines():
  m=re.search(r'【\d+†([0-9A-Z]{4})†[^】]*】(?:☆)?\s*\|\s*([^|]+)\|\s*東([ＰＳＧＰSGPＧＳ])\s*\|\s*([\d,.]+)\s*\|\s*([+−-]?[\d,.]+)\s*\|\s*([+−-]?[\d.]+)%\s*\|\s*([\d,]+)',line)
  if m:
   code,name,market,close,change,pct,volume=m.groups();market=market.translate(str.maketrans('ＰＳＧ','PSG'))
   rows.append(dict(code=code,name=name.strip(),market=market,close=float(close.replace(',','')),change=float(change.replace(',','')),return_pct=float(pct),volume=int(volume.replace(',',''))))
 unique={r['code']:r for r in rows};return list(unique.values())
def digest_candidates(text):
 rows={}
 for line in text.splitlines():
  m=re.search(r'(?:■|★)?([^【]+)【\d+†<([0-9A-Z]{4})>】\s*\[東証([ＰＳＧ])\]',line)
  if m:
   name,code,market=m.groups();name=re.sub(r'^L\d+:\s*','',name).strip(' ★■')
   rows[code]={'code':code,'name':name,'market':market.translate(str.maketrans('ＰＳＧ','PSG'))}
 return rows
def evidence(id,url,stamp,verified,note):
 return dict(id=id,url=url,available_at=stamp,version_verified=verified,timestamp_evidence=note,role='predictor')
def build(day,prior,ranking_file,digest_files,releases,events,penalties=None):
 price=ranking(texts(ROOT/'evidence'/ranking_file));assert len(price)>=10
 news={}
 for f in digest_files:news.update(digest_candidates(texts(ROOT/'evidence'/f)))
 pe='price_'+prior;ev=[evidence(pe,price_url[prior],prior+'T23:59:59+09:00',True,'前営業日の引け後公表日付き価格表。日付精度のため当日末を採用。動的関連欄は不使用。全原票による完全性保証はなし。')]
 candidates={r['code']:dict(code=r['code'],name=r['name'],market=r['market'],eligible_ordinary=True,previous_return_pct=r['return_pct'],evidence_ids=[pe],events=[]) for r in price}
 for code,row in news.items():
  if code not in candidates:candidates[code]=dict(**row,eligible_ordinary=True,previous_return_pct=None,evidence_ids=[],events=[])
 for code,row in candidates.items():
  if code in releases:
   rel=releases[code];eid='release_'+code+'_'+rel['first'];ev.append(evidence(eid,rel['url'],rel['at'],True,rel['verified_by']))
   row['evidence_ids'].append(eid)
   for typ in events.get(code,[]):row['events'].append(dict(evidence_id=eid,type=typ,first_eligible_session=rel['first']))
  elif not row['evidence_ids']:
   eid='unverified_'+code;ev.append(evidence(eid,'https://s.kabutan.jp/',prior+'T23:59:59+09:00',False,'日付付き記事で候補抽出したが原開示照合未了。採点対象から除外。'));row['evidence_ids']=[eid]
  if penalties and code in penalties:row.update(penalties[code])
 coverage=dict(universe='前日5%以上上昇の東証普通株＋取得ニュース掲載普通株。原開示照合未了のニュースのみ候補は除外',price_rows=len(price),news_rows=len(news),union_rows=len(candidates),full_tse=False,long_ohlcv=False,revision_archive_limit='日付付き原開示の内容を当時記事と照合。第三者タイムスタンプによる改訂不存在の証明ではない。',missing_return='5%以上表にない銘柄の前日騰落率は未取得、0点。0%と認定しない。',future_exposure='非盲検の過去再現。検索の偶発的な将来記事表示あり、入力に不採用。')
 x=dict(date=day,coverage=coverage,evidence=ev,candidates=list(candidates.values()));save(ROOT/f'data/july_inputs/{day}.json',x)
 print(json.dumps({'date':day,'price':len(price),'news':len(news),'union':len(candidates)},ensure_ascii=False))
price_url={'2026-06-30':'https://kabu.kininew.net/fiveup/7898.html'}
