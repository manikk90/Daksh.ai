import copy
import unittest

from transfer_intrinsics import transfer


def project(k, p):
    q = [sum(k[i][j] * p[j] for j in range(3)) for i in range(3)]
    return [q[0] / q[2], q[1] / q[2]]


class IntrinsicsTests(unittest.TestCase):
    def record(self, a):
        return {"camera_model": "pinhole", "source_pixels": [1920, 1080],
                "output_pixels": [960, 540], "K": [[1000, 0, 960], [0, 1000, 540], [0, 0, 1]],
                "pixel_transform": a, "pixel_convention": "Explicit source-to-output coordinate mapping"}

    def check_projection(self, record):
        before = copy.deepcopy(record)
        result = transfer(record)
        for p in ([0, 0, 1], [1, 0.5, 5], [-2, -1, 8]):
            u, v = project(record['K'], p)
            expected = project(record['pixel_transform'], [u, v, 1])
            actual = project(result['K'], p)
            for x, y in zip(expected, actual):
                self.assertAlmostEqual(x, y, places=10)
        self.assertEqual(record, before)
        return result

    def test_resize_stale_intrinsics_fail_updated_pass(self):
        r = self.record([[0.5, 0, 0], [0, 0.5, 0], [0, 0, 1]])
        p = [1, 0.5, 5]
        stale = project(r['K'], p)
        expected = [x * 0.5 for x in stale]
        self.assertGreater(sum((a-b)**2 for a,b in zip(stale, expected)), 0)
        self.assertEqual(self.check_projection(r)['K'], [[500, 0, 480], [0, 500, 270], [0, 0, 1]])

    def test_crop_then_resize_principal_point(self):
        # Crop left=200, top=100; scale by 0.5. The approved scene never moves.
        r = self.record([[0.5, 0, -100], [0, 0.5, -50], [0, 0, 1]])
        self.assertEqual(self.check_projection(r)['K'], [[500, 0, 380], [0, 500, 220], [0, 0, 1]])

    def test_letterbox_and_nonuniform_resize(self):
        self.check_projection(self.record([[0.5, 0, 20], [0, 0.75, 40], [0, 0, 1]]))

    def test_half_pixel_offset_is_explicit(self):
        self.check_projection(self.record([[0.5, 0, -0.25], [0, 0.5, -0.25], [0, 0, 1]]))

    def test_identity_boundary(self):
        r = self.record([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        r['output_pixels'] = r['source_pixels'][:]
        self.assertEqual(self.check_projection(r)['K'], r['K'])

    def test_reject_unsupported_projection_or_unknown_convention(self):
        for field, value in [('camera_model', 'equirectangular'), ('camera_model', 'fisheye'),
                             ('pixel_convention', ''), ('source_pixels', [True, 1080])]:
            r = self.record([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
            r[field] = value
            with self.assertRaises(ValueError): transfer(r)

    def test_reject_nonfinite_rotation_perspective_or_flip(self):
        for a in ([[float('nan'),0,0],[0,1,0],[0,0,1]],
                  [[0,-1,0],[1,0,0],[0,0,1]], [[1,0,0],[0,1,0],[0.1,0,1]],
                  [[-1,0,0],[0,1,0],[0,0,1]], [[True,0,0],[0,1,0],[0,0,1]]):
            with self.assertRaises(ValueError): transfer(self.record(a))


if __name__ == '__main__': unittest.main()
