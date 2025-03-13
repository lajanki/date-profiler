from flask import (
    Flask,
    render_template,
    request,
    abort
)

from content_generator import autocomplete, utils


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/_generate")
def generate_game_description():
    # Only respond, if a custom header was set
    if "X-Button-Callback" in request.headers:
        type_ = request.args.get("type")
        data = autocomplete.generate_letter(type_)
        return data, 200

    abort(500)

@app.route("/_refresh")
def refresh_suggestion_cache():
    # Only respond to cron request from App Engine
    # (The X- headers are stripped by App Engine when they originate from external sources)
    # https://cloud.google.com/appengine/docs/flexible/nodejs/scheduling-jobs-with-cron-yaml
    if "X-Appengine-Cron" in request.headers:
        utils.refresh_and_upload_cache()
        return "OK", 200

    abort(500)
