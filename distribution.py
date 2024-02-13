import re
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
        'WateredCan': 'Watering Can',
        'Mov_Microwave2': 'White Microwave',
        'Mov_DegreeDoctor': 'Doctor Degree Certificate',
        'Mov_DegreeSurgeon': 'Surgeon Degree Certificate',
        'Mov_FlagAdmin': 'Administrative Flag',
        'Mov_FlagUSA': 'USA Flag',
        'Mov_FlagUSALarge': 'Stars & Stripes Flag',
        'Mov_PosterDroids': 'Droids Poster',
        'Mov_PosterElement': 'Element Poster',
        'Mov_PosterMedical': 'Medical Poster',
        'Mov_PosterOmega': 'Omega Poster',
        'Mov_PosterPaws': 'Paws Poster',
        'Mov_PosterPieBlue': 'Pie Blue Poster',
        'Mov_PosterPiePink': 'Pie Pink Poster',
        'Mov_PosterPieRed': 'Pie Red Poster',
        'Mov_SignArmy': 'Army Property Sign',
        'Mov_SignCitrus': 'Citrus Sign',
        'Mov_SignRestricted': 'Restricted Area Sign',
        'Mov_SignWarning': 'Warning Sign'
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
        # Iterate over dictionary items
        for key, value in self.ITEM_ID_TRANSLATION.items():
            if key in raw_item_id:
                return value

        # Select the appropriate file based on whether the ID starts with 'Mov_'
        translation_file_path = 'resources/movables.txt' if raw_item_id.startswith(
            'Mov_') else 'resources/translate.txt'
        item_id_for_search = raw_item_id[4:] if raw_item_id.startswith('Mov_') else raw_item_id

        # First attempt to find a translation
        found, id = self.attempt_translation(translation_file_path, item_id_for_search)
        if found:
            return id

        modified_id = item_id_for_search
        # If no translation found and the ID was originally prefixed with 'Mov_', modify the ID
        if raw_item_id.startswith('Mov_'):
            modified_id = self.modify_id(item_id_for_search)
            # Second attempt to find a translation with modified ID
            found, id = self.attempt_translation(translation_file_path, modified_id)
            if found:
                return id

        # Adjust the final return statement to return the modified ID when no translation is found
        if raw_item_id.startswith('Mov_') and modified_id != item_id_for_search:
            final_id = 'Mov_' + modified_id
            return final_id
        else:
            return raw_item_id

    def attempt_translation(self, file_path, item_id):
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if item_id in line:
                        parts = line.split('=')
                        if len(parts) > 1 and '"' in parts[1]:
                            start_pos = parts[1].find('"') + 1
                            end_pos = parts[1].find('"', start_pos)
                            if end_pos > start_pos:
                                id = parts[1][start_pos:end_pos]
                                return True, id
            return False, item_id
        except Exception as e:
            return False, item_id

    def modify_id(self, item_id):
        modified_id = re.sub(r'([a-z])([A-Z])', r'\1_\2', item_id)
        return modified_id
