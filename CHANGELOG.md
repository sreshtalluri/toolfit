# Changelog

## 0.1.0 (2026-09-05)

First release.

- `toolfit scan <server>`: free static lint over `tools/list` — missing, too-short, duplicated, and self-declared-deprecated descriptions. No model calls.
- `toolfit eval <server>`: inverted task generation (sample schema-valid arguments first, then ask a generator to write the request), structural grading with canonicalisation, confusion matrix, per-tool pass rates with Wilson 95% intervals, leakage and solvability guardrails reported as warnings.
- `--mutate 'tool:new description'`: paired re-run of that tool's own tasks against a catalog with one description patched; exact one-sided McNemar p-value; one Bonferroni correction across everything re-measured in the run.
- `--fix` / `--fix-tool NAME`: propose a rewrite per failing tool (rewriter sees the real parameters and neighbour descriptions), re-measure, report accepted and rejected alike; `toolfit-fixes.json` with description text only.
- `--badge`: SVG coloured by pass rate with model, generator, seeds, and task-suite hash embedded. `--strict` / `--strict-threshold`: exit codes for CI.
- Servers as a `.py` script (`uv run`), any command line (`npx -y …`), or an `http(s)://` URL; subprocess inherits the environment.
- Adapters for Anthropic, OpenAI, and OpenRouter, inferred from `--model`; retry with backoff on 429/5xx for every model call.
- Composite GitHub Action (`action.yml`); repo CI on 3.10/3.13; PyPI publish on `v*` tags via trusted publishing.
- Evidence: toy server and three public servers evaluated end-to-end (`docs/examples/`), twenty public servers scanned (`docs/corpus.md`).
