"""Pure statistical functions for M2's confidence intervals and mutation-testing acceptance rule
(design doc M2 Design §1). No model calls, no I/O — every function here takes and returns plain
Python values, so it's fully covered by offline TDD.
"""

from __future__ import annotations

import math
import random

# z-scores for the two-sided confidence levels this project uses. A closed-form inverse-normal-CDF
# approximation would be overkill for three fixed lookups.
_Z_SCORES = {0.90: 1.6448536269514722, 0.95: 1.9599639845400545, 0.99: 2.5758293035489004}


def wilson_interval(successes: int, n: int, *, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion — closed-form, well-behaved at small n and
    at the boundaries (0 or all successes), unlike the naive normal-approximation interval.
    Returns (lo, hi) as fractions in [0, 1]."""
    if n == 0:
        raise ValueError("cannot compute a confidence interval with zero trials")
    if not (0 <= successes <= n):
        raise ValueError(f"successes ({successes}) must be between 0 and n ({n})")
    if confidence not in _Z_SCORES:
        raise ValueError(f"unsupported confidence level {confidence!r}; supported: {sorted(_Z_SCORES)}")

    z = _Z_SCORES[confidence]
    p_hat = successes / n
    denom = 1 + z * z / n
    center = (p_hat + z * z / (2 * n)) / denom
    margin = (z * math.sqrt(p_hat * (1 - p_hat) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def paired_bootstrap_pvalue(
    before: list[bool], after: list[bool], *, resamples: int = 10000, seed: int = 0
) -> float:
    """One-sided paired bootstrap test for improvement: resamples the paired (before, after)
    outcomes with replacement `resamples` times, and returns the fraction of resamples whose
    delta (sum(after) - sum(before)) is <= 0. A small p-value means most of the bootstrap
    distribution shows a real improvement — strong evidence 'after' is better than 'before'.
    Requires paired, non-empty input.
    """
    if len(before) != len(after):
        raise ValueError(f"before and after must be paired (same length): {len(before)} vs {len(after)}")
    if len(before) == 0:
        raise ValueError("cannot run a significance test with zero trials")

    n = len(before)
    rng = random.Random(seed)
    non_positive_deltas = 0
    for _ in range(resamples):
        delta = 0
        for _ in range(n):
            i = rng.randrange(n)
            delta += int(after[i]) - int(before[i])
        if delta <= 0:
            non_positive_deltas += 1
    return non_positive_deltas / resamples


def bonferroni_correct(p_values: list[float], *, alpha: float = 0.05) -> list[bool]:
    """Bonferroni correction for testing multiple mutations in one run: a p-value is significant
    only if it clears alpha divided by the number of tests. Returns one bool per input p-value,
    same order — True means 'still significant after correction'."""
    if not p_values:
        return []
    corrected_alpha = alpha / len(p_values)
    return [p < corrected_alpha for p in p_values]
