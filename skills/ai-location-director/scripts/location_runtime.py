#!/usr/bin/env python3
"""Location production helpers. Diagnostics never certify visual fidelity."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path


def audit(d, base=Path('.')):
    errors, pending = [], []
    def registry(key):
        rows=d.get(key, [])
        ids=[r.get('id') for r in rows]
        if len(ids)!=len(set(ids)) or any(not x for x in ids): errors.append(key+': missing/duplicate IDs')
        return {r['id']:r for r in rows if r.get('id')}
    refs=registry('reference_register'); cams=registry('cameras'); outs=registry('outputs')
    objects=registry('objects'); routes=registry('routes'); lights=registry('lights'); states=registry('states')
    for rid,r in refs.items():
        if r.get('status') not in ['proposed','approved','superseded']: errors.append(rid+': invalid reference status')
        if r.get('status')=='approved' and not r.get('approval_evidence'): errors.append(rid+': missing approval evidence')
        if r.get('status')=='approved' and not r.get('version'): errors.append(rid+': missing version')
        if r.get('path'):
            p=Path(r['path']); p=p if p.is_absolute() else base/p
            if not p.is_file(): pending.append(rid+': reference file unavailable')
            elif r.get('sha256') and hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']: errors.append(rid+': reference content changed')
        else: pending.append(rid+': reference path missing')
    for cid,c in cams.items():
        for rid in c.get('reference_ids',[]):
            if rid not in refs or refs[rid].get('status')!='approved': errors.append(cid+': inactive/unapproved reference '+rid)
    for row in d.get('scene_coverage',[]):
        label=row.get('id','coverage')
        for field in ['scene_id','action','surface_ids','camera_ids','output_ids']:
            if not row.get(field): errors.append(label+': missing '+field)
        for key,reg in [('surface_ids',objects),('camera_ids',cams),('output_ids',outs),('route_ids',routes)]:
            for oid in row.get(key,[]):
                if oid not in reg: errors.append(label+': unknown '+key+' '+oid)
        for cid in row.get('camera_ids',[]):
            visible=set(cams.get(cid,{}).get('visible_object_ids',[]))
            if visible.intersection(row.get('excluded_object_ids',[])): errors.append(label+': excluded object visible in '+cid)
        if row.get('feasibility_status')!='PASS': pending.append(label+': camera/route feasibility not inspected')
        elif not row.get('feasibility_evidence'): errors.append(label+': feasibility PASS lacks evidence')
        for oid in row.get('output_ids',[]):
            if oid in outs and outs[oid].get('status')!='approved': pending.append(label+': unfinished output '+oid)
    for lid,l in lights.items():
        if not l.get('direction_world') or not l.get('white_balance_kelvin') or not l.get('exposure_reference_id'): pending.append(lid+': lighting lock incomplete')
        if l.get('exposure_reference_id') and l['exposure_reference_id'] not in refs: errors.append(lid+': unknown exposure reference')
    for sid,s in states.items():
        if s.get('light_id') and s['light_id'] not in lights: errors.append(sid+': unknown light preset')
    for cid,c in cams.items():
        s=states.get(c.get('state_id'),{})
        if s.get('light_id') and s['light_id']!=c.get('light_id'): errors.append(cid+': camera/state lighting mismatch')
    deps={oid:o.get('depends_on_output_ids',[]) for oid,o in outs.items()}
    done=set(); visiting=set()
    def walk(oid):
        if oid in visiting: errors.append('Output dependency cycle: '+oid); return
        if oid in done:return
        visiting.add(oid)
        for dep in deps.get(oid,[]):
            if dep not in outs: errors.append(oid+': missing dependency '+dep)
            else:
                if outs[oid].get('status')=='approved' and outs[dep].get('status') in ['stale','superseded']: errors.append(oid+': stale dependency '+dep)
                walk(dep)
        visiting.remove(oid);done.add(oid)
    for oid in outs:walk(oid)
    if d.get('stage')=='delivered':
        if pending: errors.append('Delivered claim has pending production checks')
        if not refs: errors.append('Delivered pack lacks a reference register')
        if d.get('mode')!='props-only' and not d.get('scene_coverage'): errors.append('Delivered location pack lacks scene/brief coverage')
    return {'structure':'FAIL' if errors else 'PASS','errors':errors,'pending':pending,'note':'Text/registry checks only; no image or physical-clearance certification.'}


def impact(d, kind, ids):
    """Return directly and transitively affected outputs; retain unaffected approvals."""
    ids=set(ids); cameras={c['id']:c for c in d.get('cameras',[])}
    affected=set(); uncertain=set()
    for o in d.get('outputs',[]):
        c=cameras.get(o.get('camera_id'),{})
        direct=False
        if kind=='output': direct=o['id'] in ids
        elif kind=='object':
            if 'visible_object_ids' not in c and 'boundary_object_ids' not in c and 'object_ids' not in o and not o.get('prop_id'): uncertain.add(o['id'])
            direct=bool(ids.intersection(c.get('visible_object_ids',[])+o.get('object_ids',[])))
            # Neighbor/boundary cameras can be affected even when object is occluded.
            direct=direct or bool(ids.intersection(c.get('boundary_object_ids',[])))
        elif kind=='reference': direct=bool(ids.intersection(c.get('reference_ids',[])+o.get('reference_ids',[])))
        elif kind=='light': direct=c.get('light_id') in ids or o.get('light_id') in ids
        elif kind=='state': direct=c.get('state_id') in ids or o.get('state_id') in ids
        elif kind=='prop': direct=o.get('prop_id') in ids or bool(ids.intersection(o.get('prop_ids',[])))
        elif kind=='camera':direct=o.get('camera_id') in ids
        if direct:affected.add(o['id'])
    while True:
        more={o['id'] for o in d.get('outputs',[]) if affected.intersection(o.get('depends_on_output_ids',[]))}
        if more<=affected:break
        affected|=more
    return {'affected_output_ids':sorted(affected),'unmapped_output_ids':sorted(uncertain-affected),'note':'Review unmapped visibility and boundary/adjacent cameras before accepting unaffected status.'}


def invalidate(d, report):
    d=copy.deepcopy(d); affected=set(report['affected_output_ids'])
    for o in d.get('outputs',[]):
        if o['id'] in affected and o.get('status') not in ['superseded','planned']:o['status']='stale'
    for q in d.get('qc',[]):
        if q.get('output_id') in affected:q.update(status='PENDING',evidence='Invalidated by dependency change; rerun affected check')
    for r in d.get('reviews',[]):
        if r.get('candidate_id') in affected:r['state']='stale'
    if affected:d['stage']='revision_requested'
    return d


def telemetry(d):
    rows=d.get('attempts',[]); elapsed={}; by_output={}
    for r in rows:
        secs=r.get('elapsed_seconds')
        if isinstance(secs,(int,float)) and not isinstance(secs,bool) and secs>=0:elapsed[r.get('phase','unknown')]=elapsed.get(r.get('phase','unknown'),0)+secs
        by_output.setdefault(r.get('output_id','unknown'),[]).append(r)
    actions={}
    limit=d.get('execution_policy',{}).get('max_same_failure_attempts',2)
    for oid,rs in by_output.items():
        failures=[r for r in rs if r.get('result')=='FAIL']
        if failures:
            last=failures[-1]; streak=0
            for r in reversed(rs):
                if r.get('result')=='FAIL' and r.get('failure_signature')==last.get('failure_signature'):streak+=1
                else:break
            if streak>=limit:actions[oid]='Change reference/camera/method before another attempt; preserve locks. If no supported alternative, report blocked.'
    return {'elapsed_seconds_by_phase':elapsed,'attempt_count':len(rows),'retry_actions':actions,'note':'Observed work time only; no promised response time or quality score.'}


def blockout(d, directory):
    """Export real box mesh OBJ and sharp wireframe camera references, not beauty photos."""
    from PIL import Image, ImageDraw
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    vertices=[]; faces=[]
    for obj in d.get('objects',[]):
        if obj.get('geometry_kind')!='box':
            raise ValueError('Blockout requires explicit geometry_kind=box: '+obj['id']+'; openings must be modeled as separate solid segments')
        if obj.get('pivot')!='centre':raise ValueError('Box helper requires pivot=centre: '+obj['id'])
        if any(obj.get('rotation_deg',[0,0,0])[:2]):raise ValueError('Box helper supports Z rotation only')
        w,h,z=obj['dimensions_m']; x,y,cz=obj['position_m']; a=math.radians(obj['rotation_deg'][2]); n=len(vertices)
        for dx,dy,dz in [(-w/2,-h/2,-z/2),(w/2,-h/2,-z/2),(w/2,h/2,-z/2),(-w/2,h/2,-z/2),(-w/2,-h/2,z/2),(w/2,-h/2,z/2),(w/2,h/2,z/2),(-w/2,h/2,z/2)]:
            vertices.append((x+dx*math.cos(a)-dy*math.sin(a),y+dx*math.sin(a)+dy*math.cos(a),cz+dz))
        faces.extend(tuple(n+i for i in face) for face in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)])
    if not vertices:raise ValueError('No explicit box solids supplied')
    objpath=directory/'blockout.obj'
    objpath.write_text('\n'.join(['# Reference blockout; not approved architecture']+['v %g %g %g'%v for v in vertices]+['f '+' '.join(str(i+1) for i in face) for face in faces])+'\n')
    def norm(v):
        length=math.sqrt(sum(x*x for x in v))
        if length<1e-9:raise ValueError('Degenerate camera basis')
        return [x/length for x in v]
    def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
    rendered=[]
    for c in d.get('cameras',[]):
        if c.get('projection') not in ['perspective','orthographic']:continue
        p=c['position_m']; f=norm([t-v for t,v in zip(c['target_m'],p)]); right=norm(cross(f,c['up'])); up=cross(right,f)
        aw,ah=c['aspect']; W=960;H=round(W*ah/aw)
        if H<1 or H>4096:raise ValueError('Unsupported diagnostic aspect')
        near=c.get('near_clip_m',0.01)
        if near<=0:raise ValueError('Near clip must be positive')
        def project(v):
            dv=[v[i]-p[i] for i in range(3)]; depth=sum(a*b for a,b in zip(dv,f))
            if depth<=near:return None
            xx=sum(a*b for a,b in zip(dv,right)); yy=sum(a*b for a,b in zip(dv,up))
            if c['projection']=='perspective':
                if c.get('sensor_fit') not in ['horizontal']:raise ValueError('Diagnostic perspective requires explicit horizontal sensor fit')
                factor=W*c['lens_mm']/c['sensor_width_mm']/depth
            else:factor=W/c['ortho_scale_m']
            return (W/2+xx*factor,H/2-yy*factor)
        pts=[project(v) for v in vertices];im=Image.new('RGB',(W,H),'white'); draw=ImageDraw.Draw(im)
        for face in faces:
            for a,b in zip(face,face[1:]+face[:1]):
                if pts[a] is not None and pts[b] is not None:draw.line([pts[a],pts[b]],fill='#425569',width=2)
        # IDs are stored in the manifest, not used as output paths.
        path=directory/('camera-%03d.png'%len(rendered));im.save(path);rendered.append({'camera_id':c['id'],'path':str(path),'pixels':[W,H]})
    scene=directory/'scene.json';scene.write_text(json.dumps(d,indent=2)+'\n')
    return {'model_path':str(objpath),'scene_manifest':str(scene),'camera_outputs':rendered,'limitations':'Wireframe diagnostics of explicit box solids only; no occlusion, near-plane segment clipping, materials, photometric lighting, collision, panorama or master-match certification. No automatic approval/status changes.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('command',choices=['audit','impact','invalidate','telemetry','blockout']);ap.add_argument('manifest',type=Path)
    ap.add_argument('--kind',choices=['object','reference','light','state','prop','camera','output']);ap.add_argument('--ids',nargs='+');ap.add_argument('--out',type=Path)
    a=ap.parse_args();d=json.loads(a.manifest.read_text())
    if a.command=='audit':result=audit(d,a.manifest.parent)
    elif a.command=='telemetry':result=telemetry(d)
    elif a.command=='blockout':
        if not a.out:ap.error('--out directory required')
        result=blockout(d,a.out)
    else:
        if not a.kind or not a.ids:ap.error('--kind and --ids required')
        result=impact(d,a.kind,a.ids)
        if a.command=='invalidate':
            if not a.out or a.out.resolve()==a.manifest.resolve():ap.error('--out must be a separate reviewable manifest path')
            a.out.write_text(json.dumps(invalidate(d,result),indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return 1 if a.command=='audit' and result['errors'] else 0
if __name__=='__main__':raise SystemExit(main())
