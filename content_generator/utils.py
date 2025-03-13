import os.path
import json
import glob
import requests

from content_generator import gcs_utils


BASE = os.path.join(os.path.dirname(__file__), "..")
SUGGEST_URL = "http://suggestqueries.google.com/complete/search"


def clean_autocomplete_suggestion(suggestion):
    """Many autocomplete suggestions are queries for movies, song lyrics and other specific
    items. This removes certain keywords from an API result.
    """
    # TODO season 7 etc
    keywords = [
        "lyrics",
        "chords",
        "song",
        "mp3",
        "app",
        "pdf",
        "imdb",
        "definition",
        "synonym",
        "meaning",
        "story",
        "latin",
        "quotes",
        "cast",
        "full movie",
        "episode",
        "gif",
        "meme",
        "essay"
    ]
    split = suggestion.split()
    words = [w for w in split if not any([invalid in w for invalid in keywords])]

    return " ".join(words)

def cleanup_extra_whitespace(s):
    """Remove whitespace before punctuation."""
    punctuation = {
        " ,": ",",
        " .": ".",
        " \"": "\"",
        " !": "!",
        " ?": ""
    }

    for old, replacement in punctuation.items():
        s = s.replace(old, replacement)

    return s

def split_metadata_token(token):
    """Metadafiles in data/love_letters/metadata and data/date_profiles/metadata consist ;-delimited
    lines of the form
        prefix;blank
    Split such a line into the two pieces
    """
    split = token.split(";")
    return split[0], split[1].strip()  # ensure no whitespace at the end of blank

def refresh_and_upload_cache():
    """Refresh the suggestion cache and upload to Cloud Storage."""
    cache = refresh_suggestion_cache()
    gcs_utils.upload_autocomplete_cache(cache)

def refresh_suggestion_cache():
    """Refresh autocomplete cache file for every prefixes in metadata files (templates and titles).
    Performs an API call for every (unqiue) prefix and stores to file.
    """
    letters = glob.glob("data/love_letters/metadata/*.txt")
    profiles = glob.glob("data/date_profiles/metadata/*.txt")
    path_to_titles = os.path.join(BASE, "data", "date_profiles", "titles.json")

    prefixes = []
    # get prefixes from templates
    for file_ in letters + profiles:
        with open(file_) as f:
            metadata = [row for row in f.readlines() if row.strip()]  # exclude empty rows
            lines = list(map(str.rstrip, metadata))

            for token in lines:
                prefix, _ = split_metadata_token(token)
                prefixes.append(prefix.lower())

    # add title prefixes
    with open(path_to_titles) as f:
        data = json.load(f)["title"]

        for token in data:
            prefixes.append(token["prefix"].lower())

    prefixes = list(set(prefixes))

    print("Refreshing cache file with {} prefixes".format(len(prefixes)))   
    totals = {}
    for q in prefixes:
        # Add a space to ensure the prefixes is fully contained in the resulting suggestions,
        # ie. "I love to" will also result in suggestions such as "I love you",
        # Whereas "I love to " keeps to orignal prefix in the response.
        query_string = q + " " 
        r = requests.get(SUGGEST_URL, params={"client":"firefox", "q":query_string})

        totals[q] = r.json()[1]  # first item in the response is the original query string, second is the set of suggestions.
                                 # Also, note that the key is without the trailing space

    return totals

def format_sources_to_html():
    """Get list of sources from the SOURCES file and format as html."""
    path_to_sources = os.path.join(BASE, "data", "SOURCES")
    with open(path_to_sources) as f:
        lines = f.readlines()

    html = ""
    for line in lines:
        if "http" in line:
            formatted_line = "<a href='{0}'>{0}</a><br/>".format(line.strip())
        else:
            formatted_line = line.strip() + "<br/>"
        html += formatted_line

    return html
