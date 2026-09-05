"""Sample one concrete, valid argument set from a tool's JSON Schema.

M1 scope: the common JSON Schema subset real MCP servers actually use — string/integer/number/
boolean/array-of-primitives, enum, format (date/date-time/email/uuid), nullable fields (expressed as
`anyOf: [<type>, {"type": "null"}]`, the real shape the `mcp` SDK generates for `X | None` type
hints — verified empirically, not assumed), simple oneOf/anyOf (pick one branch), nested objects,
list-typed nullables, numeric bounds, and local `$ref`/`allOf` (what pydantic emits for nested
models — the CRM example's `address: Address | None`). Regex-pattern generation and dependent
constraints are still unsupported and raise loudly (never silently sampling wrong).
"""

from __future__ import annotations

import random
import uuid
from datetime import date, timedelta
from typing import Any, Callable

# Deterministic example values per parameter name, so runs are reproducible without an LLM call
# for sampling itself (that call is reserved for the *task generator*, see taskgen.py).
_EXAMPLES: dict[str, list[str]] = {
    "title": ["Write Q3 report", "Fix login bug", "Book dentist appointment"],
    "priority": ["high", "medium", "low"],
    "task_id": ["t1", "t2", "t3"],
    "status": ["open", "in_progress", "done"],
    "notify_channels": ["email", "sms", "slack"],
    "notes": ["Bring snacks", "Confirm with manager first", "Low priority"],
}

_FORMAT_GENERATORS: dict[str, Callable[[random.Random], str]] = {
    "date": lambda rng: (date(2026, 1, 1) + timedelta(days=rng.randint(0, 365))).isoformat(),
    "date-time": lambda rng: (date(2026, 1, 1) + timedelta(days=rng.randint(0, 365))).isoformat() + "T12:00:00",
    "email": lambda rng: f"user{rng.randint(1, 999)}@example.com",
    "uuid": lambda rng: str(uuid.UUID(int=rng.getrandbits(128))),
}

_UNSUPPORTED_KEYS = ("pattern",)


def _resolve(prop_schema: dict, root: dict) -> dict:
    """Inline local `$ref`s and merge `allOf` — the shapes pydantic emits for nested models
    (`{"$ref": "#/$defs/Address"}`, sometimes wrapped in `allOf` to carry a description)."""
    schema = dict(prop_schema)
    ref = schema.pop("$ref", None)
    if ref is not None:
        if not ref.startswith("#/"):
            raise ValueError(f"sample_arguments: only local $ref is supported, got {ref!r}")
        target: Any = root
        try:
            for part in ref[2:].split("/"):
                target = target[part]
        except (KeyError, TypeError, IndexError):
            raise ValueError(f"sample_arguments: unresolvable $ref {ref!r}") from None
        schema = {**_resolve(target, root), **schema}
    if "allOf" in schema:
        merged: dict = {}
        for sub in schema.pop("allOf"):
            merged.update(_resolve(sub, root))
        schema = {**merged, **schema}
    return schema


def sample_arguments(schema: dict, *, seed: int) -> dict[str, Any]:
    """Sample one valid argument value per property in `schema`.

    Raises ValueError on anything outside the supported subset (see module docstring), on
    purpose: a harness that silently produces wrong samples on schemas it doesn't understand is
    worse than one that fails loudly (same "never suppress" ethos as the design doc's Failure
    Modes).
    """
    rng = random.Random(seed)
    if schema.get("type") != "object":
        raise ValueError(f"sample_arguments: expected object schema, got {schema.get('type')!r}")
    return _sample_object(schema, rng, root=schema)


def _sample_object(schema: dict, rng: random.Random, *, root: dict) -> dict[str, Any]:
    # Required properties always; each optional one with 50% probability. Sampling every optional
    # (as this used to) turns a 10-filter search tool into a 10-argument task that the grader's
    # exact-match rule then fails on any omission, misattributing model behaviour to description
    # quality. Draw the coin before the value so the seed still fully determines the sample.
    required = set(schema.get("required", []))
    result: dict[str, Any] = {}
    for prop_name, prop_schema in schema.get("properties", {}).items():
        if prop_name in required or rng.random() < 0.5:
            result[prop_name] = _sample_value(prop_name, prop_schema, rng, root=root)
    return result


