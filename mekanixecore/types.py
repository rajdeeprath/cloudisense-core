'''
This file is part of `cloudmechanik` 
Copyright 2018 Connessione Technologies

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
