from Interfaces import invoke,require,script

mcv = require('MinecraftVersions') # 需求前置 MinecraftVersions
get_server_jar = mcv.get_server_jar()

@script('ServerJar')
def script(card,**_):
    return get_server_jar(card['version-id'])