def _sample_value(prop_name: str, prop_schema: dict, rng: random.Random, *, root: dict) -> Any:
    prop_schema = _resolve(prop_schema, root)
    for key in _UNSUPPORTED_KEYS:
        if key in prop_schema:
            raise ValueError(f"sample_arguments: {key!r} not supported for property {prop_name!r} (M2+)")

    if "enum" in prop_schema:
        return rng.choice(prop_schema["enum"])

    branches = prop_schema.get("oneOf") or prop_schema.get("anyOf")
    if branches:
        return _sample_value(prop_name, rng.choice(branches), rng, root=root)

    prop_type = prop_schema.get("type")
    if isinstance(prop_type, list):
        # `"type": ["string", "null"]` is the hand-written-schema spelling of nullable.
        return _sample_value(prop_name, {**prop_schema, "type": rng.choice(prop_type)}, rng, root=root)

    if prop_type == "null":
        return None

    if prop_type == "object":
        return _sample_object(prop_schema, rng, root=root)

    if prop_type == "string":
        fmt = prop_schema.get("format")
        if fmt is not None:
            generator = _FORMAT_GENERATORS.get(fmt)
            if generator is None:
                raise ValueError(f"sample_arguments: unsupported format {fmt!r} for property {prop_name!r} (M2+)")
            return generator(rng)
        choices = _EXAMPLES.get(prop_name)
        if choices:
            return rng.choice(choices)
        # No registered example pool for this property name: real MCP servers have arbitrarily
        # many string field names, and raising here (as this used to) makes the sampler fail on
        # ordinary, unremarkable server shapes. Fall back to a generic, clearly-synthetic
        # placeholder instead — this is not one of the "never silently sample wrong" cases in the
        # module docstring, since any string value is a structurally valid sample for a plain
        # `{"type": "string"}` property with no further constraints.
        return f"sample-{prop_name}-{rng.randint(1, 999)}"

    if prop_type in ("integer", "number"):
        # An integer is a valid `number`, and zod-generated MCP schemas type counts (`head`,
        # `tail`, `max_count`) as `number`; "read the first 76.22 lines" is not a task anyone sends.
        # Honour declared bounds so a [0, 1] `temperature` doesn't get 73.
        lo = prop_schema.get("minimum", prop_schema.get("exclusiveMinimum", 0) + 1 if "exclusiveMinimum" in prop_schema else 1)
        hi = prop_schema.get("maximum", prop_schema.get("exclusiveMaximum", 101) - 1 if "exclusiveMaximum" in prop_schema else 100)
        if hi < lo:
            raise ValueError(f"sample_arguments: empty range for property {prop_name!r}: [{lo}, {hi}]")
        if isinstance(lo, float) or isinstance(hi, float):
            return round(rng.uniform(lo, hi), 2)
        return rng.randint(lo, hi)

    if prop_type == "boolean":
        return rng.choice([True, False])

    if prop_type == "array":
        items_schema = prop_schema.get("items")
        if items_schema is None:
            raise ValueError(f"sample_arguments: array property {prop_name!r} has no 'items' schema")
        count = rng.randint(1, 3)
        return [_sample_value(prop_name, items_schema, rng, root=root) for _ in range(count)]

    raise ValueError(f"sample_arguments: unsupported property type for {prop_name!r}: {prop_type!r}")


def _make_hashable(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_make_hashable(v) for v in value)
    if isinstance(value, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in value.items()))
    return value


def count_distinct(arg_sets: list[dict[str, Any]]) -> int:
    """How many of the given argument sets are actually distinct.

    Small example pools mean seeds can collide onto the same sampled arguments (design doc Open
    Questions: this happened with the original 2-value `status` pool). Rather than trying to
    engineer around every possible collision, callers report this honestly — "n=8, but only 5
    distinct" — instead of presenting a collided trial as independent evidence.
    """
    return len({tuple(sorted((k, _make_hashable(v)) for k, v in args.items())) for args in arg_sets})
