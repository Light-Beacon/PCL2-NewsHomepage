from homepagebuilder.core.project import Project
from homepagebuilder.interfaces import require,script,format_code

mcv = require('MinecraftVersions') # 需求前置 MinecraftVersions
MANIFSET = mcv.get_manifset()
FULL_VERSIONS = MANIFSET.get('versions')
ID_LIST = [version.get('id') for version in FULL_VERSIONS]

@script('VersionArchiveList')
def version_achive_list(cat_name,env,card,**_):
    components = env.get('components')
    cat_name = format_code(code = cat_name,data=card,env=env)
    cards = list(filter(lambda card:isinstance(card.get('cats'),list)
           and cat_name in card.get('cats'), env.get('project').get_all_card()))
    code = '<StackPanel Margin="8,2,8,15">'
    cards.sort(key=lambda card:ID_LIST.index(format_code(card['version-id'],
                                                         data=card,env=env)))
    if len(cards) > 0 and cards[0]['version-type-id'] not in ['Release','April-Fools']:
        code += components['VersionLinks/Future'].toxaml(card={},env=env)
    for vercard in cards:
        if vercard.get('lack'):
            code += components['VersionLinks/Lack'].toxaml(card=vercard,env=env)
        else:
            code += components['VersionLinks/Common'].toxaml(card=vercard,env=env)
    code += '</StackPanel>'
    return code

@script('VersionLatestList')
def version_latest_list(env,**_):
    proj = env.get('project')
    components = env.get('components')
    code = ''
    for version_type in ['release','snapshot']:
        if latest_version := mcv.get_latest(version_type):
            vercard = proj.base_library.get_card(latest_version,False)
            code += components['VersionLinks/Latest'].toxaml(card=vercard,env=env)
    return code