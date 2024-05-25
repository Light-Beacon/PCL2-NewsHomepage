from Core.project import Project
from Core.module_manager import invoke_module, until_loaded

until_loaded('MinecraftVersions') # 需求前置 MinecraftVersions
MANIFSET = invoke_module('MinecraftVersions','get_manifset')()
FULL_VERSIONS = MANIFSET.get('versions')
ID_LIST = [version.get('id') for version in FULL_VERSIONS]

def script(cat_name,proj:Project,**_):
    cards = list(filter(lambda card:isinstance(card.get('cats'),list)
           and cat_name in card.get('cats'), proj.get_all_card()))
    cardrefs = [card['card_id'] for card in cards]
    cardrefs.sort(key=lambda ver:ID_LIST.index(ver.split(':')[1]))
    return str.join(';',cardrefs)
