import copy
import math
import unittest

from inspect_colmap_pose import inspect_pose


class ColmapPoseTests(unittest.TestCase):
    def record(self, q=None, t=None):
        return {"format": "colmap-images-txt-world-to-camera",
                "qvec_wxyz": q if q is not None else [1, 0, 0, 0],
                "tvec": t if t is not None else [1, 2, 3]}

    def assert_vector(self, a, b):
        for x, y in zip(a, b): self.assertAlmostEqual(x, y, places=10)

    def test_translation_is_not_camera_centre(self):
        record = self.record()
        report = inspect_pose(record)
        self.assertEqual(report['camera_center_source_world'], [-1, -2, -3])
        # The source projection must map camera centre to zero, not to 2*t.
        self.assert_vector([a+b for a,b in zip(report['camera_center_source_world'], record['tvec'])], [0,0,0])
        self.assertNotEqual(record['tvec'], report['camera_center_source_world'])

    def test_rotated_pose_round_trip_and_axes(self):
        report = inspect_pose(self.record([math.sqrt(0.5), 0, math.sqrt(0.5), 0]))
        self.assert_vector(report['camera_center_source_world'], [3, -2, -1])
        self.assert_vector(report['forward_source_world'], [-1, 0, 0])
        self.assert_vector(report['up_source_world'], [0, -1, 0])
        r = report['rotation_world_to_camera']
        for offset in ([0,0,0], [1,2,3], [-2,3,1]):
            p = [a+b for a,b in zip(report['camera_center_source_world'], offset)]
            cam = [sum(row[j]*p[j] for j in range(3))+t for row,t in zip(r,[1,2,3])]
            expected = [sum(row[j]*offset[j] for j in range(3)) for row in r]
            self.assert_vector(cam, expected)

    def test_identity_boundary_and_no_mutation(self):
        record = self.record(t=[0,0,0]); original = copy.deepcopy(record)
        report = inspect_pose(record)
        self.assertEqual(record, original)
        self.assert_vector(report['camera_center_source_world'], [0,0,0])
        self.assertEqual(report['alignment_status'], 'PENDING_PROJECT_ALIGNMENT')
        self.assertNotIn('position_m', report)

    def test_quaternion_sign_equivalence(self):
        q = [math.sqrt(0.5), 0, 0, math.sqrt(0.5)]
        a = inspect_pose(self.record(q)); b = inspect_pose(self.record([-v for v in q]))
        self.assert_vector(a['camera_center_source_world'], b['camera_center_source_world'])

    def test_reject_unknown_pose_direction_or_format(self):
        for value in ('camera-to-world', 'colmap-rig-body', None):
            record = self.record(); record['format'] = value
            with self.assertRaises(ValueError): inspect_pose(record)

    def test_reject_invalid_quaternion_or_translation(self):
        for q in ([0,0,0,0], [2,0,0,0], [True,0,0,0], [float('nan'),0,0,0], [1,0,0]):
            with self.assertRaises(ValueError): inspect_pose(self.record(q))
        with self.assertRaises(ValueError): inspect_pose(self.record(t=[0,float('inf'),0]))


if __name__ == '__main__': unittest.main()
