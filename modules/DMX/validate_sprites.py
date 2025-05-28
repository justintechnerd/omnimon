import json
import os

# Path to your monster.json and monsters folder
json_path = "monster.json"
monsters_folder = "monsters"

# Load monster.json
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

missing_folders = []

# Check each monster name
for monster in data.get("monster", []):
    name = monster["name"]
    folder_name = f"{name}_dmc"
    full_path = os.path.join(monsters_folder, folder_name)
    if not os.path.isdir(full_path):
        missing_folders.append(name)

# Output results
if missing_folders:
    print("Missing folders for the following monsters:")
    for name in missing_folders:
        print(f"- {name}")
else:
    print("All monster folders are present.")
