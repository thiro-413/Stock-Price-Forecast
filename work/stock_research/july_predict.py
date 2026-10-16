#!/usr/bin/env python3
"""固定ルールv1。全候補の採点を保存し、当日実績を読み込む前に予測を封印する。"""
import json,hashlib,sys
from pathlib import Path
from datetime import datetime
from research import gate,seal,trading_days
ROOT=Path(__file__).resolve().parent
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def freeze():
    target=ROOT/'data/july_model_frozen.json'
    if target.exists():raise ValueError('frozen model exists; do not overwrite')
    m=json.loads((ROOT/'data/july_model_v1.json').read_text())
    m['artifact_sha256']=sha(ROOT/'july_predict.py')
    m['specification_sha256']=sha(ROOT/'data/july_model_v1.json')
    m['frozen_at_utc']=datetime.now().astimezone().isoformat()
    save(target,m);print(json.dumps({'frozen':True,'model_hash':m['specification_sha256'],'code_hash':m['artifact_sha256']}))
def predict(day):
    model=json.loads((ROOT/'data/july_model_frozen.json').read_text())
    assert model['artifact_sha256']==sha(ROOT/'july_predict.py')
    assert model['specification_sha256']==sha(ROOT/'data/july_model_v1.json')
    source=ROOT/f'data/july_inputs/{day}.json'
    x=json.loads(source.read_text());assert x['date']==day
    evidence=x['evidence'];g=gate(evidence,day+'T08:30:00+09:00')
    allowed={e['id'] for e in g['accepted']}
    days=trading_days(6)+trading_days(7);today=days.index(day)
    scores=[];rejected=[]
    for row in x['candidates']:
        row=dict(row)
        if row.get('eligible_ordinary') is not True or not row.get('evidence_ids') or not set(row['evidence_ids']).issubset(allowed):
            rejected.append(row);continue
        ret=row.get('previous_return_pct')
        momentum=0 if ret is None else max(-2,min(3,ret/10))
        material=0
        for ev in row.get('events',[]):
            if ev['evidence_id'] not in allowed:continue
            age=today-days.index(ev['first_eligible_session'])
            base=model['features']['material_base'].get(ev['type'],0)
            weight=1 if age==0 else 0.5 if age in (1,2) else 0
            material=max(material,base*weight)
        market=1 if row['market'] in ('S','G') else 0
        dilution=-1 if row.get('dilution') else 0
        negative=-4 if row.get('negative_material') else 0
        margin=-1 if row.get('margin_restriction') else 0
        row.update(score=round(material+momentum+market+dilution+negative+margin,8),
          components={'material':material,'momentum':momentum,'market':market,
          'dilution':dilution,'negative':negative,'margin':margin},
          missing_momentum=ret is None)
        scores.append(row)
    scores.sort(key=lambda r:(-r['score'],-(r['previous_return_pct'] if r.get('previous_return_pct') is not None else -999),r['code']))
    assert len(scores)>=10
    target=ROOT/f'results/july_predictions/{day}.json'
    if target.exists():raise ValueError('sealed prediction exists; do not overwrite')
    prediction=scores[:10]
    payload=seal(day,prediction,evidence,model)
    payload['coverage']=x['coverage']
    payload['input_sha256']=sha(source)
    save(target,payload)
    save(ROOT/f'results/july_scores/{day}.json',{'candidates':scores,'rejected_candidates':rejected,'evidence_gate':g,'input_sha256':sha(source)})
    print(json.dumps({'date':day,'eligible_candidates':len(scores),'rejected_candidates':len(rejected),'predictions':[(r['code'],r['score']) for r in prediction],'seal':payload['sha256']},ensure_ascii=False))
if __name__=='__main__':
    freeze() if sys.argv[1]=='freeze' else predict(sys.argv[1])
