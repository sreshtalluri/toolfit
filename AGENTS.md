# toolfit — operating manual for agents

You are installing or running `toolfit` on behalf of a user. Everything below was verified on
2026-09-05 against the published `toolfit==0.1.0` in a fresh Python 3.12 venv. Follow it in order;
each step names the exact command, what success looks like, and what a failure means.

## 0. What it is, in one breath

`toolfit` points at an MCP server, fetches its tool catalog, and tells the user where the tool
descriptions confuse models. `scan` is free and static. `eval` runs a model and costs API calls.
`--fix` proposes description rewrites and re-measures them. Nothing ever calls a tool on the user's
server — only `tools/list` — so it is safe against production servers.

## 1. Install

Needs Python **3.10+**. Check first: `python3 --version`. macOS system Python is 3.9 and pip will
only say `No matching distribution found for toolfit` — that is the Python floor, not a network
problem.

| Situation | Command |
|---|---|
| One-off, nothing installed | `uvx toolfit --help` |
| Persistent CLI | `uv tool install toolfit` or `pipx install toolfit` |
| Into an existing venv (3.10+) | `pip install toolfit` |
| Working on this repo | `uv sync --extra dev` then `uv run toolfit …` / `uv run pytest -q` |

Success: `toolfit --help` lists two commands, `scan` and `eval`.

## 2. Point it at a server

The first positional argument is the server, in one of three forms. Quote command lines.

```
toolfit scan path/to/server.py                                       # run via `uv run <path>`
toolfit scan "npx -y @modelcontextprotocol/server-github"            # any command line
toolfit scan http://127.0.0.1:8765/mcp                               # Streamable HTTP endpoint
```

- `.py` files run through `uv run`; if the script imports `mcp`, it must either be inside a uv
  project or carry PEP 723 inline metadata (`# /// script` … `dependencies = ["mcp>=2.0,<3"]`).
  Both bundled examples do. `ModuleNotFoundError: No module named 'mcp'` means it doesn't.
- The subprocess receives the caller's environment minus `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
  `OPENROUTER_API_KEY`. So `GITHUB_TOKEN=… toolfit scan "npx -y @modelcontextprotocol/server-github"`
  works; the server's own token variable is the one to set.
- Some servers refuse `tools/list` without a token (Stripe, HubSpot, Supabase, Sentry): you'll see
  `Could not connect to server … Connection closed` and the server's own message above it.

Connection errors always print `Could not connect to server at '<what you passed>': <cause>` and
exit 1. Causes you'll see: `FileNotFoundError` (binary not on PATH), `ConnectError` (URL down),
`MCPError: Connection closed` (server started then died — read its stderr just above),
`ValueError: server must not be empty`.

## 3. `scan` — free, seconds, no key

```
toolfit scan <server>            # prints findings, always exit 0
toolfit scan --strict <server>   # exit 1 if any finding
```

Rules and what they mean:

| rule_id | Fires when | Why it matters |
|---|---|---|
| `missing_description` | description empty | the model has only the name to go on |
| `short_description` | under 15 characters | "Find contacts." says nothing about *how* |
| `duplicate_description` | two+ tools share the same text (case/space-insensitive) | the classic copy-paste bug; models pick by coin flip |
| `deprecated_tool` | the description calls *itself* deprecated | models obey it and score 0; drop the tool from the catalog |

Expect few findings on mature servers (1 across 166 tools on 15 public ones — `docs/corpus.md`).
That is the tool working, not failing: the copy-paste class is rare in shipped code. The real
question needs `eval`.

Example (bundled `examples/crm_server.py`, 8 tools, four planted problems):

```
4 finding(s) across 8 tool(s).

## deprecated_tool
- get_contact describes itself as deprecated but is still in the catalog

## duplicate_description
- list_contacts, search_contacts share the identical description 'Find contacts.'

## short_description
- search_contacts's description is only 14 characters: 'Find contacts.'
- list_contacts's description is only 14 characters: 'Find contacts.'
```

## 4. `eval` — model-graded, minutes, the user's API key

### Keys

`ANTHROPIC_API_KEY` is **always** required: task generation and fix proposals use Claude regardless
of the model under test. The model under test adds one more:

| `--model` | Provider | Key |
|---|---|---|
| `claude-*` (default `claude-sonnet-5`) | Anthropic | `ANTHROPIC_API_KEY` |
| `gpt-*`, `o1*`, `o3*`, `o4*` | OpenAI | `OPENAI_API_KEY` |
| `vendor/model` (any slash) | OpenRouter | `OPENROUTER_API_KEY` |

Missing key → one line on stderr naming the variable, exit 1, before any network call.
Set keys in the environment (or a `.env` you `source`); never paste them into commands the user
can see in shell history.

### Cost and time, so you can warn the user first

Calls ≈ `tools × seeds × 3` (generate, solvability check, model under test) + `seeds` per
`--mutate` + `seeds + 1` per proposed fix. All sequential. Observed with Sonnet 5:

| Server | Tools | Seeds | Wall time |
|---|---|---|---|
| toy server | 5 | 10 | ~5 min |
| server-memory | 9 | 10 | ~8 min |
| server-filesystem | 14 | 10 | ~22 min |

Rate limits are retried with backoff (up to 5 tries, ~30 s); you'll see
`WARNING: RateLimitError, retrying in …` on stderr. Run one eval at a time — three in parallel
starved each other on an org-level 429.

### The command

```
toolfit eval <server> [--seeds N] [--model M] [--mutate 'tool:new description']...
                      [--fix | --fix-tool NAME ...] [--badge] [--strict] [--strict-threshold F]
```

