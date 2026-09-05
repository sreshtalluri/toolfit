import pytest

from toolfit.gen.schema_sampler import count_distinct, sample_arguments

CREATE_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "priority": {"type": "string"},
    },
    "required": ["title", "priority"],
}


def test_sample_arguments_returns_all_required_properties():
    result = sample_arguments(CREATE_TASK_SCHEMA, seed=1)
    assert set(result.keys()) == {"title", "priority"}


def test_sample_arguments_is_deterministic_for_same_seed():
    first = sample_arguments(CREATE_TASK_SCHEMA, seed=42)
    second = sample_arguments(CREATE_TASK_SCHEMA, seed=42)
    assert first == second


def test_sample_arguments_rejects_non_object_schema():
    with pytest.raises(ValueError, match="expected object schema"):
        sample_arguments({"type": "string"}, seed=1)


def test_sample_arguments_generates_a_generic_placeholder_for_an_unregistered_property_name():
    schema = {
        "type": "object",
        "properties": {"some_new_field": {"type": "string"}},
        "required": ["some_new_field"],
    }
    result = sample_arguments(schema, seed=1)
    assert "some_new_field" in result["some_new_field"] or isinstance(result["some_new_field"], str)
    assert len(result["some_new_field"]) > 0


def test_count_distinct_counts_all_unique_sets():
    assert count_distinct([{"status": "open"}, {"status": "done"}, {"status": "in_progress"}]) == 3


def test_count_distinct_detects_a_collision():
    assert count_distinct([{"status": "open"}, {"status": "open"}, {"status": "done"}]) == 2


def test_count_distinct_of_empty_list_is_zero():
    assert count_distinct([]) == 0


def test_sample_arguments_picks_an_enum_value():
    schema = {
        "type": "object",
        "properties": {"priority": {"type": "string", "enum": ["low", "medium", "high"]}},
        "required": ["priority"],
    }
    result = sample_arguments(schema, seed=1)
    assert result["priority"] in ("low", "medium", "high")


def test_sample_arguments_generates_a_date_format_value():
    schema = {
        "type": "object",
        "properties": {"remind_at": {"type": "string", "format": "date"}},
        "required": ["remind_at"],
    }
    result = sample_arguments(schema, seed=1)
    # ISO date shape: YYYY-MM-DD
    parts = result["remind_at"].split("-")
    assert len(parts) == 3
    assert len(parts[0]) == 4


def test_sample_arguments_generates_an_email_format_value():
    schema = {
        "type": "object",
        "properties": {"contact": {"type": "string", "format": "email"}},
        "required": ["contact"],
    }
    result = sample_arguments(schema, seed=1)
    assert "@" in result["contact"]


def test_sample_arguments_generates_a_uuid_format_value():
    import uuid

    schema = {
        "type": "object",
        "properties": {"external_id": {"type": "string", "format": "uuid"}},
        "required": ["external_id"],
    }
    result = sample_arguments(schema, seed=1)
    uuid.UUID(result["external_id"])  # raises ValueError if not a valid UUID string


def test_sample_arguments_generates_a_date_time_format_value():
    schema = {
        "type": "object",
        "properties": {"when": {"type": "string", "format": "date-time"}},
        "required": ["when"],
    }
    result = sample_arguments(schema, seed=1)
    assert "T" in result["when"]


def test_sample_arguments_rejects_unsupported_format():
    schema = {
        "type": "object",
        "properties": {"weird": {"type": "string", "format": "ipv4"}},
        "required": ["weird"],
    }
    with pytest.raises(ValueError, match="unsupported format"):
        sample_arguments(schema, seed=1)


def test_sample_arguments_generates_integer_number_and_boolean():
    schema = {
        "type": "object",
        "properties": {
            "count": {"type": "integer"},
            "score": {"type": "number"},
            "active": {"type": "boolean"},
        },
        "required": ["count", "score", "active"],
    }
    result = sample_arguments(schema, seed=1)
    assert isinstance(result["count"], int)
    assert isinstance(result["score"], int)  # integers are valid numbers and read naturally in tasks
    assert isinstance(result["active"], bool)


def test_sample_arguments_generates_an_array_of_strings():
    schema = {
        "type": "object",
        "properties": {"tags": {"type": "array", "items": {"type": "string", "enum": ["a", "b"]}}},
        "required": ["tags"],
    }
    result = sample_arguments(schema, seed=1)
    assert isinstance(result["tags"], list)
    assert len(result["tags"]) >= 1
    assert all(v in ("a", "b") for v in result["tags"])


