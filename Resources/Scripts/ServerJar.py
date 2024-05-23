from Core.ModuleManager import invokeModule, untilLoaded

untilLoaded('MinecraftVersions') # 需求前置 MinecraftVersions
get_server_jar = invokeModule('MinecraftVersions','get_server_jar')

def script(card,**kwargs):
    return get_server_jar(card['version-id'])