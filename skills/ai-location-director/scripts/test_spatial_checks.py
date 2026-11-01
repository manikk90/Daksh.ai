import unittest
from spatial_checks import segment_box, check_routes, visibility, interactions

def box(i='wall',pos=(0,0,1),dims=(2,1,2),rot=0):
    return dict(id=i,geometry_kind='box',pivot='centre',position_m=list(pos),dimensions_m=list(dims),rotation_deg=[0,0,rot])
class SpatialTests(unittest.TestCase):
    def test_segment_and_rotation(self):
        self.assertIsNotNone(segment_box([-4,0,1],[4,0,1],box()))
        self.assertIsNone(segment_box([-4,3,1],[4,3,1],box()))
        self.assertIsNotNone(segment_box([0,-4,1],[0,4,1],box(rot=90)))
    def test_sweep_does_not_tunnel(self):
        d={'objects':[box(dims=(.01,1,2))],'routes':[{'id':'r','actor_radius_m':.2,'actor_height_m':1.6,'points_m':[[-10,0,0],[10,0,0]]}]}
        self.assertTrue(check_routes(d)['routes'][0]['contacts'])
    def test_clearance_vs_point(self):
        o=box(pos=(0,0,1),dims=(1,1,2))
        self.assertIsNone(segment_box([-2,.7,0],[2,.7,0],o))
        self.assertIsNotNone(segment_box([-2,.7,0],[2,.7,0],o,.3,1.7))
    def test_unknown_and_support_pending(self):
        r={'id':'r','actor_radius_m':.2,'actor_height_m':1,'points_m':[[-1,0,0],[1,0,0]],'support_object_ids':['floor']}
        d={'objects':[box('floor',pos=(0,0,-.1),dims=(10,10,.2)),{'id':'tree','geometry_kind':'mesh'}],'routes':[r]}
        result=check_routes(d);self.assertEqual(result['routes'][0]['status'],'PENDING_UNMODELED_OBSTACLES');self.assertFalse(result['routes'][0]['contacts'])
    def test_visibility_and_occlusion(self):
        c=dict(id='c',projection='perspective',sensor_fit='horizontal',position_m=[0,-8,1],target_m=[0,0,1],up=[0,0,1],sensor_width_mm=36,lens_mm=35,aspect=[16,9],probe_object_ids=['target'])
        d={'cameras':[c],'objects':[box('target',dims=(1,1,1))]}
        self.assertGreater(visibility(d)['visibility_probes'][0]['clear_probes'],0)
        d['objects'].append(box('occluder',pos=(0,-4,1),dims=(10,1,10)))
        r=visibility(d)['visibility_probes'][0];self.assertEqual(r['clear_probes'],0);self.assertIn('occluder',r['blocker_ids'])
        c['target_m']=[0,-10,1];self.assertEqual(visibility(d)['visibility_probes'][0]['in_frame_probes'],0)
    def test_transparent_occluder(self):
        c=dict(id='c',projection='perspective',sensor_fit='horizontal',position_m=[0,-8,1],target_m=[0,0,1],up=[0,0,1],sensor_width_mm=36,lens_mm=35,aspect=[16,9],probe_object_ids=['target'])
        o=box('glass',pos=(0,-4,1),dims=(10,1,10));o['opaque']=False
        self.assertGreater(visibility({'cameras':[c],'objects':[box('target'),o]})['visibility_probes'][0]['clear_probes'],0)
    def test_prop_state_and_version(self):
        d={'props':[{'id':'bag','version':'2','allowed_states':['closed'],'grip_points':[{'id':'strap'}]}],'prop_interactions':[{'id':'carry','prop_id':'bag','prop_version':'1','state':'open','grip_id':'unknown','hand':'right'}]}
        r=interactions(d)['interactions'][0];self.assertEqual(r['status'],'FAIL');self.assertEqual(len(r['errors']),3)
        d['prop_interactions'][0].update(prop_version='2',state='closed',grip_id='strap',actor_id='naina',actor_profile_evidence='profile-v1',scale_evidence='approved ref',contact_evidence='inspected ref')
        self.assertEqual(interactions(d)['interactions'][0]['status'],'RECORD_COMPLETE_PHYSICAL_CHECK_PENDING')
if __name__=='__main__':unittest.main()
