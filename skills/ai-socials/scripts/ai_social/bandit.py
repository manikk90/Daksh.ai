"""Thompson-sampling allocator for the learnable dimensions.

A "win" is a mature post whose normalised score beats its baseline (> 1.0).
Each (platform, dimension, value) arm keeps a Beta(1 + wins, 1 + losses)
posterior, recomputed from logs every time, so there is no hidden state to
drift. Arms with fewer than ``MIN_TRIALS`` posts are tried first, so new
ideas always get a fair shot before the agent settles.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Sequence

from ai_social.metrics import ScoredPost

MIN_TRIALS = 2


@dataclass(frozen=True)
class ArmStats:
    """Win/loss counts and posterior mean for one arm."""

    value: str
    wins: int
    losses: int

    @property
    def trials(self) -> int:
        return self.wins + self.losses

    @property
    def posterior_mean(self) -> float:
        return (1 + self.wins) / (2 + self.trials)


def arm_stats(scored: Sequence[ScoredPost], platform: str, dimension: str, candidates: Sequence[str]) -> list[ArmStats]:
    """Count wins and losses per candidate value from scored posts."""
    wins = {c: 0 for c in candidates}
    losses = {c: 0 for c in candidates}
    for sp in scored:
        if sp.normalized is None or sp.post.platform != platform:
            continue
        value = sp.post.dimension(dimension)
        if value not in wins:
            continue
        if sp.normalized > 1.0:
            wins[value] += 1
        else:
            losses[value] += 1
    return [ArmStats(c, wins[c], losses[c]) for c in candidates]


def suggest(
    scored: Sequence[ScoredPost],
    platform: str,
    dimension: str,
    candidates: Sequence[str],
    seed: int | None = None,
) -> dict[str, object]:
    """Pick the next value to use for ``dimension`` on ``platform``.

    Args:
        scored: Output of ``metrics.score_posts``.
        platform: Which platform the next post is for.
        dimension: One of ``models.LEARNABLE_DIMENSIONS``.
        candidates: Allowed values, e.g. slot labels from the playbook.
        seed: Fix for reproducible suggestions in tests.

    Returns:
        ``{"choice", "reason", "arms"}`` where ``arms`` lists each candidate's
        wins, losses and posterior mean.

    Raises:
        ValueError: If ``candidates`` is empty.
    """
    if not candidates:
        raise ValueError("no candidates to choose from")
    rng = random.Random(seed)
    stats = arm_stats(scored, platform, dimension, candidates)
    under = [s for s in stats if s.trials < MIN_TRIALS]
    if under:
        pick = min(under, key=lambda s: (s.trials, candidates.index(s.value)))
        reason = f"exploring: only {pick.trials} scored post(s) so far"
    else:
        draws = {s.value: rng.betavariate(1 + s.wins, 1 + s.losses) for s in stats}
        best = max(draws, key=lambda v: draws[v])
        pick = next(s for s in stats if s.value == best)
        reason = f"thompson draw {draws[best]:.2f} (posterior mean {pick.posterior_mean:.2f})"
    return {
        "choice": pick.value,
        "reason": reason,
        "arms": [
            {"value": s.value, "wins": s.wins, "losses": s.losses, "posterior_mean": round(s.posterior_mean, 3)}
            for s in stats
        ],
    }
