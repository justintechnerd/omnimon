import csv
import json

def attribute_mapping(code):
    return {
        "0": "",
        "1": "Vi",
        "2": "Da",
        "3": "Va"
    }.get(code.strip(), "")

def parse_csv_to_json(csv_path, json_path):
    monsters = {}

    with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:  # <- 'utf-8-sig' remove BOM
        reader = csv.reader(csvfile, delimiter=';')
        headers = [h.strip() for h in next(reader)]  # Limpa cabeçalhos
        for row in reader:
            row_dict = dict(zip(headers, row))
            stage = int(row_dict["Stage"]) + 1
            monster_id = row_dict["ID"].strip()
            monster_data = {
                "name": monster_id,
                "stage": stage,
                "version": 2,
                "special": False if int(row_dict["DefaultAlbumOpen"]) == 1 else True,
                "sleeps": f'{row_dict["SleepHour"]}:{row_dict["SleepMin"]}',
                "wakes": f'{row_dict["WakeHour"]}:{row_dict["WakeMin"]}',
                "atk_main": int(row_dict["AttackSprite"]),
                "atk_alt": 0,
                "time": int(row_dict["EvoTime"]),
                "poop_timer": int(row_dict["PoopTimer"]),
                "energy": int(row_dict["DP"]),
                "min_weight": int(row_dict["MinWeight"]),
                "stomach": 4,
                "hunger_loss": int(row_dict["HungerTimer"]),
                "strength_loss": int(row_dict["HungerTimer"]),
                "heal_doses": 1,
                "power": int(row_dict["Power"]),
                "attribute": attribute_mapping(row_dict["Attribute"]),
                "miss_care_max": int(row_dict["MissCareMax"]),
                "jogress_avaliable": True if int(row_dict["JogressAvailable"]) == 1 else False,
                "evolve": []
            }

            monsters[monster_id] = monster_data

    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(monsters, jsonfile, indent=4, ensure_ascii=False)

# Executar
parse_csv_to_json("Book1.csv", "parsed_monsters.json")
