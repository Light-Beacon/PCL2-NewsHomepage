from Core.project import Project
from Interfaces import require,script,format_code

mcv = require('MinecraftVersions') # 需求前置 MinecraftVersions
MANIFSET = mcv.get_manifset()
FULL_VERSIONS = MANIFSET.get('versions')
ID_LIST = [version.get('id') for version in FULL_VERSIONS]

@script('VersionAchiveList')
def version_achive_list(cat_name,proj:Project,card,**_):
    cat_name = format_code(code = cat_name,card=card,project=proj)
    cards = list(filter(lambda card:isinstance(card.get('cats'),list)
           and cat_name in card.get('cats'), proj.get_all_card()))
    code = '<StackPanel Margin="8,2,8,15">'
    res = proj.resources
    cards.sort(key=lambda card:ID_LIST.index(format_code(card['version-id'],
                                                         card=card,project=proj)))
    if len(cards) > 0 and cards[0]['version-type-id'] not in ['Release','April-Fools']:
        code += res.components['VersionLinks/Future']
    for vercard in cards:
        if vercard.get('lack'):
            code += format_code(code = res.components['VersionLinks/Lack'],
                            card=vercard,project=proj)
        else:
            code += format_code(code = res.components['VersionLinks/Common'],
                            card=vercard,project=proj)
    code += '</StackPanel>'
    return code
