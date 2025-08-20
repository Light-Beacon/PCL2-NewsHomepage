from homepagebuilder.interfaces import config, Logger
from homepagebuilder.core.types import Context

_PROTOCOL = config('NewsHomepage.Protocol', 'https', str)
_DOMAIN = config('NewsHomepage.Domain', 'pcl.mcnews.thestack.top', str)
_PORT = config('NewsHomepage.Port', '443', str)

logger = Logger('Domain')

def _get_disp_port():
    if config('NewsHomepage.HidePort', True, bool):
        return ''
    if _PROTOCOL == 'http' and _PORT == '80':
        return ''
    if _PROTOCOL == 'https' and _PORT == '443':
        return ''
    return ':' + _PORT

_DISP_PORT_STR = _get_disp_port()

def get_doamin_url(context:Context):
    display_port = _DISP_PORT_STR
    if config('NewsHomepage.UseRuntimePort', False):
        display_port = ':' + context.builder.get_data('server.port')
    if not display_port:
        logger.warning('无效的端口')
    return f"{_PROTOCOL}://{_DOMAIN}{display_port}/"