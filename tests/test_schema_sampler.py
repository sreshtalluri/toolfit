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
    assert isinstance(result["score"], float)
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


def test_sample_arguments_rejects_ref():
    schema = {
        "type": "object",
        "properties": {"thing": {"$ref": "#/definitions/Thing"}},
        "required": ["thing"],
    }
    with pytest.raises(ValueError, match=r"\$ref.*not supported"):
        sample_arguments(schema, seed=1)


def test_sample_arguments_rejects_allof():
    schema = {
        "type": "object",
        "properties": {"thing": {"allOf": [{"type": "string"}]}},
        "required": ["thing"],
    }
    with pytest.raises(ValueError, match="allOf.*not supported"):
        sample_arguments(schema, seed=1)


def test_count_distinct_handles_array_valued_arguments():
    # Lists aren't hashable directly — count_distinct must handle this without raising.
    assert count_distinct([{"tags": ["a", "b"]}, {"tags": ["a", "b"]}, {"tags": ["c"]}]) == 2
