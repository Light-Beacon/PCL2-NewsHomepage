import re
import json
import requests
from enum import Enum
from typing import Optional, TypedDict, Literal
from logging import Logger

# region 版本模式定义
DEVELOP_VERSION_PATTERN = re.compile(r'^(?P<major>[\d.]+)-(?P<type>[a-zA-Z]+)-?(?P<index>\d)+$')
"开发版本号模式"
RELEASE_PATTERN = re.compile(r'^\d{1,2}\.\d+(\.\d+)?$')
"正式版本号模式"
OLD_SNAPSHOT_PATTERN = re.compile(r'^(1\d)|(2[0-5])[w|W]\d{2}[A-Fa-f]$')
"旧版本快照模式，用于 1.21.11 及以前的版本"
# endregion

# region 常量定义
OFFICIAL_CHANGELOG_URL_PREFIX = 'https://minecraft.net/article/minecraft'
LAUNCHER_MANIFEST_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest.json'
# endregion

# region 官网更新日志重载词典
OFFICIAL_CHANGE_LOG_OVERRIDE_LINKS: dict[str, str] = {}

# endregion

logger = Logger('MCV')

# region 版本信息类定义
class MinecraftManifestVersionInfo(TypedDict):
    id: str
    type: Literal['snapshot', 'release', 'old_beta', 'old_alpha']
    url: str
    time: str
    releaseTime: str


class MinecraftManifestLatestVersionInfo(TypedDict):
    snapshot: Optional[str]
    release: Optional[str]


class MinecraftManifest(TypedDict):
    latest: MinecraftManifestLatestVersionInfo
    versions: list[MinecraftManifestVersionInfo]


# endregion

# region 版本类定义
class VersionType(Enum):
    SNAPSHOT = 'snapshot'
    PRE_RELEASE = 'pre'
    RELEASE_CANDIDATE = 'rc'
    RELEASE = 'release'
    OTHER = 'other'


class MinecraftVersion:
    id: str
    type: VersionType
    url: str
    time: str
    release_time: str
    use_old_id_format: bool = False
    major_version: Optional[str] = None
    release_index: Optional[str] = None

    __server_jar_url: Optional[str] = None

    @property
    def server_jar_url(self) -> str:
        if self.__server_jar_url:
            return self.__server_jar_url
        server_jar_url: Optional[str]
        response = requests.get(self.url, timeout=10000)
        server_jar_url = json.loads(response.content).get('downloads').get('server').get('url')
        if not server_jar_url:
            raise ValueError(f"版本 {self.id} 的服务器端下载链接不存在")
        self.__server_jar_url = server_jar_url
        return server_jar_url

    __change_log_url: Optional[str] = None

    @property
    def change_log_url(self) -> str:
        """获取版本更新日志链接"""
        if self.__change_log_url:
            return self.__change_log_url
        if override_url := OFFICIAL_CHANGE_LOG_OVERRIDE_LINKS.get(self.id):
            self.__change_log_url = override_url
            return override_url
        if self.type == VersionType.OTHER:
            return ""
        if self.use_old_id_format:
            self.__change_log_url = OFFICIAL_CHANGELOG_URL_PREFIX + '-snapshot-' + self.id.lower()
        elif self.type == VersionType.RELEASE:
            self.__change_log_url = f"{OFFICIAL_CHANGELOG_URL_PREFIX}-java-edition-{self.id.replace('.', '-')}"
        else:
            assert self.major_version is not None
            self.__change_log_url = f"{OFFICIAL_CHANGELOG_URL_PREFIX}-" \
                                    f"{self.major_version.replace('.', '-')}-" \
                                    f"{self.type.name.lower().replace('_', '-')}-{self.release_index}"
        return self.__change_log_url

    def __init__(self, version_id: str, url: str, time: str, release_time: str):
        self.id = version_id
        self.url = url
        self.time = time
        self.release_time = release_time
        if m := re.match(DEVELOP_VERSION_PATTERN, version_id):
            self.type = VersionType(m.group('type').lower())
            self.major_version = m.group('major')
            self.release_index = m.group('index')
        elif re.match(OLD_SNAPSHOT_PATTERN, version_id):
            self.type = VersionType.SNAPSHOT
            self.use_old_id_format = True
        elif re.match(RELEASE_PATTERN, version_id):
            self.type = VersionType.RELEASE
            self.major_version = version_id
        else:
            self.type = VersionType.OTHER


class MinecraftVersionManager:
    __latest_development_version_id: Optional[str]
    __latest_release_version_id: Optional[str]
    __manifest: MinecraftManifest
    __manifest_versions: list[MinecraftManifestVersionInfo]
    __versions: dict[str, MinecraftVersion] = {}
    __version_ids: list[str] = []

    def __init__(self):
        self.refresh_manifest()
        self.__latest_development_version_id = self.__manifest['latest']['snapshot']
        self.__latest_release_version_id = self.__manifest['latest']['release']
        self.__manifest_versions = self.__manifest.get('versions', [])
        self.__version_ids = [version['id'] for version in self.__manifest_versions]

    def get(self, version_id: str) -> Optional[MinecraftVersion]:
        if version_id in self.__versions:
            return self.__versions[version_id]
        for version_info in self.__manifest_versions:
            if version_info['id'] == version_id:
                version = MinecraftVersion(version_id=version_info['id'],
                                           url=version_info['url'],
                                           time=version_info['time'],
                                           release_time=version_info['releaseTime'])
                self.__versions[version_id] = version
                return version
        return None

    def get_version_id_list(self) -> list[str]:
        return self.__version_ids

    def get_latest_version(self, version_type: Literal['any', 'development', 'release'] = 'any'
                           ) -> Optional[MinecraftVersion]:
        if version_type == 'any':
            if self.__latest_development_version_id:
                return self.get(self.__latest_development_version_id)
            elif self.__latest_release_version_id:
                return self.get(self.__latest_release_version_id)
            else:
                return None
        elif version_type == 'development' and self.__latest_development_version_id:
            return self.get(self.__latest_development_version_id)
        elif version_type == 'release' and self.__latest_release_version_id:
            return self.get(self.__latest_release_version_id)
        else:
            return None
    
    @property
    def versions(self):
        for version_id in self.__version_ids:
            version = self.get(version_id)
            assert version is not None
            yield version

    def get_latest_development_versions(self) -> Optional[list[MinecraftVersion]]:
        latest_version = self.get_latest_version()
        if not latest_version or latest_version.type == VersionType.RELEASE:
            return None
        latest_development_versions = []
        current_major_version_branches = set()
        for version in self.versions:
            if version.major_version in current_major_version_branches:
                break
            if version.type == VersionType.RELEASE:
                break
            if version.type == VersionType.OTHER:
                continue
            current_major_version_branches.add(version.major_version)
            latest_development_versions.append(version)
        return latest_development_versions

    def refresh_manifest(self):
        self.__manifest = self.fetch_manifest()

    @classmethod
    def fetch_manifest(cls) -> MinecraftManifest:
        logger.info("正在加载 MC 版本列表")
        try:
            response = requests.get(LAUNCHER_MANIFEST_URL, timeout=10000)
            return json.loads(response.content)
        except Exception as e:
            logger.warning("加载 MC 版本列表失败")
            logger.exception(e)
            return MinecraftManifest(latest=MinecraftManifestLatestVersionInfo(snapshot=None, release=None),
                                     versions=[])


# endregion

MCVM = MinecraftVersionManager()
