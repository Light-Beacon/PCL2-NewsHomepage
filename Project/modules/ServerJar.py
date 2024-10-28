from homepagebuilder.interfaces import require,script

mcv = require('MinecraftVersions') # 需求前置 MinecraftVersions
get_server_jar = mcv.get_server_jar

@script('ServerJar')
def get_server_jar_script(card,**_):
    return get_server_jar(card['version-id'])
