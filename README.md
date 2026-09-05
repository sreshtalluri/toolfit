# toolfit

toolfit finds the specific places your MCP server confuses models, rewrites the tool
descriptions to fix them, and proves the fix with a before-and-after eval.

```
uvx toolfit scan "npx -y @modelcontextprotocol/server-github"     # free, static, seconds
uvx toolfit eval examples/toy_server.py --seeds 10 --fix --badge   # model-graded, minutes, your key
```

Every existing MCP grader stops at a number and a list of complaints. toolfit measures which
tool pairs a model actually confuses, proposes a description rewrite for each failing tool,
re-runs the same tasks against the rewrite, and reports the delta with a p-value — accepted
*and* rejected. The rejected ones are what make the accepted ones believable.

## What a run looks like

`toolfit eval examples/toy_server.py --seeds 10 --fix --badge`, model under test `claude-sonnet-5`
(full output: [`docs/examples/toy-server/`](docs/examples/toy-server/)). The toy server has two
deliberately confusable pairs: `create_task`/`update_task` share the description *"Add a new task."*,
and `list_tasks`/`count_tasks` share *"Get tasks by status."*

```
## Confusion Matrix

| Intended \ Called | count_tasks | create_reminder | create_task | list_tasks | update_task |
|---|---|---|---|---|---|
| count_tasks       | 0  | 0  | 0  | 10 | 0  |
| create_reminder   | 0  | 10 | 0  | 0  | 0  |
| create_task       | 0  | 0  | 10 | 0  | 0  |
| list_tasks        | 0  | 0  | 0  | 10 | 0  |
| update_task       | 0  | 0  | 0  | 0  | 10 |

## Pass Rates
- count_tasks: 0/10 (0%), 95% CI [0%, 28%]
- create_reminder: 8/10 (80%), 95% CI [49%, 94%]
- create_task: 9/10 (90%), 95% CI [60%, 98%]
- list_tasks: 10/10 (100%), 95% CI [72%, 100%]
- update_task: 10/10 (100%), 95% CI [72%, 100%]

## Proposed Fixes

### create_task — REJECTED
- Before: 'Add a new task.'
- After:  'Creates a brand-new task by specifying its title and priority, distinct from
           update_task (which modifies existing tasks) or create_reminder (...)'
- Pass rate: 9/10 → 7/10, p-value 1.0000
- Reason: rejected: made things worse

### count_tasks — REJECTED
- Before: 'Get tasks by status.'
- After:  'Return the number of tasks matching a given status, rather than the tasks
           themselves, by accepting a required status argument.'
- Pass rate: 0/10 → 0/10, p-value 1.0000
- Reason: rejected: no change
```

![toolfit: 74%](docs/examples/toy-server/toolfit-badge.svg)

Three things this run shows, none of them flattering, all of them the point:

- **The matrix names the real problem.** `count_tasks` is called *zero* times out of ten; every
  request meant for it goes to `list_tasks`. The solvability check flagged the identical
  `create_task`/`update_task` descriptions on 14 of 20 tasks — yet Sonnet 5 still picked the right
  one every time, because it reads `task_id` in the schema. Descriptions aren't the whole story,
  and toolfit measures what the model does, not what the text says.
- **The fix loop refused to claim a win.** Three rewrites were proposed and measured; one made
  things worse, two changed nothing. They are printed anyway. Every failure here is at the
  argument level or in the generator's "count vs. list" phrasing — things a description rewrite
  can't fix — and the numbers say so instead of the tool saying so.
- **Every number carries its uncertainty.** `9/10` and `7/10` overlap almost entirely at n=10;
  the exact test gives p=1.0 for a change in the wrong direction. Nothing gets reported as a
  finding because it looked good once.

## Two commands, two budgets

| | `scan` | `eval` |
|---|---|---|
| What | Static lint over `tools/list`: missing, too-short, and duplicated descriptions | Live model behaviour: which tool it calls, with which arguments, for a request that should lead to each tool |
| Cost | Free — no model calls, no key | Your API key: roughly `tools × seeds × 3` calls, plus `seeds` per proposed fix |
| Time | Under a second after the server starts | Minutes |
| Output | Findings list (never a letter grade) | Confusion matrix, per-tool pass rates with 95% CIs, mutation/fix verdicts, optional badge and `toolfit-fixes.json` |

They are deliberately separate. `scan` is the zero-config front door; on mature servers it finds
little ([1 finding across 166 tools on 15 public servers](docs/corpus.md)) because the bug it
catches is the copy-paste class. The confusion is what `eval` is for.

## Install

```
uvx toolfit --help          # zero-install, one-off
pipx install toolfit        # persistent / CI
```

