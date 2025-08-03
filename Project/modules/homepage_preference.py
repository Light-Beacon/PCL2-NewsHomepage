from homepagebuilder.interfaces import script
from homepagebuilder.core.types import Context

def true_that(obj:str):
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, str):
        return obj.lower() == 'true'

@script('PreferenceUrl')
def get_preferece_url(context:'Context', *_args, **_kwargs):
    settings = context.setter.toProperties()
    url = 'https://pcl.mcnews.thestack.top/'
    if true_that(settings.get('LightEdition', False)):
        url += 'Light'
    args = []
    if true_that(settings.get('SkinNewra', False)):
        args.append('skin=newra')
    if true_that(settings.get('HideTranslating', False)):
        args.append('not_finished=false')
    if len(args) > 0:
        url += '?' + '&amp;'.join(args)
    return url