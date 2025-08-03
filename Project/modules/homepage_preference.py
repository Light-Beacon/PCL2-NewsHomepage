from homepagebuilder.interfaces import script
from homepagebuilder.core.types import Context

@script('PreferenceUrl')
def get_preferece_url(context:'Context', *_args, **_kwargs):
    settings = context.setter.toProperties()
    url = 'https://pcl.mcnews.thestack.top/'
    if settings.get('LightEdition', False):
        url += 'Light'
    args = []
    if settings.get('SkinNewra', False):
        args.append('skin=newra')
    if settings.get('HideTranslating', False):
        args.append('not_finished=false')
    if len(args) > 0:
        url += '?' + '&amp;'.join(args)
    return url