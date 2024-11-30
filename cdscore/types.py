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
