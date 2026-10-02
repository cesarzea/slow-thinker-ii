"""Dynamic callback references must remain valid under the supported Python runtime."""

from tooling.quality.dynamic_callbacks import HTML_PARSER_CALLBACKS


def test_registered_standard_library_callbacks_exist() -> None:
    assert all(callable(callback) for callback in HTML_PARSER_CALLBACKS)
    assert {callback.__name__ for callback in HTML_PARSER_CALLBACKS} == {
        "handle_starttag",
        "handle_endtag",
    }
