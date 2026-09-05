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

## Not done here

A model-graded `eval` across this corpus. Each server is ~`tools × seeds × 3` model calls plus the
fix loop; at 166 tools and 10 seeds that is several thousand calls, and it should be run per
server, with a read-scoped token where needed, by whoever wants that server's confusion matrix —
not as one unscoped batch. The toy-server run in `docs/examples/` is the reference for what the
output looks like.
