import glob
import re
from unittest.mock import patch, mock_open

from src import generator


def test_template_syntax():
	"""Test there are no bracketed template strings in any generated profiles."""
	invalid_profiles = []
	PATTERN = "\[(.*?)\]"

	with patch("src.generator.autocomplete_cache") as mock_cache:
		mock_cache.__getitem__.return_value = ["foo"]
		for profile in glob.glob("data/date_profiles/templates/*.md") + glob.glob("data/love_letters/templates/*.md") + ["data/date_profiles/titles.txt"]:
			p = generator.fill_template(profile)

			if any(c in p for c in ("[", "]")):
				invalid_profiles.append(profile)


		# tokens = re.findall(PATTERN, p)

		# # If the were any token detected, store the template name
		# if tokens != []:
		# 	invalid_profiles.append(profile)

	assert invalid_profiles == []

@patch(
	"builtins.open",
	new_callable=mock_open,
	read_data="It's one of the [three worst;wurst companies]. Every decision made [is a;decision made]. Sometimes they will [come;]."
)
def test_template_fill(mock_open):
	"""Does template fill produce expected outcome?"""
	# Generate a profile based on a fixed cache and suggest_rate of 1 to ensure all items are used.
	mock_cache_data = {"three worst": "A", "is a": "B", "come": "C"}
	with patch.object(generator.autocomplete_cache, "data", mock_cache_data):
		p = generator.fill_template("dummy_profile.md", 1)

	assert p == "It's one of the **A**. Every decision made **B**. Sometimes they will **C**."


@patch("src.generator.autocomplete_cache")
@patch(
	"builtins.open",
	new_callable=mock_open,
	read_data="[It's one of;the three] worst wurst companies. Every decision made is a one for the future. [Sometimes things;don't happen]."
)
def test_cache_lowercasing(mock_open, mock_cache):
	"""Is the cache queried using lowercase keys?"""
	mock_cache_data = {"it's one of": "A", "sometimes things": "B"}
	with patch.object(generator.autocomplete_cache, "data", mock_cache_data):
		generator.fill_template("dummy_profile.md", 1)

	mock_cache.__getitem__.assert_any_call("it's one of")
	mock_cache.__getitem__.assert_any_call("sometimes things")

@patch("random.random")
@patch("src.generator.autocomplete_cache")
@patch(
	"builtins.open",
	new_callable=mock_open,
	read_data="he who hesitates is [a Damn;Fool]"
)
def test_title_creation(mock_open, mock_cache, mock_random):
	"""Is title queries with lowercase key?"""
	mock_cache_data = {"a damn": "common enemy"}
	mock_cache.__getitem__.return_value = ["a common enemy"] # needed to avoid returning a Mock as an intermediary result
	mock_random.return_value = 0 # Ensure cache the is used
	with patch.object(generator.autocomplete_cache, "data", mock_cache_data):
		title = generator.generate_title()

	mock_cache.__getitem__.assert_called_with("a damn")
	assert title == "He Who Hesitates Is A Common Enemy" 
