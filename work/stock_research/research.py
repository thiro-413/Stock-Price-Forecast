#!/usr/bin/env python3
"""3営業日単位の調査集計・時刻検査・封印済み予測の評価。標準ライブラリのみ。"""
import argparse
import calendar
import csv
import hashlib
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
JST = ZoneInfo('Asia/Tokyo')

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def trading_days(month):
    # この調査で使用する2026年6・7月のみ。7/20は現物株休業日。
    if month not in (6, 7):
        raise ValueError('検証済みカレンダーは2026年6・7月のみ')
    return [date(2026, month, d).isoformat() for d in range(1, calendar.monthrange(2026, month)[1]+1)
            if date(2026, month, d).weekday() < 5 and (month, d) != (7, 20)]

def batch_days(month, batch):
    days = trading_days(month)[(batch-1)*3:batch*3]
    if not days:
        raise ValueError('バッチ番号範囲外')
    return days

def gate(records, cutoff):
    """後日取得でも当時の本文版を確認できる証拠を要求。日付だけは採用しない。"""
    cutoff = datetime.fromisoformat(cutoff)
    if cutoff.tzinfo is None:
        raise ValueError('cutoffにタイムゾーンが必要')
    accepted, rejected = [], []
    for item in records:
        reason = None
        try:
            stamp = datetime.fromisoformat(item['available_at'])
            if stamp.tzinfo is None:
                reason = 'timezone_missing'
            elif stamp > cutoff:
                reason = 'after_cutoff'
            elif not item.get('url') or not item.get('timestamp_evidence'):
                reason = 'source_or_timestamp_evidence_missing'
            elif item.get('version_verified') is not True:
                reason = 'historical_content_version_unverified'
            elif item.get('role') != 'predictor':
                reason = 'not_predictor_information'
        except (KeyError, ValueError, TypeError):
            reason = 'timestamp_missing_or_invalid'
        if reason:
            rejected.append({'record': item, 'reason': reason})
        else:
            accepted.append(item)
    return {'cutoff': cutoff.isoformat(), 'accepted': accepted, 'rejected': rejected}

def seal(day, predictions, evidence, model):
    if len(predictions) != 10 or len({p['code'] for p in predictions}) != 10:
        raise ValueError('重複のない10銘柄が必要')
    if model.get('status') != 'frozen' or model.get('training_end') != '2026-06-30':
        raise ValueError('6月分析完了後に固定したモデルが必要')
    if not model.get('artifact_sha256'):
        raise ValueError('モデルの内容ハッシュが必要')
    eligible = gate(evidence, day+'T08:30:00+09:00')
    allowed = {x['id'] for x in eligible['accepted']}
    for pred in predictions:
        if not pred.get('evidence_ids') or not set(pred['evidence_ids']).issubset(allowed):
            raise ValueError('予測根拠に未検証または締切後の情報がある')
    payload = {'date': day, 'cutoff': eligible['cutoff'], 'predictions': predictions,
               'model': model, 'evidence': eligible['accepted'],
               'limitation': '過去再現検証。ハッシュは改変検出用で、事前予測の第三者証明ではない。'}
    return {'payload': payload, 'sha256': digest(payload), 'exclusions': eligible['rejected']}

def evaluate(sealed, actual):
    payload = sealed['payload']
    if digest(payload) != sealed['sha256']:
        raise ValueError('予測封印後の改変を検出')
    if actual['date'] != payload['date'] or actual.get('top10_verified') is not True:
        raise ValueError('同日で順位と母集団を確認した実績が必要')
    rows = actual['top10']
    if len(rows) != 10 or len({x['code'] for x in rows}) != 10:
        raise ValueError('実績上位10件が不正')
    ranks = {x['code']: i+1 for i, x in enumerate(rows)}
    details = [{'predicted_rank': i+1, 'code': p['code'], 'actual_rank': ranks.get(p['code']),
                'result': 'hit_top10' if p['code'] in ranks else 'outside_top10'}
               for i,p in enumerate(payload['predictions'])]
    predicted = {p['code'] for p in payload['predictions']}
    hits = sum(x['result']=='hit_top10' for x in details)
    return {'date': payload['date'], 'hits': hits, 'precision_at_10': hits/10,
            'recall_at_10': hits/10,
            'exact_rank_hits': sum(x['actual_rank']==x['predicted_rank'] for x in details),
            'predictions': details,
            'missed_winners': [dict(x, actual_rank=i+1) for i,x in enumerate(rows) if x['code'] not in predicted],
            'note': '上位10外の正確な順位は全銘柄実績がない限り算出しない。利益率とは異なる。'}

