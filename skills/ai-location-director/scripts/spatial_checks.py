#!/usr/bin/env python3
"""Conservative solid-box checks; not mesh collision or complete visibility proof."""
import argparse
import json
import math
from pathlib import Path


def local(point,obj):
    if obj.get('geometry_kind')!='box' or obj.get('pivot')!='centre':raise ValueError(obj.get('id','object')+': requires centre-pivot box')
    rot=obj.get('rotation_deg',[0,0,0])
    if any(rot[:2]):raise ValueError(obj['id']+': only Z rotation supported')
    dims=obj['dimensions_m']
    if len(dims)!=3 or any(not math.isfinite(v) or v<=0 for v in dims):raise ValueError('Invalid box dimensions')
    a=math.radians(-rot[2]);v=[point[i]-obj['position_m'][i] for i in range(3)]
    return [v[0]*math.cos(a)-v[1]*math.sin(a),v[0]*math.sin(a)+v[1]*math.cos(a),v[2]]


def segment_box(a,b,obj,radius=0,height=0):
    """Sweep a feet point with square XY radius and vertical height against Z-rotated box."""
    a=local(a,obj);b=local(b,obj);half=[v/2 for v in obj['dimensions_m']]
    lo=[-half[0]-radius,-half[1]-radius,-half[2]-height];hi=[half[0]+radius,half[1]+radius,half[2]]
    enter,leave=0.,1.
    for i in range(3):
        delta=b[i]-a[i]
        if abs(delta)<1e-12:
            if a[i]<lo[i] or a[i]>hi[i]:return None
        else:
            u,v=(lo[i]-a[i])/delta,(hi[i]-a[i])/delta
            enter=max(enter,min(u,v));leave=min(leave,max(u,v))
            if enter>leave:return None
    return enter


def supported_objects(d):
    boxes=[];pending=[]
    for o in d.get('objects',[]):
        if o.get('collidable',True) is False:continue
        try:local(o['position_m'],o);boxes.append(o)
        except (ValueError,KeyError,TypeError) as e:pending.append({'object_id':o.get('id'),'reason':str(e)})
    return boxes,pending


def check_routes(d):
    boxes,pending=supported_objects(d);results=[]
    for route in d.get('routes',[]):
        radius=route.get('actor_radius_m');height=route.get('actor_height_m');points=route.get('points_m',[])
        if radius is None or height is None or not math.isfinite(radius) or not math.isfinite(height) or radius<0 or height<=0 or len(points)<2:
            results.append({'route_id':route.get('id'),'status':'PENDING','reason':'Supply measured/approved actor radius, height and two or more feet positions'});continue
        hits=[];support=set(route.get('support_object_ids',[]))
        for i,(a,b) in enumerate(zip(points,points[1:])):
            for o in boxes:
                if o['id'] in support:continue
                t=segment_box(a,b,o,radius,height)
                if t is not None:hits.append({'segment':i,'object_id':o['id'],'fraction':t})
        results.append({'route_id':route['id'],'status':'BLOCKED_OR_CONSERVATIVE_CONTACT' if hits else ('PENDING_UNMODELED_OBSTACLES' if pending else 'CLEAR_OF_MODELED_BOX_OBSTACLES'),'contacts':hits,'support_check':'PENDING: no ground adhesion, step climb, slope, balance or dynamic crowd simulation'})
    return {'routes':results,'unmodeled_obstacles':pending,'limitations':'Swept square actor envelope, conservative corner contacts; actual human/vehicle articulation and support still require inspection. Support IDs explicitly excluded from obstacle testing, never certified walkable.'}


def samples(obj):
    local(obj['position_m'],obj);p=obj['position_m'];half=[x/2 for x in obj['dimensions_m']];a=math.radians(obj.get('rotation_deg',[0,0,0])[2]);pts=[p]
    for x in [-half[0],half[0]]:
        for y in [-half[1],half[1]]:
            for z in [-half[2],half[2]]:pts.append([p[0]+x*math.cos(a)-y*math.sin(a),p[1]+x*math.sin(a)+y*math.cos(a),p[2]+z])
    return pts


def normalize(v):
    length=math.sqrt(sum(x*x for x in v))
    if length<1e-12:raise ValueError('Degenerate camera basis')
    return [x/length for x in v]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]


