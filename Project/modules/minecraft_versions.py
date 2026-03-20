import re
import json
import requests
from enum import Enum
from typing import Optional, TypedDict, Literal
from homepagebuilder.core.logger import Logger
from homepagebuilder.interfaces import script, format_code
from homepagebuilder.core.types import Context
from homepagebuilder.core.utils.event import listen_event as on

# region 版本模式定义
DEVELOP_VERSION_PATTERN = re.compile(r'^(?P<major>[\d.]+)-(?P<type>[a-zA-Z]+)-?(?P<index>\d)+$')
"开发版本号模式"
RELEASE_PATTERN = re.compile(r'^\d{1,2}\.\d+(\.\d+)?$')
"正式版本号模式"
OLD_SNAPSHOT_PATTERN = re.compile(r'^\d{2}[w|W]\d{2}[A-Fa-f]$')
"旧版本快照模式，用于 1.21.11 及以前的版本"
# endregion

logger = Logger('MinecraftVersion')

# region 常量定义
OFFICIAL_CHANGELOG_URL_PREFIX = 'https://minecraft.net/article/minecraft'
LAUNCHER_MANIFEST_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest.json'
# endregion

# region 官网更新日志重载词典
OFFICIAL_CHANGE_LOG_OVERRIDE_LINKS: dict[str, str] = {}


@on('project.import.return')
def setup_official_changelog_override_links(*_, **__) -> None:
    global OFFICIAL_CHANGE_LOG_OVERRIDE_LINKS
    OFFICIAL_CHANGE_LOG_OVERRIDE_LINKS = Context.get_current_context().data.get('OfficialLink')
# endregion

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
        self.__manifest = self.fetch_manifest()
        self.__latest_development_version_id = self.__manifest['latest']['snapshot']
        self.__latest_release_version_id = self.__manifest['latest']['release']
        self.__manifest_versions = self.__manifest.get('versions', [])
        logger.info(f"最新快照版:{self.__latest_development_version_id}, "
                    f"最新正式版:{self.__latest_release_version_id}")
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
        logger.warning(f"版本 {version_id} 不存在于版本列表中")
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

# region 脚本接口


@script('ServerJar')
def get_server_jar_script(card, **_) -> str:
    """获取该卡片MC版本服务器端 jar 包下载链接"""
    version = MCVM.get(card['version-id'])
    assert version is not None, f"无法获取版本 {card['version-id']} 的信息，无法获取服务器端下载链接"
    return version.server_jar_url


@script('MainPageVersions')
def main_page_versions_script(page_area, **_) -> str:
    """获取特定区域的最新 MC 版本的卡片引用"""
    latest_version = MCVM.get_latest_version(version_type='any')
    assert latest_version is not None, "无法获取最新版本信息"
    if page_area == 'new':
        return f"{latest_version.id} | latest = true | s = false"
    else:
        if latest_version.type == VersionType.RELEASE:
            return ''
        latest_development_version = MCVM.get_latest_version(version_type='release')
        assert latest_development_version is not None, "无法获取最新开发版本信息"
        return f"{latest_development_version.id} | latest = true"


@script('VersionLatestList')
def version_latest_list_script(**_):
    """获取最新版本展示列表（用于新闻主页精简版）"""
    context = Context.get_current_context()
    library = context.project.base_library
    components = context.components
    code = ''
    version_type: Literal['development', 'release']
    for version_type in ['release', 'development']:
        if latest_version := MCVM.get_latest_version(version_type=version_type):
            version_card = library.get_card(latest_version.id, False)
            code += components['VersionLinks/Latest'].toxaml(card=version_card)
    return code


@script('VersionArchiveList')
def version_archive_list_script(cat_name, card, **_):
    context = Context.get_current_context()
    components = context.components
    cat_name = format_code(code=cat_name, data=card)
    cards = list(filter(lambda c: isinstance(c.get('cats'), list)
                                  and cat_name in c.get('cats'), context.project.get_all_card()))
    code = '<StackPanel Margin="8,0,8,0">'
    cards.sort(key=lambda c: MCVM.get_version_id_list().index(format_code(c['version-id'], data=c)))
    first_card_version_type = format_code(cards[0]['version-type-id'], cards[0])
    if len(cards) > 0 and first_card_version_type not in ['Release', 'April-Fools']:
        code += components['VersionLinks/Future'].toxaml(card={})
    for version_card in cards:
        if version_card.get('lack'):
            code += components['VersionLinks/Lack'].toxaml(card=version_card)
        else:
            code += components['VersionLinks/Common'].toxaml(card=version_card)
    code += '</StackPanel>'
    return code


@script('GetLink')
def get_link(link_type, card, link_key=None, **kwargs):
    name: str = card['version-id']
    name = format_code(name, card)
    if link_type == 'Official':
        return MCVM.get(name).change_log_url
    if card.get('wip') == 'true' and link_type != 'Official':
        return ''
    data = Context.get_current_context().data[f'{link_type}Link']
    if link_key:  # 如果指定查找键
        return data[link_key]
    return data.get(name, "")
# endregion
