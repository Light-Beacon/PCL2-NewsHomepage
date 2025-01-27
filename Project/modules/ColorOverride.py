from homepagebuilder.interfaces.Events import on, ResultOverride
from homepagebuilder.core.config import enable_by_config

COLOR_MAPPING = {
    1: None,
    2: "#9B2A2A",
    3: "#C05252",
    4: "#D56B6B",
    5: "#E18E8E",
    #6: "#E18E8E",
    #7: "#E18E8E",
}

@on('page.generate.return')
@enable_by_config('news.replacecolor')
def script(*args, **kwargs):
    result:str = kwargs['result']
    for num, color in COLOR_MAPPING.items():
        if not color:
            continue
        result = result.replace(f"{{DynamicResource ColorBrush{num}}}",color)
    raise ResultOverride(result)
