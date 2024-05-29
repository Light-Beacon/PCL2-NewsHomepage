from Core.module_manager import invoke_module, until_loaded
from Core.logger import Logger

until_loaded('MinecraftVersions') # 需求前置 MinecraftVersions
get_latest = invoke_module('MinecraftVersions','get_latest')
get_type = invoke_module('MinecraftVersions','get_version_type')

latest_version = get_latest()
latest_type = get_type(latest_version)

logger = Logger('MainPageVersions')

def script(page_area,**_):
    '''脚本体'''
    if page_area == 'new':
        result = f"{latest_version} | latest = true | s = false"
        if latest_type == 'snapshot':
            iversion = latest_version
            index = 1
            while True: # 循环添加该周发布的所有版本
                if (get_type(iversion) != 'snapshot') or (iversion[5] == 'a'):
                    break
                index += 1
                iversion = get_latest('snapshot',index)
                result += f';{iversion} | s = false'
        return result
    else:
        if latest_type == 'release':
            return ''
        return f"{get_latest('release')} | latest = true"
