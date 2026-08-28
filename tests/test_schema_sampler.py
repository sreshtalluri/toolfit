import pytest

from toolfit.gen.schema_sampler import sample_arguments

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


def test_sample_arguments_rejects_unknown_property_name():
    schema = {
        "type": "object",
        "properties": {"unregistered_field": {"type": "string"}},
        "required": ["unregistered_field"],
    }
    with pytest.raises(ValueError, match="no example values registered"):
        sample_arguments(schema, seed=1)
