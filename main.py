import argparse
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

    if cl_arguments.get("list"):
        handler = SOURCE_TO_HANDLERS[source](source = source)
        handler.list_files()
