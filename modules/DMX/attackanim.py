import json

# Paths to your files
monster_file = "monster.json"
battle_file = "battle.json"
output_file = "battle_updated.json"

# Load monster data
with open(monster_file, "r", encoding="utf-8") as f:
    monster_data = json.load(f)

# Create a lookup by (name, version)
monster_lookup = {
    (m["name"], m["version"]): {
        "atk_main": m.get("atk_main", 0),
        "atk_alt": m.get("atk_alt", 0)
    }
    for m in monster_data["monster"]
}

# Load battle data
with open(battle_file, "r", encoding="utf-8") as f:
    battle_data = json.load(f)

# Update each enemy
for enemy in battle_data:
    key = (enemy["name"], enemy["version"])
    if key in monster_lookup:
        enemy["atk_main"] = monster_lookup[key]["atk_main"]
        enemy["atk_alt"] = monster_lookup[key]["atk_alt"]
    else:
        print(f"⚠️ No matching monster found for {key}")

# Save updated battle.json
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(battle_data, f, indent=2, ensure_ascii=False)

print("✅ Updated battle.json with atk_main and atk_alt.")
