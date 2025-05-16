"""
获取版本分类的卡片ID列表
"""
from homepagebuilder.interfaces import script,require

mcv = require('minecraft_version') # 需求前置 MinecraftVersions
MANIFSET = mcv.get_manifset()
FULL_VERSIONS = MANIFSET.get('versions')
ID_LIST = [version.get('id') for version in FULL_VERSIONS]

@script('VersionCategory')
def version_category(cat_name,context,**_):
    cards = list(filter(lambda card:isinstance(card.get('cats'),list)
           and cat_name in card.get('cats'), context.project.get_all_card()))
    cardrefs = [card['card_id'] for card in cards]
    cardrefs.sort(key=lambda ver:ID_LIST.index(ver.split(':')[1]))
    return str.join(';',cardrefs)
