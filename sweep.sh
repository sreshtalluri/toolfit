#!/bin/bash
# Runs one server across all 10 models, strictly sequential (avoids OpenRouter
# rate-limit exhaustion from stacking multiple models' --workers concurrently).
# Writes docs/examples/model-sweep/<server-name>/<model-slug>.md
# Retries a model up to 3 attempts total if the CLI call itself errors out
# (rc!=0, e.g. rate-limit exhaustion) before recording it as a real failure.
# Usage: bash sweep.sh <server_path> <server-name>
set -u
cd /Users/sreshtalluri/Documents/Github/toolfit/.claude/worktrees/agent-af4b3e1e61e3a0d2e
set -a
source .env
set +a

SERVER_PATH="$1"
SERVER_NAME="$2"
OUTDIR="docs/examples/model-sweep/${SERVER_NAME}"
mkdir -p "$OUTDIR"
LOG="sweep-${SERVER_NAME}.log"

MODELS=(
  "meta-llama/llama-3.3-70b-instruct"
  "qwen/qwen3-32b"
  "mistralai/mistral-small-3.2-24b-instruct"
  "mistralai/mistral-nemo"
  "google/gemma-3-27b-it"
  "openai/gpt-4o-mini"
  "openai/gpt-4.1-mini"
  "deepseek/deepseek-chat-v3-0324"
  "google/gemini-2.5-flash"
  "claude-sonnet-5"
)

echo "=== sweep started $(date) for $SERVER_NAME (sequential) ===" >> "$LOG"

for MODEL in "${MODELS[@]}"; do
  SLUG="${MODEL//\//-}"
  OUTFILE="${OUTDIR}/${SLUG}.md"
  # success = non-empty .md and no leftover .stderr from a prior failed attempt
  if [ -s "$OUTFILE" ] && [ ! -f "${OUTFILE}.stderr" ]; then
    echo "SKIP (already succeeded): $SERVER_NAME / $MODEL" >> "$LOG"
    continue
  fi
  for ATTEMPT in 1 2 3; do
    echo "START $(date +%H:%M:%S) attempt $ATTEMPT: $SERVER_NAME / $MODEL" >> "$LOG"
    START=$(date +%s)
    uv run toolfit eval "$SERVER_PATH" --model "$MODEL" --seeds 10 --workers 4 > "$OUTFILE" 2> "${OUTFILE}.stderr"
    RC=$?
    END=$(date +%s)
    echo "DONE $(date +%H:%M:%S) rc=$RC elapsed=$((END-START))s attempt $ATTEMPT: $SERVER_NAME / $MODEL" >> "$LOG"
    if [ $RC -eq 0 ]; then
      rm -f "${OUTFILE}.stderr"
      break
    fi
    echo "  -> attempt $ATTEMPT FAILED, stderr at ${OUTFILE}.stderr" >> "$LOG"
    if [ $ATTEMPT -eq 3 ]; then
      echo "  -> GIVING UP after 3 attempts: $SERVER_NAME / $MODEL" >> "$LOG"
    else
      echo "  -> cooling down 30s before retry (persistent rate-limit exhaustion, not a burst)" >> "$LOG"
      sleep 30
    fi
  done
done

echo "=== sweep finished $(date) for $SERVER_NAME ===" >> "$LOG"
