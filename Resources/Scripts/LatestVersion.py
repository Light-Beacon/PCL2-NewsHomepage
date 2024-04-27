from Core.Debug import LogWarning, LogInfo
from Core.ModuleManager import invokeModule, untilLoaded
import requests
import json

untilLoaded('FetchMainfest')
MANIFSET = invokeModule('FetchMainfest','fetch')()
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