# Fills date profile and love letter templates in data/ with random Google Search's autocomplete suggestions.
# Valid query strings to pass to the autocomplete API are stored in json files in the metadata directory.


import requests
import random
import json

import simplejson as json
import markdown
from bs4 import BeautifulSoup
from pathlib import Path

from content_generator import utils, gcs_utils


autocomplete_cache = gcs_utils.get_cached_autocomplete_suggestions()
SUGGEST_URL = "http://suggestqueries.google.com/complete/search"


def generate_letter(type_):
	"""Conveniance wrapper to fill_template: generates an autocompleted,
	randomly selected, date profile or love letter.
	Args:
		type_ (str): type of content to generate either "date_profile" or "love_letter"
	Returns:
		dict: a dictionary containing the generated content as html and the template file used.
	"""
	if type_ == "date_profile":
		profiles = list(Path("data/date_profiles/letters").glob("*.md"))
		template = random.choice(profiles)
		body = fill_template(template)

		# Date profiles should have titles
		title = generate_title()

		text = "#{}#\n\n{}".format(title, body)

	else:
		profiles = list(Path("data/love_letters/letters").glob("*.md"))
		template = random.choice(profiles)
		body = fill_template(template)

		# Letters templates already contain titles, instead
		# love letters should contain a signiture.
		name = generate_name(first_only=True)
		name = "<p id='letter-signiture'>{}</p>".format(name)

		text = "{}\n\n{}".format(body, name)

	text = utils.cleanup_extra_whitespace(text)
	html = markdown.markdown(text.strip())
	template = template.name

	return {"html": html, "template": template}

def fill_template(template, splice_percentage=0.85):
	"""Fill a templated date profile or love letter. Chooses a random number of tokens
	in the corresponding metadata file and fills the original template with autocompleted
	results.
	Args:
		template (str): path to template file
		splice_percentage (float): percentage of valid queries to pass to autocomplete
	Returns:
		str: the filled template
	"""
	with open(template) as f:
		text = f.read()

	# read the matching metadata file
	name = template.stem  # filename without extension

	template_folder = template.parent
	metadata_file = template_folder / ".." / "metadata" / f"{name}.txt"

	with open(metadata_file) as f:
		metadata = [row for row in f.readlines() if row.strip()]
		metadata = list(map(str.rstrip, metadata))

	# randomly choose which tokens in metadata to switch
	n = int(splice_percentage * len(metadata))
	query_tokens = random.sample(metadata, n)
	
	for token in query_tokens:
		 # Tokens are lines of the form "prefix;blank" where prefix is passed to the API
		 # and the result is used to overwrite the original prefix + blank.
		prefix, blank = utils.split_metadata_token(token)

		# cache keys are lowercase (autocomplete is case insensitive)
		prefix = prefix.lower()
		autocomplete_choices = autocomplete_cache[prefix]
		if autocomplete_choices:
			new = random.choice(autocomplete_choices)
			new = utils.clean_autocomplete_suggestion(new)

			# Cleanup may have lead to the chosen suggestion being the same as the original,
			# if so, skip to the next token.
			if new.lower().strip() == prefix.strip():
				continue

			# Check if first word of autocompleted result should be capitalized
			if prefix == prefix.capitalize():
				new = new.capitalize()

			# Replace the full token with the autocompleted result
			old = "{} {}".format(prefix, blank).strip()  # blank may be empty, in that case strip the extra whitespace

			# Set markdown bolding for the replacing autocomplete suggestion
			new = "**{}**".format(new)
			text = text.replace(old, new, 1) # in case there are many, replace only the first instance

	return text

def get_autocomplete_suggestions(prefixes):
	"""Get autocomplete suggestions for a list of query strings.
	Args:
		prefixes (list): list of strings to get autocomplete suggestions for
	Returns:
		dict: a mapping of the query strings and the returned suggestions.
	"""
	print("Refreshing cache file with {} prefixes".format(len(prefixes)))
	totals = {}
	for p in prefixes:
		# Add a space to ensure the prefixes is fully contained in the resulting suggestions,
		# ie. "I love to" will also result in suggestions such as "I love you",
		# Whereas "I love to " keeps to orignal prefix in the response.
		q = p + " " 
		r = requests.get(SUGGEST_URL, params={"client":"firefox", "q":q})

		# The first item in the response is the original query string, second is a list of suggestions.
		totals[p] = r.json()[1]  
								 
	return totals

def refresh_and_upload_cache():
	"""Refresh the suggestion cache and upload to Cloud Storage."""
	prefixes = utils.get_all_prefixes()
	suggestion_cache = get_autocomplete_suggestions(prefixes)
	gcs_utils.upload_autocomplete_cache(suggestion_cache)

def generate_title():
	"""Generate a random title from the title file.
	Title can either be an original title or a title
	with autocompleted terms.
	Returns:
		str: the generated title
	"""
	path_to_titles = Path(utils.BASE) / "data" / "date_profiles" / "titles.json"
	with open(path_to_titles) as f:
		titles = json.load(f)

	token = random.choice(titles["title"])

	# Randomly choose to either an existing orignal title or autocomplete it
	if random.random() <= 0.7 and token["prefix"]:
		query_string = token["prefix"].lower()
		autocomplete_choices = autocomplete_cache[query_string]
		new = random.choice(autocomplete_choices)
		new = utils.clean_autocomplete_suggestion(new)
		old = "{} {}".format(token["prefix"], token["blank"])

		title = token["title"].replace(old, new)
	else:
		title = token["title"]

	capitalized = title.title()
	# The str.title method also capitalizes any character after a single quote '.
	# Manually fix these by cheking if the previous character was asingle quote:
	chars = []
	for i, char in enumerate(capitalized):
		if i > 0 and capitalized[i-1] in ("'", "`"):
			chars.append(char.lower()) 
		else:
			chars.append(char)

	title = "".join(chars)

	return title

def generate_name(nfirst_names=1, first_only=False):
	"""Generate a random naming from behindthename.com.
	Arg:
		nfirst_names (int): number first names the result should have
		first_only (boolean): whether only the first name should be returned
	Returns:
		str: the generated name
	"""

	# set name parameters,
	# first + middle + surname
	name_params = {
		"number":nfirst_names,
		"gender":"both",
		"randomsurname":"yes",
		"all":"no",
		"usage_chi":1,
		"usage_dan":1,
		"usage_dut":1,
		"usage_end":1,
		"usage_est":1,
		"usage_get":1,
		"usage_hun":1,
		"usage_ind":1,
		"usage_ita":1,
		"usage_jew":1,
		"usage_nor":1,
		"usage_per":1,
		"usage_rus":1,
		"usage_spa":1
	}
	if first_only:
		name_params["randomsurname"] = ""
	r = requests.get("http://www.behindthename.com/random/random.php", params=name_params)

	soup = BeautifulSoup(r.text, "html.parser")
	names = [a.text for a in soup.find_all("a", class_="plain")]
	return " ".join(names)

