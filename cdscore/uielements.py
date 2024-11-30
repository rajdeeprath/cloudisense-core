# Copyright © 2024 Rajdeep Rath. All Rights Reserved.
#
# This codebase is open-source and provided for use exclusively with the Cloudisense platform,
# as governed by its End-User License Agreement (EULA). Unauthorized use, reproduction,
# or distribution of this code outside of the Cloudisense ecosystem is strictly prohibited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# A copy of the License is available at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# This code may include third-party open-source libraries subject to their respective licenses.
# Such licenses are referenced in the source files or accompanying documentation.
#
# For questions or permissions beyond the scope of this notice, please contact Rajdeep Rath.

from builtins import str
from typing import Dict, List



class ActionItemType(object):

        __NUMBER = "number",
        __STRING = "string",
        __BOOLEAN = "boolean"
        __OBJECT = "object"
        __LIST = "list"

        @staticmethod
        def NUMBER():
            return ActionItemType.__NUMBER[0]
        
        @staticmethod
        def STRING():
            return ActionItemType.__STRING[0]
        
        @staticmethod
        def BOOLEAN():
            return ActionItemType.__BOOLEAN[0]
        
        @staticmethod
        def OBJECT():
            return ActionItemType.__OBJECT[0]
        
        @staticmethod
        def LIST():
            return ActionItemType.__LIST[0]


class ActionParamValidation(object):


    def __init__(self, required:bool=False, regex:str=None):
        '''
        Constructor
        '''
        
        self.__regex:str = regex
        self.__required:bool = required
    

    @property
    def regex(self) ->str:
        return self.__regex
        
        
    @regex.setter
    def name(self, _regex:str)->None:
        self.__regex = _regex

    
    @property
    def required(self) ->bool:
        return self.__required
        
        
    @required.setter
    def name(self, _required:bool)->None:
        self.__required = _required


    @property
    def __deserialize__(self)->Dict:
        return {
            "required": self.required,
            "regex": self.regex
        }




class ActionItemParams(object):
    """
    A class used to represent an Animal

    ...

    Attributes
    ----------
    name : str
        the name of the parameter & label of the client side label
    type : str
        the data type fo the parameter (number|string|boolean|object|list)
    meta : str
        provides additional data about the type of data expected (text|textarea|email|number|option)    
    required : boolean
        Whether the parameter is required or not
    hint : str
        useful tip that can be provided by the client ui as placeholder or tooltip
    options : list
        list of options to allow selection from. This is for checkbox, radio & select type UI
    """

    
    def __init__(self, name:str=None, type:str=None, options:List = None, meta:str=None, hint:str="", validation:ActionParamValidation=None):
        '''
        Constructor
        '''

        self.__name:str = name
        self.__type:str = type
        self.__meta:str = meta
        self.__options:str = options
        self.__validation:ActionParamValidation = ActionParamValidation() if validation == None else validation
        self.__hint:str = hint
    

    @property
    def name(self) ->str:
        return self.__name
        
        
    @name.setter
    def name(self, _name:str)->None:
        self.__name = _name


    @property
    def type(self) ->str:
        return self.__type
        
        
    @type.setter
    def type(self, _type:str)->None:
        self.__type = _type
    
    
    @property
    def options(self) ->List:
        return self.__options
        
        
    @options.setter
    def options(self, _options:List)->None:
        self.__options = _options
    

    @property
    def meta(self) ->str:
        return self.__meta
        
        
    @meta.setter
    def meta(self, _meta:str)->None:
        self.__meta = _meta

    
    @property
    def validation(self) ->ActionParamValidation:
        return self.__validation
        
        
    @validation.setter
    def validation(self, _validation:ActionParamValidation)->None:
        self.__validation = _validation

    
    @property
    def hint(self) ->str:
        return self.__hint
        
        
    @hint.setter
    def hint(self, _hint:str)->None:
        self.__hint = _hint


    @property
    def __deserialize__(self)->Dict:
        return {
            "name": self.name,
            "type": self.type,
            "hint": self.hint,
            "meta": self.meta,
            "options": self.options,
            "validation": self.validation.__deserialize__
        }



class ActionItemData(object):

    def __init__(self, intent = "INTENT_NAME", params = list()):
        '''
        Constructor
        '''

        self.__intent:str = intent
        self.__params:List[ActionItemParams] = params

    
    @property
    def intent(self) ->str:
        return self.__intent
        
        
    @intent.setter
    def intent(self, _intent:str)->None:
        self.__intent = _intent
    

    @property
    def params(self) ->List[ActionItemParams]:
        return self.__params
        
        
    @params.setter
    def params(self, _params:List[ActionItemParams])->None:
        self.__params = _params


    @property
    def __deserialize__(self)->Dict:
        return {
            "intent": self.intent,
            "params": list(map(lambda param: param.__deserialize__, self.params))
        }



class ActionItem(object):

    
    def __init__(self, label = "Item", is_category = False, data:ActionItemData = None):
        '''
        Constructor
        '''

        self.__label:str = label
        self.__is_category:bool = is_category
        self.__data:ActionItemData = data
        self.__children:List[ActionItem] = list()
    

    @property
    def label(self) ->str:
        return self.__label
        
        
    @label.setter
    def label(self, _label:str)->None:
        self.__label = _label


    @property
    def is_category(self) ->bool:
        return self.__is_category
        
        
    @is_category.setter
    def is_category(self, _is_category:bool)->None:
        self.__is_category = _is_category
    

    @property
    def children(self) ->List:
        return self.__children
        
        
    @children.setter
    def children(self, _children:List)->None:
        self.__children = _children

    
    @property
    def data(self) ->ActionItemData:
        return self.__data
        
        
    @data.setter
    def data(self, _data:ActionItemData)->None:
        self.__data = _data


    @property
    def __deserialize__(self)->Dict:
        return {
            "label": self.label,            
            "is_category": self.is_category,
            "children": list(map(lambda child: child.__deserialize__, self.children)),
            "data": self.data.__deserialize__ if not self.is_category else None
        }