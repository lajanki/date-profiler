import os.path
import json
import glob



BASE = os.path.join(os.path.dirname(__file__), "..")


def get_all_prefixes():
    """Get prefixes from all metadata files.
    Return:
        dict: list of prefixes
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

    return list(set(prefixes))

def clean_autocomplete_suggestion(suggestion):
    """Remove selected keywords from autocomplete suggestions.
    Autocomplete suggestions often include query terms for movies,
    song lyrics and other popular search terms.
    Args:
        suggestion (str): raw autocomplete suggestion
    Returns:
        str: cleaned suggestion
    """
    # TODO include multipart terms such as season 7, etc.
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
    """Metadata files in data/love_letters/metadata and data/date_profiles/metadata
    consist of ";" delimited lines of the form
        prefix;blank
    Split such a line into the two pieces
    """
    split = token.split(";")
    return split[0], split[1].strip()  # ensure no whitespace at the end of blank

def format_sources_to_html():
    """Read list of sources from the SOURCES file and format as html.
    Returns:
        str: html formatted list of sources
    """
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
