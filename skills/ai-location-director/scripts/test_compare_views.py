import tempfile
import unittest
from pathlib import Path

from PIL import Image

from compare_views import compare_views


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def image(self, name, color, size=(101, 101)):
        path = self.root / name
        Image.new("RGB", size, color).save(path)
        return path

    def test_identical_images_and_artifacts(self):
        a = self.image("a.png", (12, 34, 56))
        b = self.image("b.png", (12, 34, 56))
        report = compare_views(a, b, self.root / "output")
        self.assertEqual(report["mean_absolute_pixel_difference"], 0)
        self.assertEqual(report["dimensions"], {"width": 101, "height": 101})
        for path in report["outputs"].values():
            self.assertTrue(Path(path).is_file())
        with Image.open(report["outputs"]["absolute_difference"]) as diff:
            self.assertEqual(diff.getextrema(), ((0, 0), (0, 0), (0, 0)))

    def test_known_channel_difference(self):
        a = self.image("a.png", (0, 0, 0))
        b = self.image("b.png", (30, 60, 90))
        report = compare_views(a, b, self.root / "output")
        self.assertEqual(report["mean_absolute_pixel_difference"], 60)

    def test_dimension_mismatch_rejected_without_outputs(self):
        a = self.image("a.png", "black")
        b = self.image("b.png", "black", (100, 101))
        with self.assertRaisesRegex(ValueError, "Dimensions differ"):
            compare_views(a, b, self.root / "output")
        self.assertFalse((self.root / "output").exists())

    def test_landmark_displacement_pixels(self):
        a = self.image("a.png", "black")
        b = self.image("b.png", "black")
        points = {"reference": {"gate": [0.2, 0.4]}, "candidate": {"gate": [0.23, 0.44]}}
        report = compare_views(a, b, self.root / "output", points)
        error = report["landmark_errors"]["gate"]
        self.assertAlmostEqual(error["dx_pixels"], 3)
        self.assertAlmostEqual(error["dy_pixels"], 4)
        self.assertAlmostEqual(error["distance_pixels"], 5)

    def test_invalid_landmarks_rejected(self):
        a = self.image("a.png", "black")
        cases = [
            {"reference": {"gate": [0, 0]}, "candidate": {}},
            {"reference": {"gate": [float("nan"), 0]}, "candidate": {"gate": [0, 0]}},
            {"reference": {"gate": [1.1, 0]}, "candidate": {"gate": [0, 0]}},
        ]
        for points in cases:
            with self.subTest(points=points), self.assertRaises(ValueError):
                compare_views(a, a, self.root / "output", points)

    def test_input_overwrite_rejected(self):
        a = self.image("overlay.png", "black")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            compare_views(a, a, self.root)


if __name__ == "__main__":
    unittest.main()
