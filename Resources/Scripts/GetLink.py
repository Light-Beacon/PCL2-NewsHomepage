from .Debug import LogWarning, LogInfo
def script(card,arg,res):
    name = card['version-id']
    data = res.data[f'{arg[1]}Link']
    if arg[1] == 'Mcbbs' and name not in data:
        LogInfo(f'尝试获取MCBBS链接 {name}，但未找到，由于 MCBBS 关站，返回空值以抑制 Warning')
        return ''
    return data[name]