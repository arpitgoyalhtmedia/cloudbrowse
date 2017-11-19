import os

SOURCE_CODES_TO_NAMES = {
    "gdrive": "Google Drive",
    "odrive": "One Drive"
}

CURRENT_WORKING_DIRECTORY = os.getcwd()
BASE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_DIRECTORY = os.path.join(BASE_DIRECTORY, ".credentials")

SOURCE_TOKEN_PATHS = {
    "gdrive": os.path.join(CREDENTIALS_DIRECTORY, "gdrive.cred"),
    "odrive": os.path.join(CREDENTIALS_DIRECTORY, "odrive.cred")
}
