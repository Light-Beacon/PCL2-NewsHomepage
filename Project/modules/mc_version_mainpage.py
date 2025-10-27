"""
主页MC版本卡片选择器
"""
from homepagebuilder.interfaces import script,require,Logger

mcv = require('minecraft_version') # 需求前置 MinecraftVersions
latest_version = mcv.get_latest()
assert latest_version is not None
latest_type = mcv.get_version_type(latest_version)
logger = Logger('MainPageVersions')

@script('MainPageVersions')
def mainPageVersion(page_area,**_):
    '''脚本体'''
    if page_area == 'new':
        result = f"{latest_version} | latest = true | s = false"
        if latest_type == 'snapshot' and latest_version[5] != 'a':
            i_version = latest_version
            index = 2
            while True: # 循环添加该周发布的所有版本
                i_version = mcv.get_latest('snapshot', index)
                result += f';{i_version} | s = false'
                if (mcv.get_version_type(i_version) != 'snapshot') or (i_version[5] == 'a'):
                    break
                index += 1
        return result
    else:
        if latest_type == 'release':
            return ''
        return f"{mcv.get_latest('release')} | latest = true"
