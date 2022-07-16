from charset_normalizer import CharsetMatch
from src import cache

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
    c = cache.Cache()

    expected = [
        "i feel you",
        "can i get butter",
        "funny bar stool",
        "girls only",
        "cupboard"
    ]
    assert set(c.clean(suggestions)) == set(expected)