from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


gauth = GoogleAuth(settings_file = "/home/arpitgoyal/projects/cloudbrowse/client_secrets.json")
#gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:
      print('title: %s, id: %s' % (file1['title'], file1['id']))