def visibility(d):
    boxes,pending=supported_objects(d);objects={o['id']:o for o in d.get('objects',[])};rows=[]
    for c in d.get('cameras',[]):
        if c.get('projection')!='perspective' or c.get('sensor_fit')!='horizontal':
            rows.append({'camera_id':c['id'],'status':'PENDING','reason':'Probe check supports horizontal-fit perspective only'});continue
        origin=c['position_m'];f=normalize([c['target_m'][i]-origin[i] for i in range(3)]);right=normalize(cross(f,c['up']));up=cross(right,f)
        halfx=c['sensor_width_mm']/(2*c['lens_mm']);halfy=halfx*c['aspect'][1]/c['aspect'][0]
        for oid in c.get('probe_object_ids',c.get('visible_object_ids',[])):
            obj=objects.get(oid)
            try:pts=samples(obj)
            except (TypeError,ValueError,KeyError):rows.append({'camera_id':c['id'],'object_id':oid,'status':'PENDING_UNSUPPORTED_TARGET'});continue
            inside=clear=0;blockers=set()
            for pt in pts:
                v=[pt[i]-origin[i] for i in range(3)];z=sum(a*b for a,b in zip(v,f));x=sum(a*b for a,b in zip(v,right));y=sum(a*b for a,b in zip(v,up))
                if z<=c.get('near_clip_m',.01) or abs(x)>z*halfx or abs(y)>z*halfy:continue
                inside+=1;blocked=False
                for obstacle in boxes:
                    if obstacle['id']==oid or obstacle.get('opaque',True) is False:continue
                    t=segment_box(origin,pt,obstacle)
                    if t is not None and t<1-1e-8:blocked=True;blockers.add(obstacle['id'])
                if not blocked:clear+=1
            rows.append({'camera_id':c['id'],'object_id':oid,'status':'PROBE_DIAGNOSTIC_ONLY','in_frame_probes':inside,'clear_probes':clear,'total_probes':len(pts),'blocker_ids':sorted(blockers),'note':'Zero clear probes does not prove invisible; faces can remain visible between samples. Clear probes do not prove final image match.'})
    return {'visibility_probes':rows,'unmodeled_obstacles':pending,'limitations':'Nine target probes and straight rays against opaque boxes only; not complete frustum clipping, mesh occlusion or pixel coverage. Never auto-edit visibility locks from this result.'}


def interactions(d):
    props={p['id']:p for p in d.get('props',[])};objects={o['id']:o for o in d.get('objects',[])};rows=[]
    for r in d.get('prop_interactions',[]):
        errors=[];pending=[];p=props.get(r.get('prop_id'))
        if p is None:errors.append('Unknown prop ID')
        else:
            if r.get('prop_version')!=p.get('version'):errors.append('Stale prop version')
            states=p.get('allowed_states',[])
            if not states:pending.append('Allowed prop states not established')
            elif r.get('state') not in states:errors.append('Unknown prop state')
            grips={g['id']:g for g in p.get('grip_points',[])}
            if r.get('grip_id') not in grips:errors.append('Unknown grip/contact ID')
        if not r.get('actor_id') or not r.get('actor_profile_evidence'):pending.append('Actor identity/scale/profile evidence missing')
        if r.get('support_object_id') and r['support_object_id'] not in objects:errors.append('Unknown support surface')
        if r.get('hand') not in ['left','right','both','none']:errors.append('Explicit hand ownership required')
        for key in ['scale_evidence','contact_evidence']:
            if not r.get(key):pending.append(key+' missing')
        rows.append({'interaction_id':r.get('id'),'status':'FAIL' if errors else 'PENDING' if pending else 'RECORD_COMPLETE_PHYSICAL_CHECK_PENDING','errors':errors,'pending':pending})
    return {'interactions':rows,'limitations':'Metadata consistency only. Hand reach, articulation, weight, grip fit, moving-part collision and rendered contact must be inspected separately.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('command',choices=['routes','visibility','interactions']);ap.add_argument('manifest',type=Path);a=ap.parse_args();d=json.loads(a.manifest.read_text())
    print(json.dumps({'routes':check_routes,'visibility':visibility,'interactions':interactions}[a.command](d),indent=2))
if __name__=='__main__':main()
