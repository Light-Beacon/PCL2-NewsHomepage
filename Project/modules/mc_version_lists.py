"""
版本最新、存档页面列表
"""

from homepagebuilder.interfaces import require,script,format_code

mcv = require('minecraft_version') # 需求前置 MinecraftVersions
MANIFSET = mcv.get_manifset()
FULL_VERSIONS = MANIFSET.get('versions')
ID_LIST = [version.get('id') for version in FULL_VERSIONS]

@script('VersionArchiveList')
def version_achive_list(cat_name,context,card,**_):
    components = context.components
    cat_name = format_code(code = cat_name,data=card,context=context)
    cards = list(filter(lambda card:isinstance(card.get('cats'),list)
           and cat_name in card.get('cats'), context.project.get_all_card()))
    code = '<StackPanel Margin="8,2,8,15">'
    cards.sort(key=lambda card:ID_LIST.index(format_code(card['version-id'],
                                                         data=card,context=context)))
    if len(cards) > 0 and cards[0]['version-type-id'] not in ['Release','April-Fools']:
        code += components['VersionLinks/Future'].toxaml(card={},context=context)
    for vercard in cards:
        if vercard.get('lack'):
            code += components['VersionLinks/Lack'].toxaml(card=vercard,context=context)
        else:
            code += components['VersionLinks/Common'].toxaml(card=vercard,context=context)
    code += '</StackPanel>'
    return code

@script('VersionLatestList')
def version_latest_list(context,**_):
    proj = context.project
    components = context.components
    code = ''
    for version_type in ['release','snapshot']:
        if latest_version := mcv.get_latest(version_type):
            vercard = proj.base_library.get_card(latest_version,False)
            code += components['VersionLinks/Latest'].toxaml(card=vercard,context=context)
    return code