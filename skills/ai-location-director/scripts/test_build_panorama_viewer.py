import base64
import io
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from build_panorama_viewer import build_viewer


class PanoramaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.png"
        Image.new("RGB", (128, 64), (21, 72, 144)).save(self.source)
        self.output = self.root / "viewer.html"

    def test_embedded_lossless_texture(self):
        report = build_viewer(self.source, self.output)
        self.assertEqual(report["dimensions"], [128, 64])
        document = self.output.read_text()
        encoded = document.split("data:image/png;base64,", 1)[1].split("'", 1)[0]
        with Image.open(io.BytesIO(base64.b64decode(encoded))) as texture:
            self.assertEqual(texture.getpixel((0, 0)), (21, 72, 144))
        self.assertNotIn('<script src=', document)
        self.assertNotIn('fetch(', document)

    def test_bad_ratio_rejected_without_output(self):
        Image.new("RGB", (128, 65)).save(self.source)
        with self.assertRaisesRegex(ValueError, "2:1"):
            build_viewer(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_existing_output_preserved(self):
        self.output.write_text("original")
        with self.assertRaises(FileExistsError):
            build_viewer(self.source, self.output)
        self.assertEqual(self.output.read_text(), "original")

    def test_source_never_overwritten(self):
        original = self.source.read_bytes()
        with self.assertRaises(FileExistsError):
            build_viewer(self.source, self.source)
        self.assertEqual(self.source.read_bytes(), original)

    def test_unreadable_source_no_output(self):
        self.source.write_bytes(b"not an image")
        with self.assertRaises(OSError):
            build_viewer(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_title_escaped(self):
        build_viewer(self.source, self.output, '<script>alert("x")</script>')
        document = self.output.read_text()
        self.assertIn('&lt;script&gt;', document)
        self.assertNotIn('<script>alert', document)


if __name__ == "__main__":
    unittest.main()
