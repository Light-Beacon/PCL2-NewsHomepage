from Core. module_manager import invoke_module, until_loaded

until_loaded('MinecraftVersions') # 需求前置 MinecraftVersions
get_server_jar = invoke_module('MinecraftVersions','get_server_jar')

def script(card,**_):
    return get_server_jar(card['version-id'])
