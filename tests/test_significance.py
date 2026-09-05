"""Pure-math tests for grade/significance.py — no API key needed, no model calls."""

import pytest

from toolfit.grade.significance import bonferroni_correct, paired_exact_pvalue, wilson_interval


def test_wilson_interval_is_centered_near_the_observed_rate_for_large_n():
    lo, hi = wilson_interval(50, 100)
    assert lo < 0.5 < hi
    assert hi - lo < 0.25  # tight interval at n=100 (correct Wilson width here is ~0.192)


def test_wilson_interval_is_wide_for_small_n():
    lo, hi = wilson_interval(1, 2)
    assert hi - lo > 0.5  # very little data, very wide interval


def test_wilson_interval_handles_zero_successes_without_going_negative():
    lo, hi = wilson_interval(0, 10)
    assert lo == 0.0
    assert hi > 0.0


def test_wilson_interval_handles_all_successes_without_exceeding_one():
    lo, hi = wilson_interval(10, 10)
    assert hi == 1.0
    assert lo < 1.0


def test_wilson_interval_rejects_zero_trials():
    with pytest.raises(ValueError, match="zero trials"):
        wilson_interval(0, 0)


def test_wilson_interval_rejects_successes_greater_than_n():
    with pytest.raises(ValueError, match="between 0 and n"):
        wilson_interval(5, 3)


def test_wilson_interval_rejects_an_unsupported_confidence_level():
    with pytest.raises(ValueError, match="unsupported confidence level"):
        wilson_interval(5, 10, confidence=0.5)


def test_paired_exact_pvalue_for_a_universal_improvement_is_one_over_two_to_the_n():
    # 5 fail->pass, 0 pass->fail: P(X >= 5 | k=5) = 1/32. Never exactly zero at small n.
    before = [False, False, False, False, False]
    after = [True, True, True, True, True]
    assert paired_exact_pvalue(before, after) == pytest.approx(1 / 32)


def test_paired_exact_pvalue_is_one_for_no_change_at_all():
    before = [True, False, True, False]
    after = [True, False, True, False]
    assert paired_exact_pvalue(before, after) == 1.0


def test_paired_exact_pvalue_is_one_when_things_got_worse():
    before = [True, True, True]
    after = [False, False, False]
    assert paired_exact_pvalue(before, after) == 1.0


def test_paired_exact_pvalue_ignores_ties_and_does_not_reach_significance_on_three_discordant_pairs():
    # 3 fail->pass + 2 ties. A paired bootstrap over this reported ~0.010 (resampling the ties
    # fabricates power); the exact test says 1/8 — correctly not significant at alpha=0.05.
    before = [False, False, False, True, False]
    after = [True, True, True, True, False]
    assert paired_exact_pvalue(before, after) == pytest.approx(0.125)


def test_paired_exact_pvalue_with_mixed_discordant_pairs():
    # 3 improvements, 1 regression: P(X >= 3 | k=4) = (4 + 1) / 16.
    before = [False, False, False, True]
    after = [True, True, True, False]
    assert paired_exact_pvalue(before, after) == pytest.approx(5 / 16)


def test_paired_exact_pvalue_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="paired"):
        paired_exact_pvalue([True, False], [True])


def test_paired_exact_pvalue_rejects_empty_input():
    with pytest.raises(ValueError, match="zero trials"):
        paired_exact_pvalue([], [])


def test_bonferroni_correct_divides_alpha_by_test_count():
    # alpha=0.05, 2 tests -> corrected threshold 0.025: 0.02 clears it, 0.03 doesn't.
    result = bonferroni_correct([0.02, 0.03])
    assert result == [True, False]


def test_bonferroni_correct_with_one_test_uses_alpha_unchanged():
    result = bonferroni_correct([0.04])
    assert result == [True]


def test_bonferroni_correct_handles_empty_input():
    assert bonferroni_correct([]) == []
