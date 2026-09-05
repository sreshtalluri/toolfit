"""Pure statistical functions for M2's confidence intervals and mutation-testing acceptance rule
(design doc M2 Design §1). No model calls, no I/O — every function here takes and returns plain
Python values, so it's fully covered by offline TDD.
"""

from __future__ import annotations

import math

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


def paired_exact_pvalue(before: list[bool], after: list[bool]) -> float:
    """One-sided exact McNemar (sign) test for improvement on paired pass/fail outcomes.

    Only discordant pairs carry information: under the null, each fail->pass is as likely as each
    pass->fail, so the p-value is P(X >= improvements | k discordant, p=0.5). Deterministic, and
    honest at small n: 3 fail->pass with 2 ties gives 0.125, never "significant". A paired
    bootstrap over the same data resampled the ties and reported 0.010 — anti-conservative in
    exactly the low-seed runs this CLI defaults to.
    """
    if len(before) != len(after):
        raise ValueError(f"before and after must be paired (same length): {len(before)} vs {len(after)}")
    if len(before) == 0:
        raise ValueError("cannot run a significance test with zero trials")

    improvements = sum(1 for b, a in zip(before, after) if a and not b)
    regressions = sum(1 for b, a in zip(before, after) if b and not a)
    k = improvements + regressions
    if k == 0:
        return 1.0
    return sum(math.comb(k, j) for j in range(improvements, k + 1)) / 2**k


def bonferroni_correct(p_values: list[float], *, alpha: float = 0.05) -> list[bool]:
    """Bonferroni correction for testing multiple mutations in one run: a p-value is significant
    only if it clears alpha divided by the number of tests. Returns one bool per input p-value,
    same order — True means 'still significant after correction'."""
    if not p_values:
        return []
    corrected_alpha = alpha / len(p_values)
    return [p < corrected_alpha for p in p_values]
