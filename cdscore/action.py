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

import urllib
import logging
from typing import Text, List,NamedTuple
from tornado.httpclient import AsyncHTTPClient
from tornado.web import HTTPError


from cdscore import types
from cdscore.constants import *
from cdscore.event import EventType
from cdscore.abstracts import IPubSubHub, IntentProvider
from cdscore.helpers import *




logger = logging.getLogger(__name__)    


ACTION_PREFIX = "action_"

ACTION_TEST_NAME = ACTION_PREFIX + "test"

ACTION_HTTP_GET_NAME = ACTION_PREFIX + "http_get"

ACTION_SUBSCRIBE_CHANNEL_NAME = ACTION_PREFIX + "subscribe_channel"

ACTION_UNSUBSCRIBE_CHANNEL_NAME = ACTION_PREFIX + "unsubscribe_channel"

ACTION_REMOVE_CHANNEL_NAME = ACTION_PREFIX + "remove_channel"

ACTION_CREATE_CHANNEL_NAME = ACTION_PREFIX + "create_channel"

ACTION_PUBLISH_CHANNEL_NAME = ACTION_PREFIX + "publish_channel"




class ActionResponse(NamedTuple):
    data:object = None
    events:List[EventType] = []
    pass



class Action(object):
    '''
    classdocs
    '''
    
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        raise NotImplementedError
    
    
    
    '''
    Declares whether the action is asynchronous or synchronous
    '''
    def is_async(self) -> bool:
        return True
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        return ActionResponse()
    
    
    
    '''
    spits out string name of action
    '''
    def __str__(self) -> Text:
        return "Action('{}')".format(self.name())
    



'''
Returns instances of builtin actions
'''
def builtin_actions() -> List[Action]:
    return [ActionSubcribeChannel(), ActionUnSubcribeChannel(), 
            ActionCreateChannel(), ActionRemoveChannel(), ActionPublishChannel(), 
            ActionHttpGet(), ActionTest()]




def builtin_action_names() -> List[Text]:
    return [a.name() for a in builtin_actions()]




def action_from_name(name:Text) -> Action:
    defaults = {a.name(): a for a in builtin_actions()}
    if name in defaults:
        return defaults.get(name)
    
    return None




class ActionPublishChannel(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_PUBLISH_CHANNEL_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        __pubsubhub = None
        
        if modules.hasModule(PUBSUBHUB_MODULE):
            __pubsubhub = modules.getModule(PUBSUBHUB_MODULE)
            handler = params["handler"] 
            topicname = params["topic"]  
            message = params["message"]        
            __pubsubhub.publish(topicname, message, handler)
            return ActionResponse(data = None, events=[])
        else:
            raise ModuleNotFoundError("`"+PUBSUBHUB_MODULE+"` module does not exist")




class ActionCreateChannel(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_CREATE_CHANNEL_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        __pubsubhub = None
        
        if modules.hasModule(PUBSUBHUB_MODULE):
            __pubsubhub = modules.getModule(PUBSUBHUB_MODULE)
            channel_info = params["channel_info"]  
            __pubsubhub.createChannel(channel_info)
            return ActionResponse(data = None, events=[])
        else:
            raise ModuleNotFoundError("`"+PUBSUBHUB_MODULE+"` module does not exist")
        
    
    

class ActionRemoveChannel(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_REMOVE_CHANNEL_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        __pubsubhub = None
        
        if modules.hasModule(PUBSUBHUB_MODULE):
            __pubsubhub = modules.getModule(PUBSUBHUB_MODULE)
            channel_name = params["topic"]        
            __pubsubhub.removeChannel(channel_name)
            return ActionResponse(data = None, events=[])
        else:
            raise ModuleNotFoundError("`"+PUBSUBHUB_MODULE+"` module does not exist")
        
 
    
class ActionSubcribeChannel(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_SUBSCRIBE_CHANNEL_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        __pubsubhub = None
        
        if modules.hasModule(PUBSUBHUB_MODULE):
            __pubsubhub:IPubSubHub = modules.getModule(PUBSUBHUB_MODULE)
        
        if(__pubsubhub != None):
            handler = params["handler"]
            topic = params["topic"]
            __pubsubhub.subscribe(topic, handler)
            return ActionResponse(data = None, events=[])
        else:
            raise ModuleNotFoundError("`"+PUBSUBHUB_MODULE+"` module does not exist")
        




class ActionUnSubcribeChannel(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_UNSUBSCRIBE_CHANNEL_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        __pubsubhub = None
        
        if modules.hasModule("pubsub"):
            __pubsubhub:IPubSubHub = modules.getModule("pubsub")
            handler = params["handler"]
            topic = params["topic"]       
            __pubsubhub.unsubscribe(topic, handler)
            return ActionResponse(data = None, events=[])
        else:
            raise ModuleNotFoundError("`PubSub` module does not exist")
        
              




class ActionHttpGet(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_HTTP_GET_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        
        url = params["url"]
        queryparams = params["queryparams"]
        querystring = urllib.parse.urlencode(queryparams)
        method = "GET"                
        
        http_client = AsyncHTTPClient()        
        url = url + querystring
        response = await http_client.fetch(url, method=method, headers=None)
        logger.debug("response = %s", str(response))
        if response.code == 200:
            result = str(response.body, 'utf-8')
            return ActionResponse(data = result, events=[])
        raise HTTPError("Unable to make request to url " + url)




class ActionTest(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_TEST_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    #@authorize__action(requiredrole="admin")
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        return ActionResponse(data = None, events=[])     



