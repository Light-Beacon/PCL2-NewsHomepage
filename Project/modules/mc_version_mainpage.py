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
        return f"{latest_version} | latest = true | s = false"
    else:
        if latest_type == 'release':
            return ''
        return f"{mcv.get_latest('release')} | latest = true"
