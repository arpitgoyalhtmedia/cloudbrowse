import flask
import requests
import json
import os
import webbrowser
from main import SOURCE_TOKEN_PATHS
import uuid


app = flask.Flask(__name__)

CLIENT_ID = os.environ.get("CLIENT_ID")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
SCOPE = os.environ.get("SCOPE")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")


def create_credential_file(file_path, response_json):
    """
    Writes the credential file to the desired
    path. Consists of the token and other metadata
    required for getting the data from the cloud
    server.
    """
    try:
        with open(file_path, "w") as f:
            f.write(json.dumps(response_json))
        f.close()

        return True
    except Exception as exc:
        print repr(exc)

        return False

@app.route("/")
def index():
    """
    Initial index function view for the proper redirection
    to get token or use it from already present tokens
    """
    source = flask.request.args.get("src")

    return flask.redirect(flask.url_for("callback"))

@app.route("/callback")
def callback():
    """
    Callback function that takes in the code
    returned by google on user verification
    """
    if 'code' not in flask.request.args:
        auth_uri = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={0}&redirect_uri={1}&scope={2}".format(CLIENT_ID, REDIRECT_URI, SCOPE)
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get("code")
        data = {
            "code" : auth_code,
            "client_id" : CLIENT_ID,
            "client_secret" : CLIENT_SECRET,
            "redirect_uri" : REDIRECT_URI,
            "grant_type" : "authorization_code"
        }
        response = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
        file_path = SOURCE_TOKEN_PATHS['gdrive']
        credentials_created = create_credential_file(file_path, response.json())

        if credentials_created:
            return "We have received the authorization token. You may close the browser window now. We do not store any of your information."
        else:
            return "There was an error try authenticating with the --auth flag again"


if __name__ == '__main__':
    app.secret_key = str(uuid.uuid4())
    app.debug = False
    app.run(port = "9201")
