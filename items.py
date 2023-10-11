class items:
    def __init__(self, unique_id, item_id, item_type, name):
        self.unique_id = unique_id
        self.item_id = item_id
        self.item_type = item_type
        self.name = name

class case(items):
    def __init__(self, unique_id, item_id, item_type, name, skins_list):
        super().__init__(unique_id, item_id, item_type, name)
        self.skins_list = skins_list

class skin(items):
    def __init__(self, unique_id, item_id, item_type, name, wear, max_wear, min_wear, rarity, pattern_id, collection):
        super().__init__(unique_id, item_id, item_type, name)
        self.wear = wear
        self.max_wear = max_wear
        self.min_wear = min_wear
        self.rarity = rarity
        self.pattern_id = pattern_id
        self.collection = collection

