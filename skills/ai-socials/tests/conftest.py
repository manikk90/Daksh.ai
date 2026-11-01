"""Shared fixtures: an isolated copy of the repo's brain/ and schemas/ per test."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from ai_social.storage import Paths

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture()
def repo(tmp_path: Path) -> Paths:
    """A throwaway AI Social home with the real brain and schemas."""
    shutil.copytree(ROOT / "brain", tmp_path / "brain")
    shutil.copytree(ROOT / "schemas", tmp_path / "schemas")
    for d in ("logs", "data", "retro"):
        (tmp_path / d).mkdir()
    return Paths(tmp_path)


@pytest.fixture()
def fixtures() -> Path:
    return FIXTURES
