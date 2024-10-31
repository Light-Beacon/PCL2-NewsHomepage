from homepagebuilder.interfaces import script,require,Logger

mcv = require('MinecraftVersions') # 需求前置 MinecraftVersions
latest_version = mcv.get_latest()
latest_type = mcv.get_version_type(latest_version)
logger = Logger('MainPageVersions')

@script('MainPageVersions')
def mainPageVersion(page_area,**_):
    '''脚本体'''
    if page_area == 'new':
        result = f"{latest_version} | latest = true | s = false"
        if latest_type == 'snapshot':
            iversion = latest_version
            index = 1
            while True: # 循环添加该周发布的所有版本
                if (mcv.get_version_type(iversion) != 'snapshot') or (iversion[5] == 'a'):
                    break
                index += 1
                iversion = mcv.get_latest('snapshot',index)
                result += f';{iversion} | s = false'
        return result
    else:
        if latest_type == 'release':
            return ''
        return f"{mcv.get_latest('release')} | latest = true"
