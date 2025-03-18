import pathlib
import re

from content_generator.env_config import FILE_ENUMERATE_PATTERN


BASE = pathlib.Path(__file__).resolve().parent.parent


def get_all_prefixes():
    """Get prefixes from all replacement metadata files.
    Return:
        dict: list of unique prefixes
    """
    letters = list(BASE.glob(f"data/love_letters/metadata/{FILE_ENUMERATE_PATTERN}.txt"))
    profiles = list(BASE.glob(f"data/date_profiles/metadata/{FILE_ENUMERATE_PATTERN}.txt"))
    path_to_titles = BASE / "data" / "date_profiles" / "titles.json"

    prefixes = []
    # get prefixes from replacement templates
    for file_ in letters + profiles:
        with open(file_) as f:
            extracts = [
                split_metadata_token(row)[0].lower()
                for row in f.readlines()
                if row.strip()
            ]
            prefixes.extend(extracts)

    # add title prefixes
    with open(path_to_titles) as f:
        extracts = [
            extract_tokens_from_brackets(row)[0].lower()
            for row in f.readlines()
            if row.strip() and ";" in row
        ]
        prefixes.extend(extracts)

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
        prefix;stub
    Split such a line into the two pieces
    """
    split = token.split(";")
    return split[0], split[1].strip()  # ensure no whitespace at the end of stub

def extract_tokens_from_brackets(line):
    """Extract the prefix part from a string with a [prefix;stub] pattern.
    Args:
        line (str): A string that may contain a "[prefix;stub]" pattern

    Returns:
        str: The extracted prefix
    """
    match = re.search(r'\[(.*?);(.*?)\]', line)
    if match:
        return match.group(1), match.group(2)

def format_sources_to_html():
    """Read list of sources from the SOURCES file and format as html.
    Returns:
        str: html formatted list of sources
    """
    path_to_sources = BASE / "data" / "SOURCES"

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
