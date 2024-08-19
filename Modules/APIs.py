from Interfaces import page_class_handles, PageBase

@page_class_handles('apis/status')
class StatusPage(PageBase):

    @property
    def display_name(self):
        return 'api/status'
    
    def generate(self, *args, **kwargs):
        return 'ok'