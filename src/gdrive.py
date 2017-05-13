from common import CommonHandler
import requests
from texttable import Texttable
import math


class GoogleDriveDataParser(object):
    """
    parses the data and helps in displaying as needed
    in the command shell
    """

    def __init__(self, response_data):
        self.file_list = response_data
        self.items = self.file_list.get("items")

    def convert_size(self, size_bytes):
        if size_bytes in [0, "", None]:
            return "0B"
        print size_bytes

        size_bytes = float(size_bytes)
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)

        return "%s %s" % (s, size_name[i])

    def get_root_files(self):
        """
        gets all the root items present in the drive
        """

        root_items = []

        for item in self.items:
            if item.get("labels").get("trashed"):
                continue
            for parent in item.get("parents"):
                if parent.get("isRoot"):
                    root_items.append(item)

        return root_items

    def get_root_folders_and_files(self):
        """
        divide the root items into folder and files
        """
        all_root_folders = []; all_root_files = []
        root_items = self.get_root_files()

        for item in root_items:
            if item.get("mimeType") == 'application/vnd.google-apps.folder':
                all_root_folders.append(item)
            else:
                all_root_files.append(item)

        return all_root_folders, all_root_files

    def get_display_data(self, data):
        """
        this function returns the data as an array
        of dicts which will then be used to display
        the console output
        """

        console_data = []

        for datum in data:
            file_type = "folder" if datum.get("mimeType")=="application/vnd.google-apps.folder" else "file"
            console_data.append({
                "id" : datum.get("id"),
                "title" : datum.get("title"),
                "created_date" : datum.get("createdDate"),
                "file_size" : self.convert_size(datum.get("fileSize")),
                "file_type" : file_type
            })

        return console_data


class GoogleDriveHandler(CommonHandler):

    API_HOST = "https://www.googleapis.com/drive/v2"
    LIST_FILES_URL = API_HOST + "/files"
    LIST_FOLDER_FILES_URL = API_HOST + "/files/{folderId}/children"

    def __init__(self, source):
        super(GoogleDriveHandler, self).__init__(source)

        self.auth_token = self.auth_data.get("access_token")
        self.headers = {
            "Authorization" : "Bearer {0}".format(self.auth_token)
        }

    def convert_for_texttable(self, data):
        """
        converts the data in the format as supported by texttype
        """
        texttable_data = [["id", "title", "created_date", "file_size", "file_type"]]

        for datum in data:
            resetable_array = []
            for key in texttable_data[0]:
                resetable_array.append(datum.get(key))
            texttable_data.append(resetable_array)

        return texttable_data

    def list_files(self):
        """
        lists the file and prints in the console
        """
        response = requests.get(self.LIST_FILES_URL, headers = self.headers)

        parser = GoogleDriveDataParser(response_data = response.json())

        root_items = parser.get_root_files()
        display_data_root = parser.get_display_data(root_items)
        texttable_data = self.convert_for_texttable(display_data_root)

        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["c", "c", "c", "c", "c"])
        table.set_cols_width([60, 50, 30, 10, 10])
        table.add_rows(texttable_data)

        print table.draw()
