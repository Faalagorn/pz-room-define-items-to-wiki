import lupa
from item import Item

class Distribution:

    NAME_ALL = 'all'
    KEY_SKIPS = [
        'rolls',
        'items',
        'noAutoAge',
        'dontSpawnAmmo',
        'procedural', # This never appears without also procList being present.
        # Ones below need more investigation...
        'procList',
        'fillRand',
        'junk'
    ]
    KEY_ITEMS = 'items'
    KEY_PROCEDURAL = 'procList'
    KEY_JUNK = 'junk'
    KEY_ALL = 'all'

    TYPE_ROOM = 'room'
    TYPE_CONTAINER = 'container'
    TYPE_PROCEDURAL = 'procedural'
    TYPE_META = 'meta'

    LUA_TYPE_TABLE = 'table'

    # Translate any matching ids to the following values.
    ITEM_ID_TRANSLATION = {
        'BookCarpentry': 'Skill_Books|Skill Book - Carpentry',
        'BookCooking': 'Skill_Books|Skill Book - Cooking',
        'BookElectrician': 'Skill_Books|Skill Book - Electrician',
        'BookFarming': 'Skill_Books|Skill Book - Farming',
        'BookFirstAid': 'Skill_Books|Skill Book - First Aid',
        'BookFishing': 'Skill_Books|Skill Book - Fishing',
        'BookForaging': 'Skill_Books|Skill Book - Foraging',
        'BookMechanic': 'Skill_Books|Skill Book - Mechanic',
        'BookMetalWelding': 'Skill_Books|Skill Book - Metalworking',
        'BookTailoring': 'Skill_Books|Skill Book - Tailoring',
        'BookTrapping': 'Skill_Books|Skill Book - Trapping',
        'CookingMag': 'Recipe_Magazines| Recipe Magazine - Cooking',
        'ElectronicsMag': 'Recipe_Magazines| Recipe Magazine - Electronics',
        'EngineerMag': 'Recipe_Magazines| Recipe Magazine - Engineering',
        'FarmingMag': 'Recipe_Magazines| Recipe Magazine - Farming',
        'FishingMag': 'Recipe_Magazines| Recipe Magazine - Fishing',
        'HerbalistMag': 'Recipe_Magazines| Recipe Magazine - Herbalist',
        'HuntingMag': 'Recipe_Magazines| Recipe Magazine - Hunting',
        'MechanicMag': 'Recipe_Magazines| Recipe Magazine - Mechanic',
        'MetalworkMag': 'Recipe_Magazines| Recipe Magazine - Metalworking',
        'RadioMag': 'Recipe_Magazines| Recipe Magazine - Radio',
        'PillsAntiDep': 'Antidepressants',
        'PillsBeta': 'Beta Blockers',
        'PillsSleepingTablets': 'Sleeping Tablets',
        'PillsVitamins': 'Vitamins',
        'WhiskeyEmpty': 'Empty_Bottle_(Alcohol)|Whiskey Empty',
        'BeerEmpty': 'Empty_Bottle_(Alcohol)|Beer Empty',
        'BluePen': 'Pen',
        'RedPen': 'Pen',
        'WateredCan': 'Watering Can'
    }

    def __init__(self, node, is_procedural, procedural_distributions):
        self.node = node
        self.is_procedural = is_procedural
        self.procedural_distributions = procedural_distributions
        self.name = node[0]
        self.items = {}
        self.containers = set()

        if self.is_procedural:
            self.type = Distribution.TYPE_PROCEDURAL
        elif self.name == Distribution.NAME_ALL:
            self.type = Distribution.TYPE_META
        else:
            self.type = Distribution.TYPE_ROOM
            for node in node[1].items():
                container_id = node[0]
                if container_id == Distribution.KEY_ITEMS:
                    self.type = Distribution.TYPE_CONTAINER
                    break

        if self.type == Distribution.TYPE_ROOM:
            self.populate_room()
        elif self.type == Distribution.TYPE_CONTAINER or self.type == Distribution.TYPE_PROCEDURAL:
            self.populate_container()
        elif self.type == Distribution.TYPE_META:
            self.populate_meta()
        else:
            print('Unrecognized type: ' + self.type)

    def populate_room(self):
        for distribution_node in self.node[1].items():
            container_id = distribution_node[0]
            container_node = distribution_node[1]

            if str(lupa.lua_type(container_node)) != Distribution.LUA_TYPE_TABLE:
                continue

            items = None
            items_procedural = None
            items_junk = None

            for container_node_property_key, container_node_property_value in container_node.items():
                if container_node_property_key == Distribution.KEY_ITEMS:
                    items = container_node_property_value
                elif container_node_property_key == Distribution.KEY_PROCEDURAL:
                    items_procedural = container_node_property_value
                elif container_node_property_key == Distribution.KEY_JUNK:
                    items_junk = container_node_property_value

            if items:
                is_value = True
                for item_id in items.values():
                    if is_value:
                        self.add_item(item_id, container_id)
                    is_value = not is_value
            elif items_procedural:
                for item_procedural in items_procedural.values():
                    for distribution_procedural in self.procedural_distributions:
                        if item_procedural.name == distribution_procedural.name:
                            for item in distribution_procedural.items:
                                self.add_item(item, container_id, False)

    def populate_container(self):
        for distribution_node in self.node[1].items():
            container_id = distribution_node[0]
            container_node = distribution_node[1]

            if container_id != Distribution.KEY_ITEMS or str(lupa.lua_type(container_node)) != Distribution.LUA_TYPE_TABLE:
                continue

            is_value = True
            for item_id in container_node.values():
                if is_value:
                    self.add_item(item_id, container_id)

                is_value = not is_value

    def populate_meta(self):
        return

    def add_item(self, item_id, container_id, cleanup=True):
        if cleanup:
            item_id = self.cleanup_item_id(item_id)
        container_id = self.cleanup_container_id(container_id)

        item = self.items.get(item_id)

        if item is None:
            item = Item(item_id)
            self.items[item_id] = item

        item.containers.add(container_id)
        self.containers.add(container_id)

    def cleanup_container_id(self, id):
        id = id.strip()  # Remove leading and trailing whitespace
        id = id.replace('_', ' ')  # Replace underscores with spaces for readability
        return id

    def cleanup_item_id(self, raw_item_id):
        # Check each key in the ITEM_ID_TRANSLATION dictionary to see if it's found in the raw item ID
        for key, value in self.ITEM_ID_TRANSLATION.items():
            if key in raw_item_id:
                # If a match is found anywhere in the raw item ID, return the corresponding translated value
                return value

        # Path to the translation file
        translation_file_path = 'resources/translate.txt'

        try:
            # Open the translation file
            with open(translation_file_path, 'r') as file:
                for line in file:
                    # Check if the raw item ID is in the current line
                    if raw_item_id in line:
                        # Look for the equals sign to extract the portion after it
                        parts = line.split('=')
                        if len(parts) > 1:
                            # Find the first quotation mark after the equals sign
                            start_pos = parts[1].find('"') + 1  # Start of the cleaned ID
                            end_pos = parts[1].find('"', start_pos)  # End of the cleaned ID
                            if start_pos > 0 and end_pos > 0:
                                # Extract the cleaned ID from within the quotation marks
                                id = parts[1][start_pos:end_pos]
                                return id  # Return the cleaned ID
            # If the raw item ID is not found in the file or dictionary, return it as is
            return raw_item_id
        except FileNotFoundError:
            # Handle the case where the translation file does not exist
            print(f"Translation file not found at {translation_file_path}.")
            return raw_item_id
        except Exception as e:
            # Handle other possible exceptions
            print(f"An error occurred: {e}")
            return raw_item_id