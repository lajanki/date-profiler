import os.path
import json
import glob
import re
import logging

from google.cloud import storage

from src import utils



ENV = os.getenv("ENV", "dev")
BUCKET = f"{ENV}_date_profiler_data"
PATH = "autocomplete_cache.json"
TEMPLATES =\
	glob.glob("data/date_profiles/templates/*.md") +\
	glob.glob("data/love_letters/templates/*.md") +\
	["data/date_profiles/titles.txt"]


class Cache:

	def __init__(self):
		self.data = {}
		self.gcs_client = storage.Client()

	def __getitem__(self, item):
		return self.data.get(item)

	def build(self):
		"""Build the cache: fetch autocomplete suggestions for each key in profile templates."""
		PARTTERN = "\[(.*?)\]"
		keys = []

		for profile in TEMPLATES:
			with open(profile) as f:
				text = f.read()

			tokens = re.findall(PARTTERN, text)
			keys.extend([t.split(";")[0].lower() for t in tokens])
		
		self.data = dict.fromkeys(keys)
		logging.info("Detected %s distinct prefixes", len(self.data))

		# Get suggestions for each key
		for key in self.data:
			suggestions = self.clean(utils.get_suggestions(key))
			self.data[key] = suggestions

		logging.info("Done")
		
	def upload(self):
		"""Upload cache to the gcs bucket"""
		bucket = self.gcs_client.get_bucket(BUCKET)
		blob = bucket.blob(PATH)
		blob.upload_from_string(json.dumps(self.data))

	def download(self):
		"""Download the cache file and parse as a dict"""
		bucket = self.gcs_client.get_bucket(BUCKET)
		blob = bucket.get_blob(PATH)
		cache_string = blob.download_as_text()
		return json.loads(cache_string)

	def load(self):
		"""Fetch cache from gsc and set it as the current cache"""
		self.data = self.download()

	def clean(self, suggestions):
		"""Many autocomplete suggestions are queries for movies, song lyrics and other specific
		items. eg. "forever yours => forever yours song".
		Remove selected keywords from a suggestions returned by the API.
		Args:
			suggestions (list): list of suggestions
		"""
		# TODO season 7 etc
		keywords = [
			"app",
			"cast",
			"chords",
			"definition",
			"episode",
			"essay",
			"gif",
			"imdb",
			"latin",
			"lyrics",
			"meaning",
			"meme",
			"movie",
			"mp3",
			"pdf",
			"quotes",
			"reddit",
			"song",
			"story",
			"synonym"
		]

		clean_suggestions = []
		for suggestion in suggestions:
			split = suggestion.split()
			clean_words = [w for w in split if not any([k in w for k in keywords])]
			clean = " ".join(clean_words)
			clean_suggestions.append(clean)

		# drop possible duplicated resulting from cleanup
		return list(set(clean_suggestions))

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



def format_sources_to_html():
    """Get list of sources from the SOURCES file and format as html."""
    with open("data/SOURCES") as f:
        lines = f.readlines()

    html = ""
    for line in lines:
        if "http" in line:
            formatted_line = "<a href='{0}'>{0}</a><br/>".format(line.strip())
        else:
            formatted_line = line.strip() + "<br/>"
        html += formatted_line

    return html
