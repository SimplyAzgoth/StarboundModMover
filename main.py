# Dynamic Starbound Mod Mover + Renamer
# Made by SimplyAzgoth
# https://steamcommunity.com/id/SimplyAzgoth/
import requests
import logging
import json
import sys
import os


# ----CONFIG----
sb_path: str = r"C:\Program Files (x86)\Steam\steamapps\common\Starbound"  # The directory of your starbound folder.
extensive_log: bool = False  # Toggle for certain logging that might make the log file thousands of lines long. (e.g. saying mod id at every stage while being loaded)
max_name_size: int = 90  # Max characters in filename, any extra are truncated. Extension is not included in this limit.
default_char: str = "_"  # The character to replace any forbidden windows characters with
remove_empty_mod_folders: bool = True  # Whether to remove *empty* folders from the workshop folder after moving mods
# ----END CONFIG----


sb_mods_path: str = os.path.join(sb_path, "mods")
sb_workshop_path: str = os.path.join(os.path.dirname(os.path.dirname(sb_path)), "workshop", "content", "211820")
api_url: str = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
logging.basicConfig(handlers=[logging.FileHandler(filename="log.txt", mode="w", encoding="utf-16")],
                    format="[%(levelname)s]: %(message)s",
                    level=logging.DEBUG)


class SBMod:
    def __init__(self,
                 mid: int,
                 main_content_path: str = None,
                 other_content_paths: list[str] = None) -> None:
        self.mid: int = mid
        self.main_content_path: str = main_content_path
        self.other_content_paths: list[str] = other_content_paths
        self.title: str = str(mid)

    def __str__(self):
        return f"SBMod {self.mid} {self.title}"

    def move_to_sb(self) -> None:
        # other_content_paths should be moved but conserve their name
        if self.main_content_path:
            os.rename(self.main_content_path, os.path.join(sb_mods_path, self.title + ".pak"))
        if self.other_content_paths:
            for cont in self.other_content_paths:
                os.rename(cont, os.path.join(sb_mods_path, os.path.basename(cont)))
        if remove_empty_mod_folders:
            try:
                os.rmdir(os.path.join(sb_workshop_path, str(self.mid)))
            except OSError as e:
                logging.warning(f"Couldn't remove dir '{os.path.join(sb_workshop_path, str(self.mid))}. Error: {e}'")


mod_id_map: dict[int, SBMod] = {}
api_data: dict[str, int] = {"itemcount": 0}

logging.info("Loading mods...")
print("Working, please wait!")
for mod_id in os.listdir(sb_workshop_path):
    if extensive_log:
        logging.info(f"Loading {mod_id}")
    mod_path: str = os.path.join(sb_workshop_path, mod_id)
    if not os.path.isdir(mod_path):
        continue
    content: list[str] = os.listdir(mod_path)

    # some validation
    if len(content) == 0:
        logging.warning(f"Empty mod folder: {mod_path}. Skipping this one.")
        continue
    try:
        mod_id = int(mod_id)
    except ValueError:
        logging.warning(f"Invalid mod folder name: '{mod_path}'. Skipping this one.")
        continue

    # adding to the api_dict
    api_data[f"publishedfileids[{api_data['itemcount']}]"] = mod_id
    api_data["itemcount"] += 1

    matches = [x for x in content if x in ("contents.pak", "content.pak")]
    if len(matches) > 0:
        for match in matches:
            content.remove(match)
        alt_content_paths: list[str] = [os.path.join(mod_path, x) for x in content if x.endswith(".pak")]
        mod_id_map[mod_id] = SBMod(mod_id, os.path.join(mod_path, matches[0]), alt_content_paths)
    else:
        alt_content_paths: list[str] = [os.path.join(mod_path, x) for x in content if x != ".DS_Store"]
        mod_id_map[mod_id] = SBMod(mod_id, other_content_paths=alt_content_paths)

logging.info("Finished loading mods")

# making the api call
logging.info(f"Making api call")
try:
    api_response_dict: dict = json.loads(requests.post(api_url, api_data).text)["response"]
except requests.ConnectionError as e:
    print("Errored while connecting to steam api. Check logs.")
    logging.critical(f"requests.ConnectionError -> Unable to connect to steam api -> {e}")
    sys.exit(1)
logging.info("Successfully called api")

# linking the names and parsing them to be valid for windows
trans = "".maketrans('/\\?%*:|"<>', "__________")
for mod in api_response_dict["publishedfiledetails"]:
    mod_id = int(mod["publishedfileid"])
    try:
        mod_id_map[mod_id].title = mod["title"].translate(trans)[0:max_name_size]
    except KeyError:
        logging.error(f"Couldn't get title for mod id: '{mod_id}'. Defaulting to its id for filename (if applicable)")

for mod in mod_id_map.values():
    mod.move_to_sb()

logging.info("Done!")
print("Done!")
