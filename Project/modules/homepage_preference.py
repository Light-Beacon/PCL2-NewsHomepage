from homepagebuilder.interfaces import script, config, require
from homepagebuilder.core.types import Context
from homepagebuilder.core.formatter import format_code
from typing import Type, TypeVar, Dict, List, Iterable, Optional
from enum import Enum

T = TypeVar('T')

def is_true(obj:str):
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, str):
        return obj.lower() == 'true' or obj == ''


GET_DOMAIN_URL = require('domain').get_doamin_url

class PrefenrenceEntry:
    __name:str
    __type:Type[T]
    __default:T
    
    def __init__(self, name:str, type:Type[T], default:T):
        self.__name = name
        self.__type = type
        self.__default = default
        
    @property
    def type(self):
        return self.__type
    
    @property
    def modify_method(self):
        return self.__method
    
    @property
    def name(self):
        return self.__name
    
    @property
    def default(self):
        return self.__default

    def get_element_names(self) -> List[str]:
        return []
    
    def get_element_name(cls) -> str:
        raise NotImplementedError()
    
    @classmethod
    def binding(cls, name) -> str:
         raise NotImplementedError()

    def get_value_from_save_page(self, settings):
        raise NotImplementedError()
    
    def convert_value(self, value):
        type = self.__type
        match type.__name__:
            case 'str':
                if isinstance(value, str):
                    return value
                else:
                    return str(value)
            case 'bool':
                if isinstance(value, str):
                    return value.lower() == 'true' or value == ''
                else:
                    return bool(value)
            case _:
                raise TypeError(type)

class PrefenrenceHiddenEntry(PrefenrenceEntry):
    def get_element_names(self):
        return []
    
    def get_element_name(cls, name:str) -> str:
        raise NotImplementedError()
    
    @classmethod
    def binding(cls, name):
         raise NotImplementedError()
     
    def get_value_from_save_page(self, settings):
        return settings.get(self.name, self.default)

class PrefenrenceChoiceEntry(PrefenrenceEntry):
    
    def __init__(self, name, type, default, values:List[T]):
        super().__init__(name, type, default)
        self.__values = values
    
    def get_element_names(self):
        return [self.get_element_name(value) for value in self.__values]
    
    def get_element_name(self, value):
        return self.get_element_name_by_value(self.name, value)
    
    @classmethod
    def get_element_name_by_value(cls, name, value):
        return name + value

    @classmethod
    def binding(cls, name):
        return f'<Binding Path="Checked" ElementName="{name}"/>'
    
    def get_value_from_save_page(self, settings):
        for value in self.__values:
            if is_true(settings.get(self.get_element_name(value))):
                return value
        return self.default

class PrefenrenceBoolEntry(PrefenrenceEntry):
    def get_element_names(self):
        return [self.get_element_name()]
    
    def get_element_name(self):
        return self.get_element_name_by_value(self.name)
    
    @classmethod
    def binding(cls, name):
        return f'<Binding Path="Checked" ElementName="{name}"/>'
    
    @classmethod
    def get_element_name_by_value(cls, name):
        return name
    
    def get_value_from_save_page(self, settings):
        return is_true(settings.get(self.get_element_name(), self.default))
    
class PrefenrenceResetEntry(PrefenrenceHiddenEntry):
    
    def __init__(self, name, type, default, reset_value):
        super().__init__(name, type, default)
        self.__reset_value = reset_value
    
    @property
    def reset_value(self):
        return self.__reset_value

class PreferenceManager:
    __entries:Dict[str, PrefenrenceEntry] = {}
    
    @classmethod
    def add_entries(cls, entries:Iterable[PrefenrenceEntry]):
        for entry in entries:
            cls.__entries[entry.name] = entry
    
    @classmethod
    def has(cls, item):
        if isinstance(item, str):
            return item in cls.__entries
        raise TypeError()
    
    @classmethod
    def get(cls, key:str, default = None):
        return cls.__entries.get(key, default)
    
    @classmethod
    def is_using(cls, context:'Context', key, value) -> bool:
        entry = cls.get(key)
        if not entry:
            return False
        settings = context.setter.toProperties().get('args',{})
        current_value = settings.get(key)
        if current_value is not None:
            if value == True:
                return is_true(current_value)
            else:
                return current_value == value
        else:
            return entry.default == value
    
    @classmethod
    def pref_length(cls):
        return len(cls.__entries)
    
    @classmethod
    def get_entries(self):
        return self.__entries.values()
    
PreferenceManager.add_entries([
    PrefenrenceChoiceEntry('Skin', str, 'basic',
                        ['basic', 'newra', 'classic',]),
    PrefenrenceChoiceEntry('Edition', str, 'standard',
                        ['standard', 'light']),
    PrefenrenceBoolEntry('HideWIP', bool, False),
    PrefenrenceBoolEntry('HideLaunchButton', bool, False),
    PrefenrenceBoolEntry('HideDownloadButton', bool, False),
    PrefenrenceBoolEntry('HideServerJarButton', bool, False),
    PrefenrenceResetEntry('mod', bool, False, True),
    PrefenrenceResetEntry('beta', bool, False, False)
])

@script('IsUsingPreset')
def get(content, context:'Context', *_args, **_kwargs):
    settings = context.setter.toProperties().get('args',{})
    if not is_true(settings.get('mod')):
        return content
    else:
        return ''

@script('PreferenceUrl')
def get_preferece_url(context:'Context', *_args, **_kwargs):
    settings = context.setter.toProperties().get('args',{})
    args = []
    url = GET_DOMAIN_URL(context)
    for entry in PreferenceManager.get_entries():
        value = entry.get_value_from_save_page(settings=settings)
        value = entry.convert_value(value)
        if isinstance(entry, PrefenrenceResetEntry):
            value = entry.reset_value
        if value != entry.default:
            if value == True:
                args.append(entry.name)
            else:
                args.append(entry.name + '=' + value)
    if len(args) > 0:
        url += '?' + '&amp;'.join(args)
    return url

@script('PreferenceSavePageUrl')
def preferece_save_page_url(context:'Context', *_args, **_kwargs):
    settings = context.setter.toProperties().get('args',{})
    string_format = '{}' + GET_DOMAIN_URL(context) + 'SaveChanges.json?'
    bindings = ''
    i = 0
    for entry in PreferenceManager.get_entries():
        if isinstance(entry, PrefenrenceHiddenEntry):
            value = settings.get(entry.name)
            if value is not None:
                value = entry.convert_value(value)
                string_format += f'{entry.name}={value}&amp;'
            continue
        for name in entry.get_element_names():
            string_format += f'{name}={{{i}}}&amp;'
            bindings += entry.binding(name)
            i += 1
    return f'<MultiBinding StringFormat="{string_format}">{bindings}</MultiBinding>'
    

@script('PreferenceRadioBox')
def preferece_radio(pref_key, pref_value, column, row, content, context:'Context', **_kwargs):
    data = {}
    data['column'] = column
    data['row'] = row
    data['content'] = content
    data['element_key'] = PrefenrenceChoiceEntry.get_element_name_by_value(pref_key, pref_value)
    data['check'] = PreferenceManager.is_using(context, pref_key, pref_value)
    return context.components['Preference/PreferenceRadioBox'].toxaml(data, context)

@script('PreferenceCheckBox')
def preferece_check(pref_key, content, context:'Context', **_kwargs):
    data = {}
    data['content'] = content
    data['element_key'] = PrefenrenceBoolEntry.get_element_name_by_value(pref_key)
    data['check'] = PreferenceManager.is_using(context, pref_key, True)
    return context.components['Preference/PreferenceCheckBox'].toxaml(data, context)