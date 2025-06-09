import json
import os

# Path to monster.json and monsters folder
json_path = "monster.json"
monsters_folder = "monsters"

# Load monster.json
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

missing_folders = []
extra_folders = []
missing_evolutions = []

# Get all pet names with ":" replaced by "_"
expected_folders = set(f"{monster['name'].replace(':', '_')}_dmc" for monster in data.get("monster", []))

# Get all known monster names for evolution validation
known_monsters = set(monster["name"] for monster in data.get("monster", []))

# Check missing folders
for folder_name in expected_folders:
    full_path = os.path.join(monsters_folder, folder_name)
    if not os.path.isdir(full_path):
        missing_folders.append(folder_name)

# Identify extra folders with no pet association
existing_folders = set(os.listdir(monsters_folder))
for folder in existing_folders:
    if folder not in expected_folders:
        extra_folders.append(folder)

# Validate evolution targets
for monster in data.get("monster", []):
    for evolution in monster.get("evolve", []):
        target_name = evolution["to"]
        if target_name not in known_monsters:
            missing_evolutions.append(target_name)

# Output results
if missing_folders:
    print("Missing folders for the following monsters:")
    for folder in missing_folders:
        print(f"- {folder}")
else:
    print("All monster folders are present.")

if extra_folders:
    print("\nFolders with no pet association:")
    for folder in extra_folders:
        print(f"- {folder}")
else:
    print("\nAll folders match known pets.")

if missing_evolutions:
    print("\nEvolution targets missing from monster.json:")
    for target in missing_evolutions:
        print(f"- {target}")
else:
    print("\nAll evolutions reference existing monsters.")