class CommonHandler(object):

    def __init__(self, source):
        auth_file_path = SOURCE_TOKEN_PATHS[source]
        self.auth_data = json.loads(open(auth_file_path, "r"))

    def list_files(self):
        pass
