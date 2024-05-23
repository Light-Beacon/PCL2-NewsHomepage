from Core.Debug import LogWarning, LogInfo
from Core.ModuleManager import invokeModule, untilLoaded

untilLoaded('MinecraftVersions') # 需求前置 MinecraftVersions
get_latest = invokeModule('MinecraftVersions','get_latest')
get_type = invokeModule('MinecraftVersions','get_version_type')

latest_version = get_latest()
latest_type = get_type(latest_version)

def script(page_area,**kwagrs):
    if page_area == 'new':
        result = f"{latest_version} | latest = true | s = false"
        if latest_type == 'snapshot':
            iversion = latest_version
            index = 1
            while(True): # 循环添加该周发布的所有版本
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