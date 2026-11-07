"""Behavior checks for catalog provenance, source availability, and privacy."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "catalog" / "build_catalog.py"
SPEC = importlib.util.spec_from_file_location("daksh_catalog", SCRIPT)
catalog_builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog_builder)


class CatalogBoundaryTests(unittest.TestCase):
    def manifest(self):
        return {
            "local_agent_skills": "",
            "system_skills": "",
            "plugin_packages": {"example/connector/1.0": "example-skill"},
            "policy_disabled_packages": [],
        }

    def build_temporary_repository(self, root):
        output = root / "catalog"
        output.mkdir()
        (output / "session-skill-manifest.json").write_text(json.dumps(self.manifest()))
        with patch.object(catalog_builder, "REPO", root), patch.object(catalog_builder, "CATALOG", output):
            with patch("sys.argv", ["build_catalog.py", "--snapshot-date", "2026-11-07"]), redirect_stdout(io.StringIO()):
                catalog_builder.main()
        return json.loads((output / "skills.json").read_text())

    def test_symlink_aliases_share_one_canonical_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "skills" / "original" / "SKILL.md"
            source.parent.mkdir(parents=True)
            source.write_text("---\nname: source\ndescription: Source metadata.\n---\nSkill body.\n")
            alias = root / "skills" / "alias" / "SKILL.md"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(source)
            result = self.build_temporary_repository(root)
            self.assertEqual(result["counts"]["canonical_readable_skills"], 1)
            self.assertEqual(result["counts"]["source_file_aliases"], 2)
            self.assertEqual(set(result["skills"][0]["source_aliases"]), {
                "repository/skills/original/SKILL.md", "repository/skills/alias/SKILL.md",
            })

    def test_machine_paths_are_redacted_from_exported_metadata(self):
        text = "Images /Users/alice/project/cast.png; report /home/bob/work/report.md"
        cleaned = catalog_builder.clean(text)
        self.assertNotIn("alice", cleaned)
        self.assertNotIn("bob", cleaned)
        self.assertIn("<home>/project/cast.png", cleaned)
        self.assertIn("<home>/work/report.md", cleaned)

    def test_session_exposure_requires_exact_version_and_primary_source(self):
        manifest = self.manifest()
        primary = "plugin-cache/example/connector/1.0/skills/example-skill/SKILL.md"
        self.assertTrue(catalog_builder.session_match(primary, "example-skill", manifest)[0])
        for locator in (
            primary.replace("/1.0/", "/0.9/"),
            primary.replace("/skills/", "/skills/v1/"),
            primary.replace("/skills/", "/skills-figquery/"),
        ):
            with self.subTest(locator=locator):
                self.assertFalse(catalog_builder.session_match(locator, "example-skill", manifest)[0])

    def test_inventory_excludes_bodies_and_keeps_work_ops_ownership(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "skills" / "maniik" / "SKILL.md"
            source.parent.mkdir(parents=True)
            secret_body = "PRIVATE_BODY_SENTINEL_DO_NOT_EXPORT"
            source.write_text("---\nname: maniik\ndescription: Work planning and coordination.\n---\n" + secret_body)
            result = self.build_temporary_repository(root)
            record = result["skills"][0]
            self.assertNotIn(secret_body, json.dumps(result))
            self.assertEqual(record["owner_agent_id"], "operations")
            self.assertEqual(record["availability"]["activation"], "repository_source_requires_adapter")
            self.assertFalse(record["availability"]["session_listed"])
            self.assertFalse(record["availability"]["runtime_verified"])
            self.assertFalse(record["availability"]["credentials_verified"])


if __name__ == "__main__":
    unittest.main()
