from backend.tribal_languages.indian_language_catalog import (
    get_language, list_languages, scheduled_language_keys,
)


def test_has_22_scheduled_languages():
    assert len(scheduled_language_keys()) == 22


def test_santali_and_manipuri_are_listed():
    keys = scheduled_language_keys()
    assert "santali" in keys
    assert "manipuri" in keys


def test_gondi_is_available_as_tribal_language():
    assert get_language("gondi")["category"] == "tribal/regional"


def test_unknown_language_raises_value_error():
    try:
        get_language("not_a_real_language")
    except ValueError as exc:
        assert "Unknown language" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unknown language")


def test_returned_metadata_is_a_copy():
    first = list_languages()
    first[0]["display_name"] = "changed"
    second = list_languages()
    assert second[0]["display_name"] != "changed"
