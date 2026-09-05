# TODOS

## eval

- **Multi-step grading (source doc M5).** On real servers the dominant off-diagonal mass is precondition calls (`git_add` before `git_commit`, `list_allowed_directories` before any path op) — correct behaviour a single-step grader scores as confusion. Grade the sequence, or let a tool declare its preconditions. **Priority:** P1
- **Separate `(error)` column.** max_tokens truncation, malformed tool-call JSON, and empty `choices` are tallied with genuine no-calls. Add `error` to `ToolCall` and a column so a flaky provider doesn't read as a confusing catalog. **Priority:** P2
- **Non-Anthropic model under test on the corpus.** `OPENROUTER_API_KEY` was empty during the scenario runs; a small model is far likelier to confuse the toy pairs and give `--fix` something to accept. **Priority:** P2
- **`--strict` on schema-excluded tools.** Currently warn-only (decided 2026-09-05). Revisit if a real CI user is surprised by a green gate on an unevaluated server. **Priority:** P3

## gen

- **Constraints the schema can't express.** `read_text_file` accepts `head` OR `tail`, not both; the sampler draws both 25% of the time and the solvability check rejects the task. Consider honouring `oneOf`/`not` at the object level, or a per-server task-rejection budget. **Priority:** P3

## Completed

- v0.1.0 (2026-09-05): scan, eval, mutation testing, fix loop, badge, strict, generic launch, Action, corpus, three real-server scenarios.
