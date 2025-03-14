# A collection of maintenance related helper functions with a runnable entrypoint.


import json
import glob
import os.path
import argparse

import pprint
from termcolor import colored

from content_generator import utils


letter_metadata = glob.glob("data/love_letters/metadata/*.txt")
letters = glob.glob("data/love_letters/letters/*.md")
profiles_metadata = glob.glob("data/date_profiles/metadata/*.txt")
profiles = glob.glob("data/date_profiles/letters/*.md")


def find_invalid(template):
	"""Find invalid entries in the metadata file for a given letter template:
	 * entries where prefix + blank is not in the template
	 * entries containing the delimiter character ; in either the prefix or blank
	Arg:
		template (string): path to template file
	"""
	with open(template) as f:
		text = f.read()

	# open metadata file based on template filename
	name = os.path.basename(template)
	name = os.path.splitext(name)[0]

	template_folder = os.path.dirname(template)
	metadata_file = os.path.join(template_folder, "..", "metadata", name+".txt")

	with open(metadata_file) as f:
		metadata = [row for row in f.readlines() if row.strip()]  # exclude empty rows
		metadata = list(map(str.rstrip, metadata))

	DELIMITER = ";"
	invalid = []
	for token in metadata:
		# does the token contain the delimiter character?
		if DELIMITER not in token:
			invalid.append(token)
			continue

		prefix, blank = utils.split_metadata_token(token)
		substr = "{} {}".format(prefix, blank).strip()  # blank may be empty, in that case strip the extra whitespace

		if substr not in text or DELIMITER in prefix or DELIMITER in blank:
			invalid.append(token)

	if invalid:
		print(os.path.basename(template))
		print("Found the following invalid entries:")
		pprint.pprint(invalid)

def find_invalid_titles():
	"""Find entries in titles.json with prefix + blank not in title."""
	path_to_titles = "data/date_profiles/titles.json"
	with open(path_to_titles) as f:
		titles = json.load(f)

	invalid = []
	for token in titles["title"]:
		substr = "{} {}".format(token["prefix"], token["blank"]).strip()
		if not substr in token["title"] and substr != " ":
			invalid.append(token)

	if invalid:
		print("Found the following invalid titles:")
		pprint.pprint(invalid)

def show_template_prefixes(category="all"):
	"""Print a colored visualization of each letter and profile template with
	prefixes highlighted in red similar to grep.
	"""
	# TODO: how to handle overlapping prefixes
	def parse_ordinal(filename):
		"""Custom key function for sorting the list of metadata and letter files:
		parses the numerical value from the filename to an int.
		eg. date_profile14.md -> 14
		The default, alphabetical sort would not keep 1 and 2 digit numbers in order.
		"""
		digits = [c for c in filename if c.isdigit()]
		return int("".join(digits))
		
	# Sort the files lists, so they're iterated in the same order
	letter_metadata.sort(key=lambda name: parse_ordinal(name))
	letters.sort(key=lambda name: parse_ordinal(name))
	profiles_metadata.sort(key=lambda name: parse_ordinal(name))
	profiles.sort(key=lambda name: parse_ordinal(name))

	# Setup template and metadata files to iterate based on the category input
	metadata_files = letter_metadata + profiles_metadata
	template_files = letters + profiles

	if category == "date_profiles":
		metadata_files = profiles_metadata
		template_files = profiles

	elif category == "love_letters":
		metadata_files = letter_metadata
		template = letters

	for idx, metadata_file in enumerate(metadata_files):
		prefixes = []
		with open(metadata_file) as f:
			metadata = [row for row in f.readlines() if row.strip()]
			metadata = list(map(str.rstrip, metadata))

			for token in metadata:
				prefix, _ = utils.split_metadata_token(token)
				prefixes.append(prefix)

		prefixes = list(set(prefixes))

		# read the corresponding template file
		with open(template_files[idx]) as f:
			template = f.read()

		for prefix in prefixes:
			colored_prefix = colored(prefix, "red")
			template = template.replace(prefix, colored_prefix)

		# print the result
		name = os.path.basename(template_files[idx])
		print(name)
		print(template)
		print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--find-invalids",
        action="store_true",
        help="Display metadata content with no match in the templates",
    )
    parser.add_argument(
        "--show-prefixes",
        choices=["all", "date_profiles", "love_letters"],
        metavar="category",
        help="Highlight prefixes in each template similar to grep.",
    )
    args = parser.parse_args()

    if args.find_invalids:
        date_profiles = glob.glob(os.path.join("data", "date_profiles", "letters", "*.md"))
        love_letters = glob.glob(os.path.join("data", "love_letters", "letters", "*.md")) 

        for template in date_profiles + love_letters:
            find_invalid(template)

        find_invalid_titles()

    elif args.show_prefixes:
        show_template_prefixes(args.show_prefixes)
