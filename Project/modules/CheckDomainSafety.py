from homepagebuilder.interfaces import config
from homepagebuilder.interfaces.Events import on, ResultOverride

@on('page.generate.start')
def script(_page,env):
    if mod_domain := env.setter.override.get('domain'):
        if mod_domain not in config('safe_domains',['news.bugjump.net']):
            raise ResultOverride('')
