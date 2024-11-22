'''
 * Copyright (C) 2019-2025 Rajdeep Rath (Cloudisense-core - cdscore)
 * This library (.py files) is intended for use solely within the Cloudisense program and its supporting codebases.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.   
'''

from typing import List, Text


class Modules(object):
    
    def __init__(self):
        
        self.__registry = {}        
        pass
    
    
    def registerModule(self, name, reference):
        if name not in self.__registry.keys():
            self.__registry[name] = reference;
        pass
    
    
    def deregisterModule(self, name):
        if name in self.__registry.keys():
            del self.__registry[name]
        pass
    
    
    def getModule(self, name):
        if name in self.__registry.keys():
            return self.__registry[name]
        else:
            return None
        pass
    
    
    def hasModule(self, name):        
        if name in self.__registry.keys():
            return True
        else:
            return False
        
        
    def getModules(self)->List:        
        return self.__registry.values()
        pass


    def getModuleNames(self)->List[Text]:
        return self.__registry.keys()