| Flag | Default | Use |
|---|---|---|
| `--seeds` | 5 | tasks per tool. **Use 10+ whenever `--mutate`/`--fix` is on** — the exact test's floor p-value is 1/2ⁿ; the CLI warns below 10 |
| `--model` | `claude-sonnet-5` | model under test |
| `--mutate 'tool:text'` | — | re-run that tool's own tasks with its description replaced; repeatable. Unknown tool or empty text → exit 1 before any call |
| `--fix` | off | propose + re-measure a rewrite for **every** tool with a failed trial |
| `--fix-tool NAME` | — | same, only for the named tools; repeatable; implies `--fix`. **Prefer this** — one Bonferroni correction spans every proposal, so 12 proposals at n=10 can never reach significance |
| `--badge` | off | write `toolfit-badge.svg` in cwd |
| `--strict` | off | exit 1 if any evaluated tool's pass rate < `--strict-threshold` (default 0.9) |

Outputs land in the **current directory**: `toolfit-badge.svg`, `toolfit-fixes.json`. Run from
the directory where the user wants them. The report is stdout; warnings and progress are stderr —
`toolfit eval … > report.md` gives a clean markdown file.

### Reading the report, section by section

1. **Confusion Matrix** — rows are the tool a task was written for, columns what the model called,
   plus `(no call)` and `(hallucinated)`. Off-diagonal mass is the finding. A single column that
   collects calls from many rows is usually a *precondition* tool (`git_add` before `git_commit`,
   `list_allowed_directories` before any path op): the model is right and the single-step grader is
   strict. Say so to the user; that is not a description bug.
2. **Trial Diversity** — `7/10 distinct` means seeds collided on identical arguments; the evidence
   is thinner than n suggests.
3. **Pass Rates** — right tool *and* right arguments, per tool, with a Wilson 95% interval. At n=10
   the interval on 9/10 is [60%, 98%]; don't over-read one-trial differences.
4. **Leakage / Solvability Warnings** — generated tasks that named a tool, or that a second model
   judged ambiguous given the catalog. Reported, never silently dropped. Many solvability warnings
   on one tool usually mean the *catalog* is ambiguous (that's the finding) or the schema allows
   combinations the server doesn't (e.g. `head` and `tail` together).
5. **Schema Warnings** — tools excluded because the sampler couldn't produce arguments. They are
   **not** in any number above and don't trip `--strict`; `--strict` prints them on stderr.
6. **Mutation Results / Proposed Fixes** — per tool: before → after pass counts, exact one-sided
   McNemar p-value, and a verdict. `ACCEPTED` requires significance after correction **and** a
   higher pass count. Rejections are printed with the reason: `made things worse`, `no net change`,
   `improvement not significant after correction (p=… vs corrected α=…)`, or rejected before
   re-measurement (empty / identical / too-short rewrite).

`toolfit-fixes.json` mirrors section 6 as data: `{"tool", "before_description",
"after_description", "before_passed", "after_passed", "n", "p_value", "accepted", "reason"}` —
description text only, nothing from the server's source, no keys.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | ran; with `--strict`, every evaluated tool met the threshold |
| 1 | could not connect / missing key / bad `--mutate` or `--fix-tool` / provider error / `--strict` failed |
| 2 | usage error (unknown flag) |

## 5. Walkthrough that always works (bundled examples)

```
export ANTHROPIC_API_KEY=…
toolfit scan examples/toy_server.py                 # 2 duplicate-description findings
toolfit scan --strict examples/crm_server.py        # 4 findings, exit 1
toolfit eval examples/toy_server.py --seeds 10 --fix --badge
toolfit eval examples/crm_server.py --seeds 10 --fix-tool search_contacts --fix-tool list_contacts --badge
```

Reference outputs to compare against: `docs/examples/toy-server/`, `docs/examples/crm-server/`,
and three public servers under `docs/examples/`.

## 6. CI

```yaml
- uses: sreshtalluri/toolfit@main
  with:
    server: "npx -y @modelcontextprotocol/server-github"
    eval: true                                  # omit for scan-only (free)
    anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
    seeds: 10
    strict-threshold: 0.9
```

The Action always runs `scan --strict`; with `eval: true` it also runs `eval --strict --badge` and
uploads `toolfit-report.md` + `toolfit-badge.svg` as an artifact named `toolfit`.

## 7. Developing in this repo

```
uv sync --extra dev
uv run pytest -q                 # ~200 tests, 10 skipped without keys, <5 s
uv run toolfit scan examples/toy_server.py
uv build                         # wheel + sdist into dist/
```

Layout: `src/toolfit/{connect,lint,gen,run,grade,fix,report}` mirror the pipeline
`connect → lint → report` (scan) and `connect → gen → run → grade → [fix] → report` (eval);
`cli.py` is the only place flags are parsed. Tests are offline except `tests/*_eval.py` and
`tests/test_e2e_*.py`, which skip without keys. Design history and every methodology decision:
`docs/designs/toolfit-v0-scope.md`; open work: `TODOS.md`.

Release: bump `version` in `pyproject.toml`, commit, `git tag vX.Y.Z && git push origin vX.Y.Z`.
`.github/workflows/publish.yml` tests, builds, and publishes via PyPI trusted publishing. No token
exists anywhere and none is needed.

## 8. Things that look like bugs and aren't

- **Every rewrite rejected.** Normal on a strong model against a small catalog; the fix loop only
  accepts what it measured. Check whether the failures are argument-level (a description can't fix
  those) or precondition calls (see §4.1).
- **`count`-style tools at 0/10.** The generator tends to phrase count requests as "show me…";
  known limitation, documented in the design doc.
- **`p=1.0000` on a "worse" result.** Correct: the test is one-sided for improvement.
- **Badge is yellow/red on a server the user considers fine.** Thresholds are 90%/70% overall pass
  rate; `--strict-threshold` is per-tool and independent.
