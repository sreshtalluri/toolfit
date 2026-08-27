# Product Doc: MCP Server Fitness Harness

Status: draft v1
Owner: Sreshta
Date: 2026-08-26

---

## 0. Read this first: what changed from the original idea

The original pitch was "point a harness at any MCP server, generate tasks, run N models, produce a report card, and note that almost nobody is doing this." That last part is no longer true. As of mid 2026 the space has at least four shipped entrants:

| Tool | What it does | Where it stops |
|---|---|---|
| mcpgrade (tengli.dev) | Static lint of tool and parameter descriptions, A to F grade, plus `--eval` that synthesizes single step tasks and measures tool pick and argument validity. Author already published a "I scanned 36 popular servers" post. | Single step only. No multi turn, no state, no fix loop. |
| mcpx (github.com/sameenchand/mcpx) | ESLint style schema linter, A to F grade, token bloat flags, CI gate. | Static only. Never runs a model. |
| MCProbe (mcprobe.org) | Static agent usability rules plus behavioral fuzzing with bad inputs, 0 to 100 conformance score, fix list. | Fuzzing, not task performance. No model in the loop. |
| lastmile-ai/mcp-eval | Real eval framework: assertions, LLM judges, OTel metrics, CI reports. | You write the test cases. Zero config generation is not the product. |
| MCPJam Inspector | Hosted evals with accuracy, TPR, FPR, cross model comparison. | Product, not open source CLI. GUI first. |
| MCP-Atlas, MCP-Bench, LiveMCPBench | Academic benchmarks ranking *models* across many servers. | They benchmark models, not your server. Not pointable at an arbitrary server. |

Two consequences:

1. **"Report card for any MCP server" is a commodity.** Building it again is a portfolio exercise, which is exactly what the original pitch said it was not.
2. **The open ground is the closed loop.** Every existing tool ends at a number and a list of complaints. None of them proposes a concrete fix to your tool schemas, applies it, re runs the eval, and shows you the delta. That is the product.

Reframed one liner:

> **Whetstone finds the specific places your MCP server confuses models, rewrites the tool descriptions and schemas to fix them, and proves the fix with a before and after eval.**

Measurement is table stakes and stays in scope. The differentiator is `--fix` producing a PR ready diff plus a verified score delta.

---

## 1. Problem

Tool descriptions are the entire API surface an agent sees. They are written last, by engineers, in a hurry. Research on 10,831 servers found description quality problems are pervasive, and controlled mutation showed description quality moves tool selection accuracy by roughly 9 to 12 points, with far larger effects when several functionally similar tools compete. Server authors have no feedback signal for this. Their tests pass, their server is spec compliant, and agents still pick the wrong tool.

Existing linters tell an author that a parameter lacks a description. That is the easy half. The hard half is: which two of your tools do models confuse with each other, on what kind of user request, and what exact wording removes the ambiguity.

## 2. Users

**Primary: MCP server author** (devtool startup, platform team shipping an internal server). Wants their server to work well in Claude Code, Cursor, and their customers' agents. Will run this in CI.

**Secondary: agent developer choosing between servers or models.** Wants to know whether to use server A or B, and which model handles their toolset. Gets value from the report card even without the fix loop.

**Non user for v0:** researchers benchmarking frontier models. MCP-Atlas owns that. Do not compete there.

## 3. Goals and non goals

**Goals**
- Zero config: point it at a server, get a useful report in under ten minutes.
- Diagnostics at the level of a specific tool pair or a specific parameter, not a global score.
- A proposed fix that is machine applicable and verified by re running the eval.
- Safe by default against real servers with real side effects.
- Deterministic enough that the same run twice gives an interpretable number, with variance reported rather than hidden.

**Non goals for v0**
- Web UI. CLI plus markdown and JSON output only.
- Multi server orchestration. One server per run.
- Security or prompt injection testing. Adjacent, well covered by MSB, and a scope trap.
- Ranking frontier models. That is a byproduct, not the pitch.

## 4. The hard problem: where does ground truth come from

This is the part the original pitch skipped and it is the part that decides whether the project is credible.

If one LLM generates the task and also declares the expected tool call, the eval measures agreement with the generator, not correctness. Any reviewer who has built evals will spot this in thirty seconds.

Three tiers, in order of increasing trust. Ship tier 1 and 2 in v0, tier 3 in v1.

