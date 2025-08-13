from homepagebuilder.interfaces import script, config
from homepagebuilder.core.types import Context

def true_that(obj:str):
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, str):
        return obj.lower() == 'true'

PREFERENCE_LIST=[
    'skin',
    'not_finished',
    'beta',
    'domain'
]
DOMAIN = config('NewsHomepage.Domain', 'https://pcl.mcnews.thestack.top/', str)
if not DOMAIN.endswith('/'):
    DOMAIN += '/'

@script('PreferenceUrl')
def get_preferece_url(context:'Context', *_args, **_kwargs):
    settings = context.setter.toProperties()
    url = DOMAIN
    if true_that(settings.get('LightEdition', False)):
        url += 'Light'
    args = []
    args.append('beta=true')
    if true_that(settings.get('SkinNewra', False)):
        args.append('skin=newra')
    if true_that(settings.get('HideTranslating', False)):
        args.append('not_finished=false')
    if len(args) > 0:
        url += '?' + '&amp;'.join(args)
    return url