import argparse
import json
import os
import webbrowser
import sys
from src import GoogleDriveHandler
from arguments import ARGPARSE_ARGUMENTS
from src.constants import SOURCE_CODES_TO_NAMES, \
        CREDENTIALS_DIRECTORY, SOURCE_TOKEN_PATHS


SOURCE_TO_HANDLERS = {
    "gdrive": GoogleDriveHandler
}


def process_token_generation(source):
    """
    Processes the token generation process
    using browser windows and user authentication
    processes
    """

    print "Opening web browser for authenticating with {0}".format(
        SOURCE_CODES_TO_NAMES[source])
    # Browser window opening and closing needs better
    # enhancements to support multiple platform
    webbrowser.open(
        "http://localhost:9201?src={0}".format(source),
        new=2
    )


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
        "client_id": os.environ.get("CLIENT_ID"),
        "client_secret": os.environ.get("CLIENT_SECRET"),
        "refresh_token": data.get("refresh_token"),
        "grant_type": "refresh_token"
    }

    response = requests.post(
        "https://www.googleapis.com/oauth2/v4/token", post_data)
    response_content = response.json()
    response_content.update({
        "refresh_token": data.get("refresh_token")
    })

    with open(token_path, "w") as f:
        f.write(json.dumps(response_content))

    f.close()


def _create_required_folders():
    """
    creates the required folders in application startup
    """
    if not os.path.exists(CREDENTIALS_DIRECTORY):
        os.makedirs(CREDENTIALS_DIRECTORY)


def _create_argument_parser():
    """
    loads the argument parser
    """
    parser = argparse.ArgumentParser(
        description="Argument parser for the command line utility of" +
        "cloudbrowse to browse through the cloud files."
    )

    for argument, argument_values in ARGPARSE_ARGUMENTS.iteritems():
        parser.add_argument(argument, **argument_values)

    cl_arguments = vars(parser.parse_args())
    source = cl_arguments.get("src")

    if cl_arguments.get("auth"):
        process_token_generation(source)
        sys.exit()

    if not os.path.exists(SOURCE_TOKEN_PATHS[source]):
        parser.error(
            "\nYou have not authenticated with {0}\n\n".format(
                SOURCE_CODES_TO_NAMES[source]) +
            " Run the following command to authenticate\n\ncloudbrowse" +
            "--src {1} --auth".format(source)
        )
        sys.exit()

    refresh_auth_token(source)

    if cl_arguments.get("list") == "list":
        handler = SOURCE_TO_HANDLERS[source](source=source)
        handler.list_files()
    else:
        handler = SOURCE_TO_HANDLERS[source](source=source)
        handler.get_folder_files(cl_arguments.get("list"))


if __name__ == '__main__':
    """
    Main function which parses the arguments provided
    in the command line.
    """

    """
    create folders
    """

    _create_required_folders()

    """
    load parser arguments
    """

    _create_argument_parser()
