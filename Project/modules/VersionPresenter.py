from bs4 import BeautifulSoup
from homepagebuilder.interfaces import page_class_handles, require
from homepagebuilder.core.page import CodeBasedPage
from homepagebuilder.core.types import Context
from homepagebuilder.interfaces import  require, script

# region presenter
presenter_module = require('markdown_presenter')
parsers_module = require('markdown_parsers')
create_node = parsers_module.create_node
MarkdownPresenter = presenter_module.MarkdownPresenter

class VersionPresenter(MarkdownPresenter):
    def html2xaml(self, html, context:Context):
        soup = BeautifulSoup(html,'html.parser')
        card_list = []
        buffer = ''
        current_heading = ''
        for tag in soup.find_all(recursive=False):
            if tag.name == 'h2':
                if len(buffer) > 0:
                    card_list.append((current_heading, buffer))
                current_heading = tag.contents[0]
                buffer = ''
            else:
                buffer += create_node(tag,context,[]).convert()
        if len(buffer) > 0:
            card_list.append((current_heading, buffer))
        xaml = ''
        for cardname, cardcontent in card_list:
            xaml += f'''
            <local:MyCard Title="{cardname}" Style="{{StaticResource Card}}" CanSwap="True" IsSwaped="false">
            <StackPanel Margin="20,28,20,10">
            <FlowDocumentScrollViewer >
            <FlowDocument>
            {cardcontent}
            </FlowDocument>
            </FlowDocumentScrollViewer >
            </StackPanel>
            </local:MyCard>
            '''
        context.used_resources.add('Card')
        context.used_resources.add('ContentStack')
        return xaml

presenter = VersionPresenter()

@script('VersionPresenter')
def version_presenter(card,context,**_):
    md = card['markdown']   
    return presenter.convert(md,context)