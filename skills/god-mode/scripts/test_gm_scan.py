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

    # A pinned-module integration (mirrors integrations/ai-film.json + catalog/ai-film-skills.json).
    (tmp / "integrations").mkdir()
    (tmp / "integrations/ai-film.json").write_text(json.dumps({
        "source": {"url": "https://github.com/manikk90/AI-film.git", "path": "modules/ai-film",
                   "commit": "abc123", "integration": "pinned_git_submodule"},
        "skill_inventory": "catalog/ai-film-skills.json",
    }))
    (tmp / "catalog").mkdir()
    (tmp / "catalog/ai-film-skills.json").write_text(json.dumps({
        "skills": [
            {"id": "ai-film:anime-reel", "name": "anime-reel", "path": ".claude/skills/anime-reel/SKILL.md",
             "owner_agent_id": "native-director", "kind": "imported_format", "sha256": "x"},
            {"id": "ai-film:madhubani-kahani", "name": "madhubani-kahani",
             "path": ".claude/skills/madhubani-kahani/SKILL.md", "owner_agent_id": "native-director",
             "kind": "imported_format", "sha256": "y"},
        ],
    }))
    # Submodule checked out for anime-reel only, so one hit gets a real description and one doesn't.
    (tmp / "modules/ai-film/.claude/skills/anime-reel").mkdir(parents=True)
    (tmp / "modules/ai-film/.claude/skills/anime-reel/SKILL.md").write_text(
        '---\nname: anime-reel\ndescription: "An anime-style episode with original characters."\n---\nBody text.\n')
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
        self.assertEqual(sorted(inv["module_skill"]), ["ai-film:anime-reel", "ai-film:madhubani-kahani"])

    def test_module_skill_checked_out_gets_real_description(self):
        top = gm_scan.rank(self.docs, "anime reel with original characters", 3)
        self.assertEqual(top[0]["id"], "ai-film:anime-reel")
        self.assertEqual(top[0]["module"], "ai-film")
        self.assertTrue(top[0]["checked_out"])
        self.assertTrue(top[0]["path"].startswith("modules/ai-film/"))

    def test_module_skill_not_checked_out_still_ranks_by_name(self):
        top = gm_scan.rank(self.docs, "madhubani kahani", 3)
        self.assertEqual(top[0]["id"], "ai-film:madhubani-kahani")
        self.assertFalse(top[0]["checked_out"])

    def test_no_integrations_dir_is_fine(self):
        with tempfile.TemporaryDirectory() as t2:
            bare = make_repo(Path(t2))
            import shutil
            shutil.rmtree(bare / "integrations")
            docs = gm_scan.collect(bare)
            self.assertNotIn("module_skill", gm_scan.inventory(docs))

    def test_internal_result_has_no_module_field(self):
        top = gm_scan.rank(self.docs, "devotional song with lyrics", 1)
        self.assertNotIn("module", top[0])

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
