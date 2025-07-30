from core import game_globals

def get_inventory_value(item_id):
    """
    Returns the quantity of the item with the given id, or 0 if not present.
    """
    return game_globals.inventory.get(item_id, 0)

def add_to_inventory(item_id, amount=1):
    """
    Adds the specified amount of the item to the inventory.
    """
    game_globals.inventory[item_id] = game_globals.inventory.get(item_id, 0) + amount

def remove_from_inventory(item_id, amount=1):
    """
    Removes the specified amount of the item from the inventory.
    """
    if item_id in game_globals.inventory:
        game_globals.inventory[item_id] -= amount
        if game_globals.inventory[item_id] <= 0:
            del game_globals.inventory[item_id]