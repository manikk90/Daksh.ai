"""Typed records shared across AI Social.

Every stage of the pipeline reads and writes these shapes, so changing a field
here means updating: schemas/*.json, metrics.py, retro.py, bandit.py, the CLI
and tests/test_models.py.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, get_args

Platform = Literal["linkedin", "instagram", "facebook", "x"]
HookType = Literal[
    "result_first",
    "constraint_number",
    "contrarian",
    "failure_reveal",
    "before_after",
    "insider_number",
    "story_open",
]
Language = Literal["en", "hinglish", "hi"]
Format = Literal["carousel", "reel", "video", "text", "image", "thread"]
EventKind = Literal["reaction", "like", "comment", "save", "share", "post"]

PLATFORMS: tuple[str, ...] = get_args(Platform)
HOOK_TYPES: tuple[str, ...] = get_args(HookType)
LANGUAGES: tuple[str, ...] = get_args(Language)
FORMATS: tuple[str, ...] = get_args(Format)

IST = timezone(timedelta(hours=5, minutes=30))

# Dimensions the weekly retro is allowed to learn about. Anything else
# (hashtag caps, link placement, confidentiality) is a hard rule and lives in
# brain/platform_rules.json, out of the self-learning loop's reach.
LEARNABLE_DIMENSIONS: tuple[str, ...] = ("slot", "hook_type", "language", "format", "pillar")


class ValidationError(ValueError):
    """Raised when a record does not satisfy its contract."""


def parse_ts(value: str) -> datetime:
    """Parse an ISO-8601 timestamp; naive values are treated as IST.

    Args:
        value: ISO string such as ``2026-10-21T08:15`` or ``2026-10-21T02:45:00Z``.

    Returns:
        A timezone-aware datetime.

    Raises:
        ValidationError: If the string is not ISO-8601.
    """
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"bad timestamp: {value!r}") from exc
    return dt if dt.tzinfo else dt.replace(tzinfo=IST)


def slot_label(dt: datetime) -> str:
    """Bucket a publish time into a learnable slot like ``tue_0800``.

    Times are converted to IST and floored to the half hour so the bandit has
    few enough arms to learn from a handful of posts per week.
    """
    local = dt.astimezone(IST)
    minute = 0 if local.minute < 30 else 30
    return f"{local.strftime('%a').lower()}_{local.hour:02d}{minute:02d}"


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ValidationError(msg)


@dataclass(frozen=True)
class PostRecord:
    """One published post, tagged with every dimension the agent learns from."""

    post_id: str
    platform: str
    published_at: str
    pillar: str
    format: str
    hook_type: str
    language: str
    experiment_id: str = "control"
    text: str = ""
    url: str = ""
    hashtags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require(bool(self.post_id.strip()), "post_id is empty")
        _require(self.platform in PLATFORMS, f"unknown platform {self.platform!r}")
        _require(self.format in FORMATS, f"unknown format {self.format!r}")
        _require(self.hook_type in HOOK_TYPES, f"unknown hook_type {self.hook_type!r}")
        _require(self.language in LANGUAGES, f"unknown language {self.language!r}")
        parse_ts(self.published_at)

    @property
    def published_dt(self) -> datetime:
        """Publish time as an aware datetime."""
        return parse_ts(self.published_at)

    @property
    def slot(self) -> str:
        """Learnable slot label derived from the publish time."""
        return slot_label(self.published_dt)

    def dimension(self, name: str) -> str:
        """Return the value of a learnable dimension for this post."""
        if name == "slot":
            return self.slot
        _require(name in LEARNABLE_DIMENSIONS, f"not a learnable dimension: {name}")
        return str(getattr(self, name))

    def to_dict(self) -> dict[str, Any]:
        """Serialise for jsonl storage."""
        data = asdict(self)
        data["hashtags"] = list(self.hashtags)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PostRecord":
        """Build from a jsonl row, ignoring unknown keys for forward compatibility."""
        known = {f for f in cls.__dataclass_fields__}
        clean = {k: v for k, v in data.items() if k in known}
        clean["hashtags"] = tuple(clean.get("hashtags") or ())
        return cls(**clean)


@dataclass(frozen=True)
class MetricSnapshot:
    """Raw platform metrics for one post at one point in time."""

    post_id: str
    platform: str
    captured_at: str
    metrics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require(bool(self.post_id.strip()), "post_id is empty")
        _require(self.platform in PLATFORMS, f"unknown platform {self.platform!r}")
        parse_ts(self.captured_at)
        for key, val in self.metrics.items():
            _require(isinstance(val, (int, float)), f"metric {key} is not numeric")
            _require(val >= 0, f"metric {key} is negative")

    def to_dict(self) -> dict[str, Any]:
        """Serialise for jsonl storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MetricSnapshot":
        """Build from a jsonl row."""
        return cls(
            post_id=data["post_id"],
            platform=data["platform"],
            captured_at=data["captured_at"],
            metrics={k: float(v) for k, v in (data.get("metrics") or {}).items()},
        )


@dataclass(frozen=True)
class EngagementEvent:
    """Something Manik did on a platform: liked, commented, saved or posted."""

    platform: str
    kind: str
    timestamp: str | None
    text: str = ""
    target_url: str = ""
    target_author: str = ""
    source_file: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialise for jsonl storage."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EngagementEvent":
        """Build from a jsonl row."""
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in known})
