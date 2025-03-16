import json
import pytest
from unittest import mock

from content_generator import utils


def test_keyword_cleanup():
    """Are selected keywords removed from list of keywords?"""
    suggestions = [
        "i feel you",
        "i feel you meaning",
        "can i get butter song",
        "funny gif bar stool",
        "girls only",
        "cupboard synonym"
    ]
    
    expected = [
        "i feel you",
        "can i get butter",
        "funny bar stool",
        "girls only",
        "cupboard"
    ]

    assert set([utils.clean_autocomplete_suggestion(s) for s in suggestions]) == set(expected)

@pytest.fixture
def mock_filesystem(tmp_path):
    # Create mock metadata files
    tmp_data_dir = tmp_path / "data"
    love_letters_metadata = tmp_data_dir / "love_letters" / "metadata"
    date_profiles_metadata = tmp_data_dir / "date_profiles" / "metadata"
    titles_json_path = tmp_data_dir / "date_profiles" / "titles.json"

    love_letters_metadata.mkdir(parents=True)
    date_profiles_metadata.mkdir(parents=True)

    (love_letters_metadata / "letter1.txt").write_text("prefix1;some data\nprefix2;some other data")
    (date_profiles_metadata / "profile1.txt").write_text("prefix3;data\nprefix4;other data")

    titles_json = {
        "title": [
            {"prefix": "prefix5"},
            {"prefix": "prefix6"}
        ]
    }
    titles_json_path.write_text(json.dumps(titles_json))

    return tmp_path


def test_get_all_prefixes(mock_filesystem):
    """Are all prefixes from metadata files returned?"""
    with mock.patch("content_generator.utils.BASE", mock_filesystem):
        prefixes = utils.get_all_prefixes()
        expected_prefixes = {"prefix1", "prefix2", "prefix3", "prefix4", "prefix5", "prefix6"}
        assert set(prefixes) == expected_prefixes