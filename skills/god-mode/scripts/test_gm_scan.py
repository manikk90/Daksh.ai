import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gm_scan  # noqa: E402


def make_repo(tmp: Path) -> Path:
    (tmp / "skills/ai-music-director/references").mkdir(parents=True)
    (tmp / "skills/ai-music-director/SKILL.md").write_text(
        "---\nname: ai-music-director\ndescription: Songs, lyrics, score and music prompts.\n---\n# Music\n## Scoring\n")
    (tmp / "skills/ai-music-director/references/scene-scoring.md").write_text("# Scene scoring\nTempo and motif.\n")
    (tmp / "skills/ai-dubbing").mkdir(parents=True)
    (tmp / "skills/ai-dubbing/SKILL.md").write_text(
        "---\nname: ai-dubbing\ndescription: Regional voice dubbing and cue QC.\n---\n# Dubbing\n")
    (tmp / "skills/daksh/assets").mkdir(parents=True)
    (tmp / "skills/daksh/SKILL.md").write_text("---\nname: daksh\ndescription: Master agent brain.\n---\n")
    (tmp / "skills/daksh/assets/agent-registry.json").write_text(json.dumps({"roles": [
        {"id": "music", "label": "AI Music Director", "skill_name": "ai-music-director",
         "tasks": ["songs", "lyrics"], "handoff": "beat timing"}]}))
    (tmp / "agents").mkdir()
    (tmp / "agents/AI_SOCIALS.md").write_text("# AI Socials | Captions\nInstagram caption workflow.\n")
    return tmp


class ScanTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = make_repo(Path(self._tmp.name))
        self.docs = gm_scan.collect(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def test_collects_all_kinds(self):
        inv = gm_scan.inventory(self.docs)
        self.assertEqual(sorted(inv["skill"]), ["ai-dubbing", "ai-music-director", "daksh"])
        self.assertEqual(inv["agent"], ["AI_SOCIALS"])
        self.assertEqual(inv["role"], ["music"])

    def test_music_goal_ranks_music_first(self):
        top = gm_scan.rank(self.docs, "devotional song with lyrics", 3)
        self.assertTrue(top)
        self.assertIn("music", top[0]["id"])

    def test_hinglish_synonym_bridge(self):
        top = gm_scan.rank(self.docs, "awaaz badalni hai", 2)
        self.assertEqual(top[0]["id"], "ai-dubbing")

    def test_caption_hits_agent_doc(self):
        top = gm_scan.rank(self.docs, "instagram post", 1)
        self.assertEqual(top[0]["id"], "AI_SOCIALS")

    def test_unrelated_goal_returns_empty(self):
        self.assertEqual(gm_scan.rank(self.docs, "kubernetes quantum zebra", 5), [])

    def test_cli_json(self):
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = gm_scan.main(["score for a scene", "--root", str(self.root), "--json", "--top", "2"])
        self.assertEqual(code, 0)
        self.assertEqual(len(json.loads(buf.getvalue())), 2)


if __name__ == "__main__":
    unittest.main()
