from unittest import mock
from unittest.mock import patch
from pathlib import Path

import pytest

# Mock the global call to read cache from Cloud Storage before importing the module
with patch(
    "content_generator.gcs_utils.get_cached_autocomplete_suggestions"
) as mock_get_cache:
    from content_generator.autocomplete import (
        get_autocomplete_suggestions,
        fill_template,
    )

from content_generator.utils import extract_tokens_from_brackets


def test_get_autocomplete_suggestions():
    """Test autocomplete suggestions are queried with a whitespace appended to the prefix."""
    query_strings = ["I love to", "How to cook"]

    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = ["", ["suggestion1", "suggestion2"]]
        result = get_autocomplete_suggestions(query_strings)

        for call in mock_get.call_args_list:
            params = call[1]["params"]
            assert params["q"].endswith(" ")
            assert params["q"].strip() in query_strings

    assert result == {
        "I love to": ["suggestion1", "suggestion2"],
        "How to cook": ["suggestion1", "suggestion2"],
    }

def test_fill_template():
    """Test that the template is filled with autocomplete suggestions."""
    # TODO: Make this more reobust:
    # currently, this relies on all metadata tokens being replaced. 
    template_content = "This is a sample template with prefix1 blank1 and prefix2 blank2."
    metadata_content = "prefix1;blank1\nprefix2;blank2"
    autocomplete_cache = {
        "prefix1": ["suggestion1"],
        "prefix2": ["suggestion2"]
    }

    template_path = Path("/fake/path/template.md")
    metadata_path = Path("/fake/path/metadata/template.txt")

    mock_template_open = mock.mock_open(read_data=template_content)
    mock_metadata_open = mock.mock_open(read_data=metadata_content)

    with mock.patch("builtins.open", side_effect=[mock_template_open.return_value, mock_metadata_open.return_value]):
        with mock.patch("content_generator.autocomplete.autocomplete_cache", autocomplete_cache):
            result = fill_template(template_path, 1)  # force a 100% splice percentage to ensure all tokens are replaced

    expected_result = "This is a sample template with **suggestion1** and **suggestion2**."
    assert result == expected_result

@pytest.mark.parametrize(
        "template,expected",
        [
            ("Some title", None),
            ("A [Better;Title]", ("Better", "Title")),
            ("take me for a [new;ride] next week", ("new", "ride")),
            ("[The Finer;Things]", ("The Finer", "Things")),
        ]
    )
def test_extract_tokens_from_brackets(template, expected):
    """Test title component extraction for [prefox;stub] format."""
    assert extract_tokens_from_brackets(template) == expected
