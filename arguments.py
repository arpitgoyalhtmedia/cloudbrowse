ARGPARSE_ARGUMENTS = {
    "--src": {
        "required": True,
        "help": "source of the cloud...\ngdrive=>Google Drive\n" +
        "odrive=>Microsoft Onedrive",
        "choices": ["gdrive", "odrive"]
    },
    "--list": {
        "const": "list",
        "nargs": "?",
        "help": "lists the files in the cloud service",
    },
    "--auth": {
        "action": "store_true",
        "help": "process of authentication with particular service"
    },
}
