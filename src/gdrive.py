from common import CommonHandler
import requests


class GoogleDriveHandler(CommonHandler):

    API_HOST = "https://www.googleapis.com/drive/v2"
    LIST_FILES_URL = API_HOST + "/files"

    def __init__(self, source):
        super(GoogleDriveHandler, self).__init__(source)

        self.auth_token = self.auth_data.get("access_token")
        self.headers = {
            "Authorization" : "Bearer {0}".format(self.auth_token)
        }

    def list_files(self):
        response = requests.get(self.LIST_FILES_URL, headers = self.headers)

