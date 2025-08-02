import json
import os

DIGIDEX_PATH = "save/digidex.json"


def load_digidex() -> list[dict]:
    """
    Lê o arquivo de progresso da Digidex. Retorna uma lista de pets obtidos.
    Cada item contém: { "name": str, "module": str, "version": int }
    """
    if not os.path.exists(DIGIDEX_PATH):
        return []
    try:
        with open(DIGIDEX_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_digidex(entries: list[dict]) -> None:
    """
    Salva a lista completa de pets conhecidos no arquivo da Digidex.
    """
    with open(DIGIDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def register_digidex_entry(name: str, module: str, version: int) -> None:
    """
    Adiciona um pet à Digidex se ainda não estiver presente.
    """
    data = load_digidex()
    exists = any(
        p["name"] == name and p["module"] == module and p["version"] == version
        for p in data
    )
    if not exists:
        data.append({"name": name, "module": module, "version": version})
        save_digidex(data)


def is_pet_unlocked(name: str, module: str, version: int) -> bool:
    """
    Verifica se um pet específico já foi desbloqueado.
    """
    data = load_digidex()
    return any(
        p["name"] == name and p["module"] == module and p["version"] == version
        for p in data
    )