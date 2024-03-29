import config as paths
import json


def load_config():
    try:
        print("Loading Config:")
        with open(paths.config_path, "r") as json_file:
            try:
                paths.config = json.load(json_file)
            except json.JSONDecodeError:
                paths.config = []
                print("Error: JSON Decode Error, creating empty JSON file")
    except FileNotFoundError:
        with open(paths.config_path, "w") as json_file:
            json.dump({"TOKEN": "",
                       "CREATE_CHANNEL": None,
                       "VC_CATEGORY": None,
                       "PERMANENT_ROLES": [],
                       "MOD_ROLES": [],
                       "LOG_Channel": None,
                       "UNMODIFIABLE_CHANNEL": []}, json_file, indent=4)
            print("Error: JSON File not found, creating empty JSON file")

    # Print the loaded VCs
    if paths.voice_channel_owners:
        for item in paths.voice_channel_owners:
            print(item)

    print("Loading completed")


# Load the JSON file with the VCs
def load_vc():
    try:
        print("Loading permanent Voice Channels:")
        with open(paths.file_path, "r") as json_file:
            try:
                paths.voice_channel_owners = json.load(json_file)
            except json.JSONDecodeError:
                paths.voice_channel_owners = []
                print("Error: JSON Decode Error, creating empty JSON file")
    except FileNotFoundError:
        with open(paths.file_path, "w") as json_file:
            json.dump([], json_file)
            print("Error: JSON File not found, creating empty JSON file")

    # Print the loaded VCs
    if paths.voice_channel_owners:
        for item in paths.voice_channel_owners:
            print(item)

    print("Loading completed")


def load_blacklist():
    try:
        print("Loading Blacklist:")
        with open(paths.blacklist_path, "r") as json_file:
            try:
                paths.blacklist = json.load(json_file)
            except json.JSONDecodeError:
                paths.blacklist = []
                print("Error: JSON Decode Error, creating empty JSON file")
    except FileNotFoundError:
        with open(paths.blacklist_path, "w") as json_file:
            json.dump([], json_file)
            print("Error: JSON File not found, creating empty JSON file")

    # Print the loaded VCs
    if paths.blacklist:
        for item in paths.blacklist:
            print(item)

    print("Loading completed")
