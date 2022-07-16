import argparse
from flask import Flask, render_template, jsonify, request, abort

from src import generator


app = Flask(__name__)


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/_generate")
def set_content():
	"""Callback to button generating new content."""
	# Only respond, if a custom header was set
	if "X-Button-Callback" in request.headers:
		type_ = request.args.get("type")
		content = generator.generate_content(type_)
		return content, 200

	abort(500, "Something went wrong!")

@app.route("/_refresh")
def refresh_suggeestion_cache():
	# Only respond to cron request from App Engine
	# (The X- headers are stripped by App Engine when they originate from external sources)
	# https://cloud.google.com/appengine/docs/flexible/nodejs/scheduling-jobs-with-cron-yaml
	if "X-Appengine-Cron" in request.headers:
		generator.autocomplete_cache.build()
		generator.autocomplete_cache.upload()
		return "OK", 200

	abort(500, "Something went wrong!")



if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--debug", action="store_true")
	args = parser.parse_args()

	app.run(debug=args.debug)