**Tier 1: inverted generation (cheap, defensible).**
Do not ask a model "what task tests this server." Pick one target tool. Sample a concrete valid argument set from its JSON schema (enums, formats, required fields). Then ask a generator model to write the natural language request a user would send *that leads to exactly those arguments*, without naming the tool. Ground truth is now the tuple you sampled, not the generator's opinion. Grading is a structural comparison against that tuple. The generator's only job is to write English, which is the thing it is reliable at.

Guardrails: a second model reviews each task for tool name leakage and for solvability given the visible catalog. Any task where three of three cheap models fail identically gets flagged as a possibly bad task, not a possibly bad server. Report task rejection rate in the appendix so the methodology is auditable.

**Tier 2: mutation testing (the strongest signal in v0, and unusual).**
This is the piece that makes the tool defensible and gives it its own research angle. Take the server as is, measure baseline accuracy. Then perturb one thing: strip a parameter description, shorten a tool description, or make two tool descriptions more similar. Re measure. The delta attributes the score to a specific piece of text. Run it in reverse for `--fix`: rewrite one description, re measure, keep the change only if the delta clears noise.

This turns a subjective claim ("your description is vague") into a measured one ("rewriting `search_messages` moved tool selection from 61 to 84 percent, n=40, 3 seeds").

**Tier 3: human authored golden set (v1).**
For servers where you personally know the domain, hand write twenty tasks. Use them to validate that tier 1 tasks correlate with hand written ones. Publish the correlation. This is what turns the harness from a plausible tool into a trusted one.

## 5. Metrics

Scores are per tool and per pair first, aggregate second. An aggregate number alone is not actionable and is easy to dismiss.

**Selection**
- Tool recall (TPR): when tool T is correct, how often is it called. Low recall means T is underdescribed or invisible.
- Tool false positive rate: how often T is called when it should not be. High FPR means T is overbroad or steals from a neighbor.
- **Confusion matrix over tools.** The headline artifact. Off diagonal mass names the exact pairs to fix. Nothing in the current market ships this.

**Arguments**
- Schema validity rate: does the call validate against the JSON schema.
- Argument exact match rate against the sampled ground truth tuple.
- Per parameter error rate, split into: omitted required, wrong type, hallucinated value not present in the prompt, wrong enum member, wrong format (dates, IDs, pagination cursors).

**Behavior under failure**
- Error recovery rate: after an injected error response, does the model repair the call within k turns.
- Injected failure classes: validation error, empty result set, rate limit, auth expired, paginated result requiring a follow up call.
- This is where most real servers fall over and where almost no existing tool looks.

**Efficiency**
- Turns to completion, tool calls to completion, redundant call rate.
- Tokens and cost per task, split into schema overhead versus conversation. Schema overhead is a real finding for bloated servers: a catalog that eats 12k tokens before the user says anything is a defect worth reporting.

**Reliability of the measurement itself**
- Every metric reported with n, number of seeds, and a confidence interval. Any single run is noise. Publishing a grade with no variance is how you get correctly torn apart by a founder.

## 6. Architecture

```
whetstone/
  cli.py              typer entrypoint: scan | eval | fix | report
  connect/            stdio + streamable HTTP transports, auth, tool catalog fetch
  lint/               static rules over the catalog (fast, no model, no cost)
  gen/                task synthesis: schema sampler -> prompt writer -> validator
  run/                model adapters, conversation loop, failure injection
  grade/              structural graders + optional LLM judge for final answers
  fix/                description rewriter, patch emitter, A/B re-runner
  report/             markdown + JSON emitters, confusion matrix rendering
  safety/             read-only classification, dry-run proxy, allowlists
  tasks/              cached task suites, checked in per server fingerprint
```

**Model adapters:** one thin interface, implementations for Anthropic, OpenAI, and one open model via OpenRouter. Same client wrapper for every model so the comparison is apples to apples. Pin model versions in the report; unpinned model names make a report unreproducible within weeks.

**Task caching:** hash the tool catalog. Same fingerprint reuses the cached suite so re runs are comparable and cheap. Schema change invalidates only affected tasks.

**Safety (this determines whether anyone lets you run it against their server):**
- Default `--read-only`. Classify tools using MCP `readOnlyHint` and `destructiveHint` annotations when present, keyword heuristics when not, and a model classifier as a tiebreaker. Anything not confidently read only is excluded unless explicitly allowlisted.
- `--dry-run` mode: the harness intercepts the call at the transport layer, validates it against the schema, and returns a synthetic result. Never touches the real backend. This is the mode used for selection and argument metrics, which is most of the report. It also means you can evaluate a server you do not have write credentials for.
- Live mode is opt in, per tool, and prints exactly what it will execute.

Getting this right is a feature, not overhead. It is the reason someone lets you run this against their production server.

