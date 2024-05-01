import json
import requests
import re
import os

LAUNCHER_MANIFSET_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest.json'

SNAPSHOT_PATTERN = re.compile(r'^[0-9]{2}[w|W][0-9]{2}[A-Za-z]$')
PRE_RELEASE_PATTERN = re.compile(r'^.*-pre[0-9]+$')
RELEASE_CANDIDATE_PATTERN = re.compile(r'^.*-rc[0-9]+$')
RELEASE_PATTERN = re.compile(r'^1\.[0-9]+(\.[0-9]+)?$')

INIT_MARKDOWN = '---\nversion-image-link: null\nnot_finished: true\nserver-jar: null\ntranslator: null\n---\n'

require_update = False

def get_version_type(vid:str):
    if re.match(SNAPSHOT_PATTERN,vid):
        return 'Snapshot'
    if re.match(PRE_RELEASE_PATTERN,vid):
        return 'Pre-Release'
    if re.match(RELEASE_CANDIDATE_PATTERN,vid):
        return 'Release-Candidate'
    if re.match(RELEASE_PATTERN,vid):
        return 'Release'
    return 'Others'

def update_library(version_libloc:str,ver_type:str,ver_id:str):
    filepath = f'{version_libloc}{ver_type}{os.sep}{ver_id}.md'
    if os.path.exists(filepath):
        return False,'存在于版本库，无需更改'
    else:
        with open(filepath, "w") as file:
            file.write(INIT_MARKDOWN)
        return True,'版本库内未找到，已添加'

try:
    response = requests.get(LAUNCHER_MANIFSET_URL)
    version_mainfest = json.loads(response.content)
except Exception as e:
    print(f'error_log={e.with_traceback()}')
    exit(1)

latest_snapshot_id = version_mainfest['latest']['snapshot']
latest_release_id = version_mainfest['latest']['release']

latest_snapshot_type = get_version_type(latest_snapshot_id)
latest_release_type = get_version_type(latest_release_id)

#print(f'● 最新 {latest_release_type} 版: {latest_release_id}') 
#print(f'● 最新 {latest_snapshot_type} 版: {latest_snapshot_id}') 

dir_location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
version_lib_location = f'{dir_location}{os.sep}Libraries{os.sep}Versions{os.sep}'

release_require_update,latest_release_act = \
update_library(version_lib_location,latest_release_type,latest_release_id)
snapshot_require_update,latest_snapshot_act = \
update_library(version_lib_location,latest_snapshot_type,latest_snapshot_id)

print(f'latest_release_type={latest_release_type}')
print(f'latest_snapshot_type={latest_snapshot_type}')
print(f'latest_release_id={latest_release_id}')
print(f'latest_snapshot_id={latest_snapshot_id}')
print(f'latest_release_act={latest_release_act}')
print(f'latest_snapshot_act={latest_snapshot_act}')
print(f'require_update={release_require_update or snapshot_require_update}')
