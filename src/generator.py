# Fill a randomly selected template


import requests
import random
import glob
import os.path
import re
import logging
import argparse
import string

import markdown
from bs4 import BeautifulSoup

from src import cache


autocomplete_cache = cache.Cache()
autocomplete_cache.load()


def generate_content(type_):
	"""Generate a ramdonly selected date profile or love letter.
	Args:
		type_ (str): type of the content: date_profiles or love_letters. Should match the
			folder name of the template path.
	"""
	template = random.choice(glob.glob(f"data/{type_}/templates/*.md"))
	logging.info("Using %s", template)
	body = fill_template(template)

	# For date profiles add a title
	if type_ == "date_profiles":
		title = generate_title()
		text = f"#{title}#\n\n{body}"

	# For love letters add a signature with custom html container
	else:
		name = f"<p id='letter-signature'>{generate_name(first_only=True)}</p>"
		text = f"{body}\n\n{name}"

	#text = cache.cleanup_extra_whitespace(text)
	html =  markdown.markdown(text)
	template = os.path.basename(template)

	return {"html": html, "template": template}

def generate_random_profile():
	"""Generate a profile from randomly selected template."""
	profile = random.choice(glob.glob("data/date_profiles/templates/*.md"))
	logging.info("Using %s", profile)
	return fill_template(profile)

def fill_template(profile, suggest_rate=0.4):
	"""Given a path to profile template, generate an autocompleted profile.
	Args:
		profile (str): path to profile template to use
		suggest_rate (float): percentage of suggest templates to switch for suggestions.
	"""
	PATTERN = "\[(.*?)\]"

	with open(profile) as f:
		text = f.read()

	tokens = re.findall(PATTERN, text)
	k = int(len(tokens) * suggest_rate)
	tokens_to_replace = random.sample(tokens, k)

	for token in tokens:
		token_str =  f"[{token}]"
		if token in tokens_to_replace:
			prefix = token.split(";")[0]
			try:
				suggestion = f"**{random.choice(autocomplete_cache[prefix.lower()])}**"
				text = text.replace(token_str, suggestion)
			
			# The cache is not guaranteed to contain any matching suggestions,
			# use the orignal token instead.
			except IndexError as e:
				logging.info("No suggestion for: %s", prefix)
				clean_text = token.replace(";", " ").strip()
				text = text.replace(token_str, clean_text)

		# Replace unselected tokens with clean text
		else:
			clean_text = token.replace(";", " ").strip()
			text = text.replace(token_str, clean_text)
	
	return text

def generate_title():
	"""Generate a random title from title file. Autocomplete the title based on a coin flip
	(if applicable).
	"""
	with open("data/date_profiles/titles.txt") as f:
		titles = [title.strip() for title in f.readlines()]

	title = random.choice(titles)
	PATTERN = "\[(.*?)\]"
	tokens = re.findall(PATTERN, title)

	if tokens and random.random() < .5:
		token_str = random.choice(tokens)
		prefix = token_str.split(";")[0]
		suggestion = random.choice(autocomplete_cache[prefix.lower()])
		title = title.replace(token_str, suggestion)

	# Replace meta chracters
	title = title.replace(";", " ").strip()
	title = title.replace("[", "")
	title = title.replace("]", "")

	return string.capwords(title)

def generate_name(nfirst_names = 1, first_only = False):
	"""Use requests on http://www.behindthename.com/random/ to generate a name.
	Arg:
		nfirst_names (int): number first names the result should have
		first_only (boolean): whether only the first name should be returned
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


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--build-cache", action="store_true", help="Build a new autocomplete cache parsed from templates and upload to Cloud Storage Bucket")
	args = parser.parse_args()

	if args.build_cache:
		logging.info("Building new cache...")
		autocomplete_cache.build()
		autocomplete_cache.upload()

