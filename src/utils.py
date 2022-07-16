import requests

def get_suggestions(query):
	"""Get a suggestion to a query from Google Search."""
	# https://stackoverflow.com/questions/6428502/google-search-autocomplete-api
	URL = "http://suggestqueries.google.com/complete/search"

	# Add a space to ensure the prefixes is fully contained in the resulting suggestions,
	# eg. "I love to" will also suggest related search terms such as "I love you".
	# postfixing a white string results in suggestions with the original query.
	q = query + " " 
	r = requests.get(URL, params={"client":"firefox", "hl":"en", "q":q})
	r.raise_for_status()
	
	return r.json()[1]