def test_sample_arguments_rejects_array_with_no_items_schema():
    schema = {
        "type": "object",
        "properties": {"tags": {"type": "array"}},
        "required": ["tags"],
    }
    with pytest.raises(ValueError, match="no 'items' schema"):
        sample_arguments(schema, seed=1)


def test_sample_arguments_picks_one_branch_of_anyof():
    schema = {
        "type": "object",
        "properties": {"notes": {"anyOf": [{"type": "string", "enum": ["x"]}, {"type": "null"}]}},
        "required": ["notes"],
    }
    # Run many seeds — with a 2-branch anyOf, some should be None and some "x".
    results = {sample_arguments(schema, seed=s)["notes"] for s in range(1, 21)}
    assert results <= {"x", None}
    assert len(results) == 2  # both branches actually got hit across 20 seeds


def test_sample_arguments_rejects_an_unresolvable_ref():
    schema = {
        "type": "object",
        "properties": {"thing": {"$ref": "#/definitions/Thing"}},
        "required": ["thing"],
    }
    with pytest.raises(ValueError, match=r"unresolvable \$ref"):
        sample_arguments(schema, seed=1)


def test_sample_arguments_merges_a_single_branch_allof():
    schema = {
        "type": "object",
        "properties": {"thing": {"allOf": [{"type": "string", "enum": ["only"]}], "description": "d"}},
        "required": ["thing"],
    }
    assert sample_arguments(schema, seed=1) == {"thing": "only"}


def test_sample_arguments_always_includes_required_and_sometimes_omits_optional():
    schema = {
        "type": "object",
        "properties": {"title": {"type": "string"}, "notes": {"type": "string"}},
        "required": ["title"],
    }
    samples = [sample_arguments(schema, seed=s) for s in range(1, 21)]
    assert all("title" in s for s in samples)
    with_notes = sum("notes" in s for s in samples)
    assert 0 < with_notes < 20


def test_sample_arguments_handles_list_typed_nullable():
    schema = {"type": "object", "properties": {"x": {"type": ["string", "null"]}}, "required": ["x"]}
    results = {sample_arguments(schema, seed=s)["x"] for s in range(1, 21)}
    assert None in results
    assert any(isinstance(r, str) for r in results)


def test_sample_arguments_honours_numeric_bounds():
    schema = {
        "type": "object",
        "properties": {
            "temperature": {"type": "number", "minimum": 0, "maximum": 1},
            "page": {"type": "integer", "minimum": 1, "maximum": 3},
            "ratio": {"type": "number", "minimum": 0.5, "maximum": 0.75},
        },
        "required": ["temperature", "page", "ratio"],
    }
    for seed in range(1, 30):
        r = sample_arguments(schema, seed=seed)
        assert 0 <= r["temperature"] <= 1
        assert r["page"] in (1, 2, 3)
        assert 0.5 <= r["ratio"] <= 0.75


def test_sample_arguments_resolves_pydantic_style_refs_and_all_of():
    # Exactly what `mcp` emits for `address: Address | None` on a pydantic model.
    schema = {
        "type": "object",
        "$defs": {
            "Address": {
                "type": "object",
                "properties": {"city": {"type": "string"}, "country": {"type": "string", "enum": ["US"]}},
                "required": ["city", "country"],
            }
        },
        "properties": {
            "address": {"anyOf": [{"$ref": "#/$defs/Address"}, {"type": "null"}]},
            "billing": {"allOf": [{"$ref": "#/$defs/Address"}], "description": "billing address"},
        },
        "required": ["address", "billing"],
    }
    seen = set()
    for seed in range(1, 20):
        r = sample_arguments(schema, seed=seed)
        assert set(r["billing"]) == {"city", "country"} and r["billing"]["country"] == "US"
        seen.add(None if r["address"] is None else "obj")
        if r["address"] is not None:
            assert r["address"]["country"] == "US"
    assert seen == {None, "obj"}


def test_sample_arguments_rejects_a_remote_ref():
    schema = {"type": "object", "properties": {"x": {"$ref": "https://example.com/s.json"}}, "required": ["x"]}
    with pytest.raises(ValueError, match="local"):
        sample_arguments(schema, seed=1)


def test_sample_arguments_recurses_into_nested_objects():
    schema = {
        "type": "object",
        "properties": {
            "filter": {
                "type": "object",
                "properties": {"status": {"type": "string", "enum": ["open"]}},
                "required": ["status"],
            }
        },
        "required": ["filter"],
    }
    assert sample_arguments(schema, seed=1) == {"filter": {"status": "open"}}


def test_count_distinct_handles_array_valued_arguments():
    # Lists aren't hashable directly — count_distinct must handle this without raising.
    assert count_distinct([{"tags": ["a", "b"]}, {"tags": ["a", "b"]}, {"tags": ["c"]}]) == 2
