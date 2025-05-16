"""
获取MC版本服务器端 jar 包下载链接
"""
from homepagebuilder.interfaces import require,script

mcv = require('minecraft_version') # 需求前置 MinecraftVersions
get_server_jar = mcv.get_server_jar

@script('ServerJar')
def get_server_jar_script(card,**_):
    return get_server_jar(card['version-id'])
