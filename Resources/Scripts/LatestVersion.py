from Core.Debug import LogWarning
import requests
import json

LAUNCHER_MANIFSET_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest.json'

def fetch_mainfest():
    try:
        response = requests.get(LAUNCHER_MANIFSET_URL)
        return json.loads(response.content)
    except Exception as e:
        LogWarning(f'获取版本列表失败：{e.with_traceback()}')
        return {}

MANIFSET = fetch_mainfest()
LATEST_VERSIONS = {'snapshot':'','release':''}
LATEST_VERSIONS.update(MANIFSET['latest'])
FULL_VERSIONS = MANIFSET.get('versions')

def script(card,arg,res):
    if len(arg) <= 2 or (count := int(arg[2])) <= 1:
        return f"{LATEST_VERSIONS[arg[1]]} | latest = true"
    for version in FULL_VERSIONS:
        if version['type'] == arg[1]:
            count -= 1
            if count == 0:
                return version['id']
    return ''