import copy
import json
import tempfile
import unittest
from pathlib import Path
from location_runtime import audit, impact, invalidate, telemetry, blockout
from validate_location import validate

class RuntimeTests(unittest.TestCase):
    def test_transitive_invalidation_preserves_unaffected(self):
        d={'stage':'delivered','cameras':[{'id':'cam','visible_object_ids':['tree']}],'outputs':[{'id':'a','camera_id':'cam','status':'approved'},{'id':'b','status':'approved','depends_on_output_ids':['a']},{'id':'c','status':'approved'}],'qc':[{'id':'q','output_id':'b','status':'PASS'}]}
        report=impact(d,'object',['tree']);self.assertEqual(report['affected_output_ids'],['a','b']);self.assertEqual(report['unmapped_output_ids'],['c'])
        r=invalidate(d,report);self.assertEqual(r['outputs'][2]['status'],'approved');self.assertEqual(r['qc'][0]['status'],'PENDING');self.assertEqual(d['stage'],'delivered')
    def test_camera_without_visibility_is_unknown(self):
        d={'cameras':[{'id':'unmapped'}],'outputs':[{'id':'a','camera_id':'unmapped','status':'approved'}]}
        self.assertEqual(impact(d,'object',['tree'])['unmapped_output_ids'],['a'])
    def test_reference_change_and_cycle(self):
        d={'cameras':[{'id':'c','reference_ids':['old']}],'outputs':[{'id':'a','camera_id':'c','depends_on_output_ids':['b']},{'id':'b','depends_on_output_ids':['a']}]}
        self.assertEqual(impact(d,'reference',['old'])['affected_output_ids'],['a','b'])
        self.assertTrue(any('cycle' in e for e in audit(d)['errors']))
    def test_reference_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp,'r').write_text('changed')
            r=audit({'reference_register':[{'id':'r','path':'r','version':'1','status':'approved','approval_evidence':'user accepted','sha256':'wrong'}]},Path(tmp))
            self.assertTrue(any('content changed' in e for e in r['errors']))
    def test_coverage_exclusion_and_light(self):
        d={'objects':[{'id':'floor'}],'cameras':[{'id':'c','visible_object_ids':['temple'],'state_id':'s','light_id':'night'}],'states':[{'id':'s','light_id':'day'}],'lights':[{'id':'day'}],'scene_coverage':[{'id':'shot','scene_id':'1','action':'sit','surface_ids':['floor'],'camera_ids':['c'],'output_ids':['o'],'excluded_object_ids':['temple']}],'outputs':[{'id':'o','status':'planned'}]}
        r=audit(d);self.assertTrue(any('excluded' in e for e in r['errors']));self.assertTrue(any('mismatch' in e for e in r['errors']));self.assertTrue(r['pending'])
    def test_retry_reset_after_pass(self):
        fail={'output_id':'a','result':'FAIL','failure_signature':'gate','phase':'repair','elapsed_seconds':2}
        d={'attempts':[fail,fail]};self.assertIn('a',telemetry(d)['retry_actions']);self.assertEqual(telemetry(d)['elapsed_seconds_by_phase']['repair'],4)
        d['attempts'].append({'output_id':'a','result':'PASS'});self.assertFalse(telemetry(d)['retry_actions'])
    def test_real_mesh_and_camera(self):
        d={'objects':[{'id':'box','geometry_kind':'box','pivot':'centre','dimensions_m':[2,2,2],'position_m':[0,0,1],'rotation_deg':[0,0,30]}],'cameras':[{'id':'front','projection':'perspective','position_m':[0,-8,3],'target_m':[0,0,1],'up':[0,0,1],'aspect':[16,9],'lens_mm':35,'sensor_width_mm':36,'sensor_fit':'horizontal'}]}
        with tempfile.TemporaryDirectory() as tmp:
            r=blockout(d,tmp);text=Path(r['model_path']).read_text();self.assertEqual(sum(x.startswith('v ') for x in text.splitlines()),8);self.assertEqual(sum(x.startswith('f ') for x in text.splitlines()),6)
            from PIL import Image
            with Image.open(r['camera_outputs'][0]['path']) as im:self.assertNotEqual(im.getextrema()[0],(255,255))
        d['objects'][0]['geometry_kind']='tree'
        with tempfile.TemporaryDirectory() as tmp,self.assertRaises(ValueError):blockout(d,tmp)
    def test_custom_prop_sheet_and_defaults(self):
        d=json.loads((Path(__file__).parent.parent/'assets/location-manifest.template.json').read_text())
        angles=['front','back','left','right','driver']
        d['props']=[{'id':'rick','name':'rick','version':'1','intrinsic_front':'forward','background':'neutral-grey','view_order':angles,'design_status':'proposed','sheet_status':'planned','custom_view_evidence':'user requested five views','delivery_layout':'combined-sheet','views':[{'angle':a,'output_id':'sheet','cell_id':a} for a in angles]}]
        d['outputs']=[{'id':'sheet','status':'planned','prop_id':'rick','prop_version':'1'}]
        self.assertFalse(validate(d,Path('.'))[0])
        del d['props'][0]['custom_view_evidence'];self.assertTrue(validate(d,Path('.'))[0])
        d['props'][0]['custom_view_evidence']='explicit';d['props'][0]['views'][1]['cell_id']='front';self.assertTrue(validate(d,Path('.'))[0])
if __name__=='__main__':unittest.main()
