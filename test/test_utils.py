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