"""Sample one concrete, valid argument set from a tool's JSON Schema.

Spike scope only: handles the flat string-typed schemas used by examples/toy_server.py. Real
$ref/oneOf/anyOf/allOf/format/regex/nullable/dependent-constraint handling is explicitly scoped
to M1 (docs/designs/toolfit-v0-scope.md, Next Steps #3), not this spike.
"""

from __future__ import annotations

import random

# Deterministic example values per parameter name, so spike runs are reproducible without an
# LLM call for sampling itself (that call is reserved for the *task generator*, see taskgen.py).
_EXAMPLES: dict[str, list[str]] = {
    "title": ["Write Q3 report", "Fix login bug", "Book dentist appointment"],
    "priority": ["high", "medium", "low"],
    "task_id": ["t1", "t2", "t3"],
    "status": ["open", "done"],
}


def sample_arguments(schema: dict, *, seed: int) -> dict[str, str]:
    """Sample one valid argument value per property in `schema`.

    Only handles `type: object` schemas whose properties are `type: string` with no
    `enum`/`format`/`$ref` — the toy server's shape. Raises ValueError on anything more complex,
    on purpose: a spike that silently produces wrong samples on schemas it doesn't understand is
    worse than one that fails loudly (same "never suppress" ethos as the design doc's Failure
    Modes).
    """
    rng = random.Random(seed)
    if schema.get("type") != "object":
        raise ValueError(f"sample_arguments: expected object schema, got {schema.get('type')!r}")
    result: dict[str, str] = {}
    for prop_name, prop_schema in schema.get("properties", {}).items():
        if prop_schema.get("type") != "string":
            raise ValueError(
                f"sample_arguments: unsupported property type for {prop_name!r}: {prop_schema.get('type')!r}"
            )
        choices = _EXAMPLES.get(prop_name)
        if not choices:
            raise ValueError(f"sample_arguments: no example values registered for property {prop_name!r}")
        result[prop_name] = rng.choice(choices)
    return result
