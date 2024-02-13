# Room Define to Wiki

This is used to generate the list of items spawned in various room definitions for [this wiki article.](https://pzwiki.net/wiki/Room_definitions_and_item_spawns)

## How to use this repository:

1. Create a directory called `resources` in the same directory as this `README` file.
2. Find the `Distributions.lua` and `ProceduralDistributions.lua` files in your Project Zomboid install and place them inside the 'resources' directory you just created.
3. Download the appropriate `ItemName_XX.txt` and `Movables_XX.txt` from [this git.](https://github.com/TheIndieStone/ProjectZomboidTranslations/)
4. Rename the translation file to `translate.txt` and the movables file to `movables.txt` and place both into the `resources` folder.
3. Run `main.py` and the results will be output to `exports/wiki_results.txt`. You now have an updated version of the items spawned by various room definitions, formatted for the Project Zomboid wiki!
    
**NOTICE FOR THOSE SUBMITTING MERGE REQUESTS: DO NOT INCLUDE LUA FILES FROM PROJECT ZOMBOID!**

Those files should not be distributed without permission from The Indie Stone. 