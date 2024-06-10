from Core.project import Project
from Core.module_manager import invoke_module, until_loaded
from Core.code_formatter import format_code

until_loaded('MinecraftVersions') # 需求前置 MinecraftVersions
MANIFSET = invoke_module('MinecraftVersions','get_manifset')()
FULL_VERSIONS = MANIFSET.get('versions')
ID_LIST = [version.get('id') for version in FULL_VERSIONS]

def script(cat_name,proj:Project,card,**_):
    cat_name = format_code(code = cat_name,card=card,project=proj)
    cards = list(filter(lambda card:isinstance(card.get('cats'),list)
           and cat_name in card.get('cats'), proj.get_all_card()))
    code = '<StackPanel Margin="8,2,8,20">'
    res = proj.resources
    cards.sort(key=lambda card:ID_LIST.index(format_code(card['version-id'],
                                                         card=card,project=proj)))
    if len(cards) > 0 and cards[0]['version-type-id'] not in ['Release','April-Fools']:
        code += res.components['VersionLinks/Future-Release']
    for vercard in cards:
        code += format_code(code = res.components[f'VersionLinks/{vercard['version-type-id']}'],
                            card=vercard,project=proj)
    code += '</StackPanel>'
    return code
