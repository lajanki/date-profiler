import json
import os

from google.cloud import storage
from dotenv import load_dotenv


# Load default GCS bucket from .env
# Does not overwrite if already set.
load_dotenv(".dev.env")


def get_cached_autocomplete_suggestions():
	"""Fetch curremt autocomplete suggestion results from 
    the Cloud Storage cache file.
    Return:
        dict: JSON object of autocomplete suggestions
    """
	client = storage.Client()
	bucket = client.get_bucket(os.environ["GCS_BUCKET"])
	blob = bucket.get_blob(os.environ["GCS_CACHE_FILE"])
	cache_string = blob.download_as_string()
	cache = json.loads(cache_string)

	return cache

def upload_autocomplete_cache(cache):
    """Upload new autocomplete cache to Cloud Storage.
    Replaces existing files.
    Args:
        cache (dict): JSON object of autocomplete suggestions to upload
    """
    client = storage.Client()
    bucket = client.get_bucket(os.environ["GCS_BUCKET"])
    blob = bucket.get_blob(os.environ["GCS_CACHE_FILE"])
    blob.upload_from_string(json.dumps(cache))