## 7. Output

Two artifacts per run.

`report.md`, in this order:
1. Grade and the two or three findings that matter, at the top. Nobody reads past the first screen.
2. Confusion matrix.
3. Per tool table: recall, FPR, argument validity, cost contribution.
4. Failure taxonomy with three real transcripts per class, trimmed.
5. Model comparison table.
6. Methodology, n, seeds, CI, task rejection rate, model versions, harness version.

`report.json`, stable schema, for CI diffing and for `whetstone compare a.json b.json`.

With `--fix`, additionally `fix.patch`: a diff against the server's tool definitions plus the measured delta per change, and the changes that were tried and rejected because the delta was inside noise. Showing the rejected ones is what makes the accepted ones believable.

## 8. Milestones

The original three to four week estimate is too long for a first public artifact while working full time. Split it. Something demoable and postable at day 10, then extend only if it earns attention.

**M0, days 1 to 2. Connect and lint.**
Transports working against stdio and remote HTTP servers. Catalog fetch. Static rules. Output a grade with no model calls. This alone reproduces mcpx and gives you a working artifact on day two.

**M1, days 3 to 5. Generate and grade, single step, dry run.**
Schema sampler, inverted task generation, task validator, structural grader. Selection and argument metrics, per tool and pair. Confusion matrix in the report.

**M2, days 6 to 8. Multi model and mutation.**
Three model adapters. Seeds and confidence intervals. Mutation harness: perturb one description, measure the delta. First real finding.

**M3, days 9 to 10. Ship v0.**
README with a real example run. GitHub Action. Scan ten to fifteen well known public servers, publish the results with the mutation evidence. This is the launch post.

**M4, days 11 to 16. The fix loop.**
Rewriter, patch emitter, A/B verification. This is the version you send to companies.

**M5, optional. Multi turn and failure injection.**
Stateful workflows, injected errors, recovery rate. Highest engineering cost, highest ceiling, only worth it if v0 gets traction.

## 9. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Crowded market, tool reads as a clone | High | Lead with the fix loop and the confusion matrix, not the grade. Cite the existing tools in the README and state what is different. Never pretend the space is empty; a founder who knows mcpgrade will notice. |
| Circular ground truth | High | Inverted generation. Mutation testing as the primary evidence. Publish task rejection rate. |
| Nondeterminism makes results unfalsifiable | High | Seeds, n, CI on every number. Refuse to print a grade below a minimum n. |
| Cannot connect to target servers (OAuth, private beta, no public endpoint) | Medium | Dry run mode needs only `tools/list`. Check reachability for each target before promising an artifact. |
| Scope creep into multi turn and security | Medium | Explicit non goals. M5 is gated on traction. |
| Report offends the recipient | Medium | See section 10. |

## 10. Adoption

An unsolicited grade is a status claim about someone else's work made by a stranger, and the downside is asymmetric: one methodological hole and the artifact becomes evidence against you. So the artifact is a **contribution**, not a grade: open a PR against the server's repo with the description fix and the before and after numbers in the PR body, or send the finding as a short note with the transcript attached. A merged PR is unambiguously positive. A grade is a coin flip. Same work, better packaging.

## 11. Success criteria

Six weeks after launch:
- The harness runs against at least fifteen public servers without hand holding.
- At least one description fix, discovered by the tool, merged into a third party server.
- The mutation result is reproducible by someone else from the README.

Stars are not a success criterion. One merged PR into a server someone actually uses beats two hundred stars.

## 12. Repo name candidates

| Name | Read | Notes |
|---|---|---|
| **whetstone** | Sharpens your tools | Top pick. Metaphor lands immediately, works as a verb in docs, distinct from every existing entrant. |
| **hone** | Same metaphor, shorter | Clean, likely contested on PyPI and npm. Check first. |
| **toolfit** | Fit between tools and models | Descriptive, searchable, less memorable. |
| **legible** | Is your server legible to a model | Strong concept, slightly abstract for a CLI. |
| **affordance** | Interface affordances for agents | Precise, a little academic, long to type. |
| **schema-smith** | Forges better schemas | Nice, hyphenated, slightly twee. |
| **tightloop** | Names the measure to fix to re measure cycle | Good if the fix loop is the whole identity. |
| **mcp-fitness** | Literal | Safe, forgettable, avoid unless discoverability wins. |

Recommendation: **whetstone**, CLI binary `whet`, tagline "sharpen your MCP server for the models that use it." If `whetstone` is taken on PyPI, `whetstone-mcp` with binary `whet` is fine.
