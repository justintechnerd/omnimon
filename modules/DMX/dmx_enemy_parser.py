import json
import os
import re
from bs4 import BeautifulSoup

# File paths
HTML_FILE_PATH = "Quest Mode - Digital Monster X Ver.3.htm"
OUTPUT_JSON = "quest_mode_data.json"

VERSION_MAP = {
    1: "XA", 2: "XB", 3: "XC",
    4: "XD", 5: "XE", 6: "XF"
}
SCRAP_VERSION = 6  # Define which version we are scraping (default: XA)

def load_html_from_file(file_path):
    """Load HTML content from a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_digimon_key(img_tag):
    """Extract Digimon key from onclick attribute."""
    match = re.search(r"digimonDetails\('([^']+)'\)", img_tag.get("onclick", ""))
    return match.group(1) if match else None

def normalize_attribute(raw_attr):
    """Standardize attribute values."""
    attr_map = {"Da": "Data", "Va": "Vaccine", "Vi": "Virus"}
    return attr_map.get(raw_attr, "")

def extract_digimon_details(soup, digimon_code):
    """Extract detailed attributes from the details section."""
    details_section = soup.find("div", {"id": f"{digimon_code}_card"})
    if not details_section:
        print(f"[WARNING] Missing details for {digimon_code}")
        return {
            "name": digimon_code.capitalize(),
            "power": 0,
            "attribute": "",
            "hp": 0
        }

    # **Use second name (`dub`) if present, otherwise fall back to first name (`sub`)**
    name_tag = details_section.find("p", class_="dub") or details_section.find("p", class_="sub")

    power_tag = details_section.find(string=re.compile(r"Power:"))
    attribute_tag = details_section.get("class", ["Unknown"])[-1]  # Extract attribute from class name
    hp_tag = details_section.find(string=re.compile(r"HP:"))

    return {
        "name": name_tag.get_text(strip=True) if name_tag else digimon_code.capitalize(),
        "power": int(re.search(r"\d+", power_tag).group()) if power_tag and re.search(r"\d+", power_tag) else 0,
        "attribute": normalize_attribute(attribute_tag),
        "hp": int(re.search(r"\d+", hp_tag).group()) if hp_tag and re.search(r"\d+", hp_tag) else 0
    }


def parse_main_table(soup):
    """Parse the HTML table and extract quest mode battle data."""
    table = soup.find("table", {"id": "x_battles"})
    battles = []

    for row in table.find_all("tr", class_="battle_row"):
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        area = int(cols[0].text.strip()) if cols[0].text.strip().isdigit() else None
        encounters = cols[1].find_all("img", onclick=True)
        boss = cols[2].find("img", onclick=True)
        prize = cols[3].find("img")["title"] if cols[3].find("img") else ""
        unlock_value = cols[4].text.strip()

        # Determine unlock condition based on SCRAP_VERSION
        unlock = VERSION_MAP[SCRAP_VERSION] if unlock_value in [VERSION_MAP[SCRAP_VERSION], "Both"] else ""

        round_number = 1

        # Extract individual encounters as separate rounds, **skip "rest" and "blank"**
        for encounter in encounters:
            digimon_key = extract_digimon_key(encounter)
            if digimon_key and digimon_key not in ["rest", "blank"]:
                details = extract_digimon_details(soup, digimon_key)
                details.update({"area": area, "round": round_number, "version": SCRAP_VERSION})
                battles.append(details)
                round_number += 1

        # Add the boss as the final round in the area
        if boss:
            digimon_key = extract_digimon_key(boss)
            details = extract_digimon_details(soup, digimon_key)
            details.update({"area": area, "round": round_number, "version": SCRAP_VERSION, "prize": prize, "unlock": unlock})
            battles.append(details)

    return battles

def generate_json():
    """Generate and save JSON file with enriched battle data."""
    html_content = load_html_from_file(HTML_FILE_PATH)
    soup = BeautifulSoup(html_content, "html.parser")
    data = parse_main_table(soup)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data

if __name__ == "__main__":
    generate_json()
