import argparse
import json
import os
import webbrowser
import sys
from src import GoogleDriveHandler
from src.constants import *


SOURCE_TO_HANDLERS = {
    "gdrive" : GoogleDriveHandler
}


def process_token_generation(source):
    """
    Processes the token generation process
    using browser windows and user authentication
    processes
    """

    print "Opening web browser for authenticating with {0}".format(SOURCE_CODES_TO_NAMES[source])
    #Browser window opening and closing needs better enhancements to support multiple platform
    webbrowser.open("http://localhost:9201?src={0}".format(source), new = 2)


def refresh_auth_token(source):
    """
    refreshes the auth token if the token has expired
    """
    import time
    import requests

    token_path = SOURCE_TOKEN_PATHS[source]
    data = json.loads(open(token_path, "r").read())
    current_unix_time = time.time()
    file_last_modified = os.path.getmtime(token_path)

    if not (current_unix_time - file_last_modified > data.get("expires_in")):
        return

    post_data = {
        "client_id" : os.environ.get("CLIENT_ID"),
        "client_secret" : os.environ.get("CLIENT_SECRET"),
        "refresh_token" : data.get("refresh_token"),
        "grant_type" : "refresh_token"
    }

    response = requests.post("https://www.googleapis.com/oauth2/v4/token", post_data)
    response_content = response.json()
    response_content.update({"refresh_token" : data.get("refresh_token")})

    with open(token_path, "w") as f:
        f.write(json.dumps(response_content))

    f.close()


if __name__ == '__main__':
    """
    Main function which parses the arguments provided
    in the command line.
    """
    if not os.path.exists(CREDENTIALS_DIRECTORY):
        os.makedirs(CREDENTIALS_DIRECTORY)

    parser = argparse.ArgumentParser(description="Argument parser for the command line utility of cloudbrowse to \
                                     browse through the cloud files.")
    parser.add_argument('--src', required = True, help = 'source of the cloud.. supported values are: \n gdrive = Google Drive\n odrive = Microsoft OneDrive\n')
    parser.add_argument('-l', '--list', action='store_true', help = 'lists the files in the cloud service')
    parser.add_argument('--auth', action='store_true', help= 'process of authentication with a particular service')
    cl_arguments = vars(parser.parse_args())
    source = cl_arguments.get("src")

    if cl_arguments.get("auth"):
        process_token_generation(source)
        sys.exit()

    if not os.path.exists(SOURCE_TOKEN_PATHS[source]):
        parser.error("\nYou have not authenticated with {0}\n\nRun the following command to authenticate\n\ncloudbrowse --src {1} --auth".format(SOURCE_CODES_TO_NAMES[source], source))
        sys.exit()

    refresh_auth_token(source)

    if cl_arguments.get("list"):
        handler = SOURCE_TO_HANDLERS[source](source = source)
        handler.list_files()
