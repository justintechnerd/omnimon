import json

def load_names_from_monster(monster_file):
    with open(monster_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {monster['name'] for monster in data.get('monster', [])}

def load_names_from_battle(battle_file):
    with open(battle_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {entry['name'] for entry in data}

def find_missing_battle_names(monster_file, battle_file):
    monster_names = load_names_from_monster(monster_file)
    battle_names = load_names_from_battle(battle_file)

    missing = sorted(battle_names - monster_names)
    if missing:
        print("Missing names in monster.json:")
        for name in missing:
            print(f"- {name}")
    else:
        print("✅ All battle names are present in monster.json.")

# Example usage:
find_missing_battle_names('monster.json', 'battle.json')