Python 3.10+. Talks to servers over the MCP protocol via the official `mcp` SDK, so the
server can be in any language.

## Pointing it at a server

```
toolfit scan path/to/server.py                                  # run via `uv run`
toolfit scan "npx -y @modelcontextprotocol/server-filesystem ."   # any command line
toolfit scan https://your-host/mcp                              # Streamable HTTP
```

The subprocess inherits your environment, so servers that read a token from `GITHUB_TOKEN` or
`STRIPE_SECRET_KEY` work unchanged. toolfit never calls a tool — it only ever asks for the
catalog (`tools/list`), then asks a model what it *would* call. Nothing touches your backend.

## How the measurement works

The credibility problem with LLM-generated evals is circularity: if one model writes the task
and also decides the expected answer, you are measuring agreement with that model. toolfit
inverts it:

1. Sample a concrete, schema-valid argument set for one tool (`gen/schema_sampler.py`),
   honouring `required`, enums, formats, and nullables.
2. Ask a generator model to write the sentence a user would type that leads to *exactly those
   arguments*, without naming the tool. Ground truth is the sampled tuple, not the model's opinion.
3. Send that sentence plus the whole catalog to the model under test.
4. Grade structurally (`grade/grader.py`): right tool, and arguments equal after canonicalising
   dates, case, whitespace, and array order. No LLM judge, ever.

Guardrails: a second pass checks each task for tool-name leakage and for solvability against
the catalog; both are reported as warnings, never silently dropped. Tools whose schema the
sampler can't handle are excluded and listed — a partial number is never printed as a complete one.

**Mutation testing** is the same grader run twice. `--mutate 'tool:new description'` re-runs a
tool's *own* base tasks against a catalog where only that description is patched (protocol-level;
your source is never touched) and compares pass rates on paired trials. `--fix` does the same with
a proposed rewrite for every failing tool.

**Significance** is an exact one-sided McNemar test on the discordant pairs, Bonferroni-corrected
across everything re-measured in one run. It is deterministic and honest at small n: with 5 seeds
the smallest attainable p-value is 1/32, so `--seeds 10` is the practical floor for a verdict —
the CLI warns if you go lower. Every rate carries `n` and a Wilson 95% interval.

## CI

```yaml
- uses: sreshtalluri/toolfit@main
  with:
    server: "npx -y @modelcontextprotocol/server-github"
    eval: true                      # omit for the free scan only
    anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
```

`scan --strict` exits 1 on any finding; `eval --strict` exits 1 if any tool's pass rate is below
`--strict-threshold` (default 0.9). Tools excluded by a schema warning are named on stderr and
*not* counted — they don't fail the gate, but you'll see them.

`--badge` writes `toolfit-badge.svg` with the pass rate (or the before→after delta of a single
mutation or accepted fix), coloured by rate, with the model, generator, seed count, and a hash of
the task suite embedded so the number is never separable from what produced it.

## Models

`--model` picks the model under test and the provider is inferred from the name: `claude*` →
Anthropic, `gpt*`/`o*` → OpenAI, `vendor/model` → OpenRouter. Keys come from `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, `OPENROUTER_API_KEY`. Task generation and fix proposals always use Anthropic, so
that key is required for `eval` regardless of `--model`.

**Data handling.** The tool catalog and the generated task text are sent to whichever provider you
configure, with your key. toolfit itself stores nothing and phones nowhere. If your server is
internal, that is the one place its schema leaves your machine.

## Landscape

| Tool | What it does | Where it stops |
|---|---|---|
| mcpgrade | Static lint + single-step eval, A–F grade | No re-measured fix |
| mcpx | ESLint-style schema lint, CI gate | Never runs a model |
| MCProbe | Usability rules + input fuzzing | Fuzzing, not task performance |
| lastmile-ai/mcp-eval | Assertion framework with LLM judges | You write the tests |
| MCPJam Inspector | Hosted evals with cross-model comparison | GUI product, not a CLI |
| MCP-Atlas / MCP-Bench | Benchmarks ranking *models* | Not pointable at your server |

toolfit is not a model leaderboard and does not test for prompt injection. One server per run.

## Development

```
uv sync --extra dev
uv run pytest -q
uv run toolfit scan examples/toy_server.py
```

`examples/toy_server.py` has two deliberately confusable tool pairs — `create_task`/`update_task`
share a description, `list_tasks`/`count_tasks` share a vague one — so the fix loop has something
real to find. Design history and the methodology decisions behind every number are in
[`docs/designs/toolfit-v0-scope.md`](docs/designs/toolfit-v0-scope.md).

MIT.
