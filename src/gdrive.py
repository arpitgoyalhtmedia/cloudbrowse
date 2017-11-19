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

    def get_files(self, items=None):
        """
        divide the root items into folder and files
        """
        all_files = []

        if not items:
            items = self.get_root_files()

        for item in items:
            if item.get("labels").get("trashed"):
                continue
            all_files.append(item)

        return all_files

    def get_display_data(self, data):
        """
        this function returns the data as an array
        of dicts which will then be used to display
        the console output
        """

        console_data = []

        for datum in data:
            file_type = "folder" if datum.get("mimeType") == \
                "application/vnd.google-apps.folder" else "file"
            console_data.append({
                "id": datum.get("id"),
                "title": datum.get("title"),
                "created_date": datum.get("createdDate"),
                "file_size": self.convert_size(datum.get("fileSize")),
                "file_type": file_type
            })

        return console_data


class GoogleDriveHandler(CommonHandler):

    API_HOST = "https://www.googleapis.com/drive/v2"
    LIST_FILES_URL = API_HOST + "/files"
    GET_FILES_DATA_URL = API_HOST + "/files/{fileId}"
    LIST_FOLDER_FILES_URL = API_HOST + "/files/{folderId}/children"

    def __init__(self, source):
        super(GoogleDriveHandler, self).__init__(source)

        self.auth_token = self.auth_data.get("access_token")
        self.headers = {
            "Authorization": "Bearer {0}".format(self.auth_token)
        }

    def convert_for_texttable(self, data):
        """
        converts the data in the format as supported by texttype
        """
        texttable_data = [[
            "id", "title", "created_date", "file_size",
            "file_type"
        ]]

        for datum in data:
            resetable_array = []
            for key in texttable_data[0]:
                resetable_array.append(datum.get(key))
            texttable_data.append(resetable_array)

        return texttable_data

    def draw_texttable(self, texttable_data):
        """
        draws the text table with a particular dataset
        provided
        """
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(["c", "c", "c", "c", "c"])
        table.set_cols_width([60, 50, 30, 10, 10])
        table.add_rows(texttable_data)

        print table.draw()

    def get_file_data(self, file_id):
        """
        gets the file details by id
        """
        URL = self.GET_FILES_DATA_URL.format(**{"fileId": file_id})
        response = requests.get(URL, headers=self.headers)

        return response.json()

    def list_files(self):
        """
        lists the file and prints in the console
        """
        response = requests.get(
            self.LIST_FILES_URL, headers=self.headers)

        parser = GoogleDriveDataParser(response_data=response.json())

        root_items = parser.get_root_files()
        display_data_root = parser.get_display_data(root_items)
        texttable_data = self.convert_for_texttable(display_data_root)

        self.draw_texttable(texttable_data)

    def get_folder_files(self, folder_id):
        """
        lists the files inside a particular folder
        """
        URL = self.LIST_FOLDER_FILES_URL.format(**{'folderId': folder_id})
        response = requests.get(URL, headers=self.headers)
        parser = GoogleDriveDataParser(response_data=response.json())

        all_file_data = map(
            lambda f: self.get_file_data(f.get("id")),
            response.json().get("items")
        )

        all_files = parser.get_files(all_file_data)
        display_data = parser.get_display_data(all_files)
        texttable_data = self.convert_for_texttable(display_data)

        self.draw_texttable(texttable_data)
