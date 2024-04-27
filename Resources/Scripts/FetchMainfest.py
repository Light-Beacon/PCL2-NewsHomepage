from Core.Debug import LogWarning
import requests
import json

LAUNCHER_MANIFSET_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest.json'

def fetch():
    try:
        response = requests.get(LAUNCHER_MANIFSET_URL)
        return json.loads(response.content)
    except Exception as e:
        LogWarning(f'获取版本列表失败：{e.with_traceback()}')
        return {}