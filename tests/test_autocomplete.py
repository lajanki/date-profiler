from unittest.mock import patch

from content_generator.autocomplete import get_autocomplete_suggestions


def test_get_autocomplete_suggestions():
    """Test autocomplete suggestions are queried with a whitespace appended to the query."""
    query_strings = ["I love to", "How to cook"]

    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = ["", ["suggestion1", "suggestion2"]]
        result = get_autocomplete_suggestions(query_strings)

        for call in mock_get.call_args_list:
            params = call[1]["params"]
            assert params["q"].endswith(" ")
            assert params["q"].strip() in query_strings

    assert result == {
        "I love to ": ["suggestion1", "suggestion2"],
        "How to cook ": ["suggestion1", "suggestion2"],
    }
