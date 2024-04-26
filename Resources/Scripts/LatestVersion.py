from Core.Debug import LogWarning, LogInfo
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
LogInfo(f'[VersionScript] 最新快照版:{LATEST_VERSIONS["snapshot"]}; 最新正式版:{LATEST_VERSIONS["release"]}')

def script(version_type,version_rank = '1',**kwagrs):
    version_rank = int(version_rank)
    if version_rank <= 1:
        return f"{LATEST_VERSIONS[version_type]} | latest = true"
    count = version_rank
    for version in FULL_VERSIONS:
        if version['type'] == version_type:
            count -= 1
            if count == 0:
                return version['id']
    return ''