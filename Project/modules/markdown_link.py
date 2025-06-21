from homepagebuilder.interfaces import require

PCL_BLOCK_PACK = 'pack://application:,,,/images/Blocks/'
LOGO_MAPPING = {
        'command_block': PCL_BLOCK_PACK + 'CommandBlock.png',
        'cobblestone': PCL_BLOCK_PACK + 'Cobblestone.png',
        'gold_block': PCL_BLOCK_PACK + 'GoldBlock.png',
        'grass_block': PCL_BLOCK_PACK + 'Grass.png',
        'grass_path': PCL_BLOCK_PACK + 'GrassPath.png',
        'anvil': PCL_BLOCK_PACK + 'Anvil.png',
        'redstone_block': PCL_BLOCK_PACK + 'RedstoneBlock.png',
        'redstone_lamp_on': PCL_BLOCK_PACK + 'RedstoneLampOn.png',
        'redstone_lamp_off': PCL_BLOCK_PACK + 'RedstoneLampOff.png',
        'egg': PCL_BLOCK_PACK + 'Egg.png',
        'fabric': PCL_BLOCK_PACK + 'Fabric.png',
        'neoforge': PCL_BLOCK_PACK + 'NeoForge.png'
}

mdp = require('markdown_parsers')

@mdp.handles('listlink')
class MyListItemLink(mdp.WPFUIContainer):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.title = self.attrs.get('title', '')
        self.href = self.attrs.get('href', '')
        self.info = self.attrs.get('info', '')
        self.logo = self.attrs.get('logo', self.attrs.get('icon', 'command_block'))
        self.logo = LOGO_MAPPING.get(self.logo, self.logo)
        self.logo_scale = self.attrs.get('logo_scale', 1.0)
        self.tooltip = self.attrs.get('tooltip')

    @property
    def component_name(self) -> str:
        return 'Elements/MarkdownMyListItemLink'

    def get_replacement(self):
        return {
            'title': self.title,
            'href': self.href,
            'info': self.info,
            'logo': self.logo,
            'logo_scale': self.logo_scale,
            'tooltip': self.tooltip
        }