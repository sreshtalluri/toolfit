# Public server corpus — `toolfit scan` (2026-09-05)

Twenty public MCP servers, launched exactly as their READMEs say, scanned with the free static
path (`toolfit scan "<command>"`). No API keys, no model calls. Fifteen were reachable without
credentials; five need a token just to answer `tools/list`.

| Server | Launch | Tools | Findings |
|---|---|---|---|
| server-everything | `npx -y @modelcontextprotocol/server-everything` | 13 | none |
| server-filesystem | `npx -y @modelcontextprotocol/server-filesystem <dir>` | 14 | none |
| server-memory | `npx -y @modelcontextprotocol/server-memory` | 9 | none |
| server-sequential-thinking | `npx -y @modelcontextprotocol/server-sequential-thinking` | 1 | none |
| server-github | `npx -y @modelcontextprotocol/server-github` | 26 | none |
| mcp-server-fetch | `uvx mcp-server-fetch` | 1 | none |
| mcp-server-git | `uvx mcp-server-git --repository <path>` | 12 | none |
| mcp-server-time | `uvx mcp-server-time` | 2 | none |
| Playwright | `npx -y @playwright/mcp@latest` | 24 | 1 — `browser_close` description is 14 chars: `'Close page'` |
| Context7 | `npx -y @upstash/context7-mcp` | 2 | none |
| Notion | `npx -y @notionhq/notion-mcp-server` | 24 | none |
| Firecrawl | `npx -y firecrawl-mcp` | 25 | none (warns about missing API key, still serves the catalog) |
| Exa | `npx -y exa-mcp-server` | 2 | none |
| Browserbase | `npx -y @browserbasehq/mcp` | 6 | none |
| Tavily | `npx -y tavily-mcp` | 5 | none |
| Supabase | `npx -y @supabase/mcp-server-supabase@latest` | — | needs `SUPABASE_ACCESS_TOKEN` before `tools/list` |
| Sentry | `npx -y @sentry/mcp-server` | — | needs `--access-token` / device-code login |
| Stripe | `npx -y @stripe/mcp --tools=all` | — | needs `STRIPE_SECRET_KEY` |
| HubSpot | `npx -y @hubspot/mcp-server` | — | needs `PRIVATE_APP_ACCESS_TOKEN` |
| Cloudflare | `npx -y @cloudflare/mcp-server-cloudflare` | — | needs a `run <account>` subcommand |

## What this says

**The static rules barely fire on mature servers: 1 finding across 166 tools.** Every one of
these catalogs has a non-empty description longer than 15 characters on every tool, and no two
tools share one. That is the honest ceiling of `scan`: it catches the copy-paste class of bug
(the toy server in `examples/` has two of them on purpose) and nothing subtler. The thing that
actually separates a good catalog from a confusing one — whether a model picks `create` when it
should pick `update` — needs a model in the loop, which is what `eval` is for and why the two
commands are kept apart.

**The Python-SDK servers (`mcp-server-fetch`, `-git`, `-time`) print a wall of pydantic warnings
on connect.** The v2 `mcp` client sends `server/discover` first; servers built on the older SDK
don't know that method and log a validation error before answering `initialize` normally. Harmless
to the scan, noisy on stderr; `toolfit` sends its own report to stdout so `2>/dev/null` gives a
clean result.

**Five of twenty refuse `tools/list` without credentials.** Dry-run mode only ever needs the
catalog, but these servers validate the token at startup, before the protocol handshake. Evaluating
them means supplying a real (read-scoped) token via the environment — `toolfit` passes the caller's
environment through to the subprocess, so `STRIPE_SECRET_KEY=... toolfit scan "npx -y @stripe/mcp
--tools=all"` is all it takes.

## Model-graded `eval` on three of them (2026-09-05)

`toolfit eval "<launch>" --seeds 10 --fix --badge`, model under test `claude-sonnet-5`. Full
reports, fixes JSON and badges in `docs/examples/<server>/`.

| Server | Tools | Pass | Wall time | Rate-limit retries | Fixes proposed / accepted |
|---|---|---|---|---|---|
| server-memory | 9 | 90/90 (100%) | 7.5 min | 24, all recovered | 0 / — |
| mcp-server-git | 12 | 112/120 (93%) | ~8 min | 15 | 3 / 0 |
| server-filesystem | 14 | 77/140 (55%) | 22 min | — | 12 / 0 |

What they taught, in order of how much code changed because of it:

1. **Retry has to cover every model call, not just the model under test.** The first attempt at
   all three died on a 429 raised inside task generation, which had no backoff. Fixed; the retry
   ceiling went from 3 to 5 attempts (~31 s).
2. **Precondition steps read as confusion.** `git_commit` → `git_add` (5/10), and
   `list_allowed_directories` called first for `directory_tree`, `get_file_info`,
   `list_directory`, `move_file`, `read_*` (4–8 each). The model is right; the single-step grader
   is strict. The matrix column makes it obvious, which is the point of the matrix. A multi-step
   harness (source doc M5) is the real answer.
3. **`number` means integer in practice.** zod-generated schemas type `head`/`tail`/`max_count`
   as `number`; sampling `76.22` produced tasks the solvability check rejected. Now integers.
4. **Deprecated tools are a lint category.** `read_file` obeys its own "DEPRECATED" note: 0/10.
   New `deprecated_tool` rule — the first static rule to fire on a mature public server.
5. **Bonferroni across a whole catalog's proposals is unwinnable at n=10.** α=0.05/12=0.004
   needs ≥8 discordant pairs all in one direction. The verdict now prints p vs corrected α.
   Guidance: `--fix` per tool of interest with `--seeds 20`.

Not done: the other twelve reachable servers, and any eval with a non-Anthropic model under test
(`OPENROUTER_API_KEY` was empty). Each server is roughly `tools × seeds × 3` calls plus `seeds`
per proposed fix.