def report(batch=1):
    if batch not in (1, 2, 3, 4, 5, 6, 7, 8):
        raise ValueError('収集済みバッチは1〜8のみ')
    prefix = f'batch{batch:02d}'
    ranking_file = 'rankings.csv' if batch==1 else prefix+'_rankings.csv'
    analysis_file = 'analysis.json' if batch==1 else prefix+'_analysis.json'
    source_ids = {'2026-06-01':'7698','2026-06-02':'7708','2026-06-03':'7716',
                  '2026-06-04':'7724','2026-06-05':'7734','2026-06-08':'7745',
                  '2026-06-09':'7753','2026-06-10':'7762','2026-06-11':'7771',
                  '2026-06-12':'7785','2026-06-15':'7795','2026-06-16':'7805',
                  '2026-06-17':'7813','2026-06-18':'7823','2026-06-19':'7832',
                  '2026-06-22':'7843','2026-06-23':'7851','2026-06-24':'7860',
                  '2026-06-25':'7869','2026-06-26':'7878','2026-06-29':'7889',
                  '2026-06-30':'7898'}
    with (ROOT/'data'/ranking_file).open(encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    notes = json.loads((ROOT/'data'/analysis_file).read_text())
    days = batch_days(6, batch)
    output = ROOT/'results'
    output.mkdir(exist_ok=True)
    result = []
    for day in days:
        daily = [r for r in rows if r['date']==day]
        if len(daily)!=10 or len({r['code'] for r in daily})!=10:
            raise ValueError('日別件数または銘柄重複エラー')
        if [int(r['rank']) for r in daily] != list(range(1,11)):
            raise ValueError('順位番号不正')
        if any(r['market'] not in ('P','S','G') for r in daily):
            raise ValueError('対象外市場')
        rates=[]
        for r in daily:
            r = dict(r)
            r['close'],r['change'] = float(r['close']),float(r['change'])
            r['previous_close_derived'] = r['close']-r['change']
            r['return_pct'] = 100*r['change']/r['previous_close_derived']
            if abs(r['return_pct']-float(r['reported_pct']))>0.011:
                raise ValueError('騰落率と価格不一致')
            category,trend,psychology,timing,confidence,url = notes[day][r['code']]
            r.update(category=category, trend=trend, psychology_hypothesis=psychology,
                     timing=timing, evidence_grade=confidence, material_source=url,
                     ranking_source='https://kabu.kininew.net/fiveup/'+
                     source_ids[day]+'.html')
            rates.append(r['return_pct'])
            result.append(r)
        if rates!=sorted(rates,reverse=True):
            raise ValueError('順位不一致')
    dump(output/(prefix+'_data.json'), result)
    with (output/(prefix+'_data.csv')).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(result[0]));writer.writeheader();writer.writerows(result)
    markets=Counter(r['market'] for r in result)
    unique=len({r['code'] for r in result})
    unknown=sum(r['evidence_grade']=='U' for r in result)
    lines=[f'# 第{batch}回：'+ '・'.join(days)+' 上昇率分析', '',
      '対象：東証P/S/Gの普通株、前営業日終値比の当日終値上昇率上位10。ETF・ETN・REIT・地方単独上場を除外。',
      f'調査実施日：2026年10月{15 if batch==1 else 16}日。これは6月の事後分析であり、朝の予測結果ではない。', '',
      f'集計：{len(result)}銘柄日、実銘柄{unique}。市場別は'+str(dict(markets))+f'。原因未特定扱い{unknown}銘柄日。', '',
      '数値検査：各日10件・重複なし・順位・上昇率の算術を確認。全上場銘柄の原票を取得して再ソートしたものではない。第1回・第4回・第6回はJPX原票を一部照合。第4回は6/12の別表に前日値転載があり、その上昇欄を不採用。その他は二次集計表・当日報道を照合。', '',
      'A＝公式発表の内容を確認、B＝報道・二次資料、U＝直接原因未特定。Aでも値動きとの因果関係の証明にはならない。心理欄は全件推測。']
    for day in days:
        lines += ['',f'## {day}', '', '|順位|コード・銘柄|前日終値→終値|上昇率|出来高|', '|---:|---|---:|---:|---:|']
        for r in result:
            if r['date']==day:
                lines.append(f"|{r['rank']}|{r['code']} {r['name']}|{r['previous_close_derived']:g}→{r['close']:g}|{r['return_pct']:.2f}%|{int(r['volume']):,}|")
        lines+=['','### 個別分析','']
        for r in result:
            if r['date']==day:
                lines += [f"- **{r['code']} {r['name']}／{r['category']}（{r['evidence_grade']}）**：{r['trend']} 心理仮説：{r['psychology_hypothesis']} 時間区分：{r['timing']}。[資料]({r['material_source']})"]
    (output/(prefix+'_report.md')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    schedule={phase:[{'batch': i//3+1,'days':td[i:i+3]} for i in range(0,len(td),3)]
              for phase,td in [('june_learning',trading_days(6)),('july_prediction',trading_days(7)),('july_error_analysis',trading_days(7))]}
    dump(output/'schedule.json',schedule)
    old = json.loads((output/'state.json').read_text()) if (output/'state.json').exists() else {}
    next_days = batch_days(6,batch+1) if batch<8 else batch_days(7,1)
    if old.get('completed_batch', 0)<=batch:
      dump(output/'state.json', {'phase':'june_learning' if batch<8 else 'june_top10_review_complete','completed_batch':batch,'next_days':next_days,
                              'requires_user_continue':True,'july_predictions_created':False,
                              'screening_prompt_created':False,'model_status':'not_frozen',
                              'data_hash':digest(result)})
    print(json.dumps({'rows':len(result),'unique_stocks':unique,'unknown_cause_rows':unknown,
                      'markets':dict(markets),'next_days':next_days,
                      'june_days':len(trading_days(6)),'july_days':len(trading_days(7)),
                      'checks':'passed','report':str(output/(prefix+'_report.md'))},ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['report','gate','evaluate'])
    ap.add_argument('--input');ap.add_argument('--actual');ap.add_argument('--cutoff')
    ap.add_argument('--batch',type=int,default=1);args=ap.parse_args()
    if args.command=='report': report(args.batch)
    elif args.command=='gate':
        print(json.dumps(gate(json.loads(Path(args.input).read_text()),args.cutoff),ensure_ascii=False,indent=2))
    else:
        print(json.dumps(evaluate(json.loads(Path(args.input).read_text()),json.loads(Path(args.actual).read_text())),ensure_ascii=False,indent=2))
