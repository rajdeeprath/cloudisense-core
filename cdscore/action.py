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

import urllib
import logging
import json
from tornado.concurrent import asyncio
from typing import Text, List,NamedTuple
from tornado.httpclient import AsyncHTTPClient
from tornado.web import HTTPError, MissingArgumentError
from pathlib import Path


from cdscore import types
from cdscore.constants import *
from cdscore.event import EventType, StartLogRecordingEvent, StopLogRecordingEvent
from cdscore.constants import SMTP_MAILER_MODULE, TOPIC_LOG_ACTIONS, FILE_MANAGER_MODULE, LOG_MANAGER_MODULE
from cdscore.abstracts import IFileSystemOperator, IntentProvider, IMailer, TargetProcess
from cdscore.helpers import *




logger = logging.getLogger(__name__)    


ACTION_PREFIX = "action_"

ACTION_TEST_NAME = ACTION_PREFIX + "test"

ACTION_GET_SOFTWARE_VERSION_NAME = ACTION_PREFIX + "get_software_version"

ACTION_HTTP_GET_NAME = ACTION_PREFIX + "http_get"

ACTION_UPDATE_SOFTWARE_NAME = ACTION_PREFIX + "update_software"

ACTION_REBOOT_SYSTEM_NAME = ACTION_PREFIX + "reboot_system"

ACTION_GET_SYSTEM_TIME_NAME = ACTION_PREFIX + "get_system_time"

ACTION_FORCE_GARBAGE_COLLECTION_NAME = ACTION_PREFIX + "force_garbage_collection"

ACTION_GET_SYSTEM_STATS_NAME = ACTION_PREFIX + "get_system_stats"

ACTION_GET_MEMORY_STATS_NAME = ACTION_PREFIX + "get_memory_stats"

ACTION_GET_CPU_STATS_NAME = ACTION_PREFIX + "get_cpu_stats"

ACTION_START_LOG_RECORDING_NAME = ACTION_PREFIX + "start_log_recording"

ACTION_STOP_LOG_RECORDING_NAME = ACTION_PREFIX + "stop_log_recording"

ACTION_INVOKE_ON_TARGET_NAME = ACTION_PREFIX + "fulfill_target_request"

ACTION_RESTART_TARGET_NAME = ACTION_PREFIX + "restart_target"

ACTION_STOP_TARGET_NAME = ACTION_PREFIX + "stop_target"

ACTION_START_TARGET_NAME = ACTION_PREFIX + "start_target"

ACTION_LIST_TARGETS_NAME = ACTION_PREFIX + "list_targets"

ACTION_SUBSCRIBE_CHANNEL_NAME = ACTION_PREFIX + "subscribe_channel"

ACTION_UNSUBSCRIBE_CHANNEL_NAME = ACTION_PREFIX + "unsubscribe_channel"

ACTION_REMOVE_CHANNEL_NAME = ACTION_PREFIX + "remove_channel"

ACTION_CREATE_CHANNEL_NAME = ACTION_PREFIX + "create_channel"

ACTION_PUBLISH_CHANNEL_NAME = ACTION_PREFIX + "publish_channel"

ACTION_RUN_DIAGNOSTICS_NAME = ACTION_PREFIX + "run_diagnostics"

ACTION_SEND_MAIL_NAME = ACTION_PREFIX + "send_mail"

ACTION_WRITE_LOG_CHUNKS_NAME = ACTION_PREFIX + "write_log_chunks"

ACTION_BOT_NOTIFY_NAME = ACTION_PREFIX + "bot_notify"

ACTION_UPDATE_ACCESSIBLE_PATHS_NAME = ACTION_PREFIX + "update_accessible_paths"




class ActionResponse(NamedTuple):
    data:object = None
    events:List[EventType] = []
    pass



class Action(object):
    '''
    classdocs
    '''
    
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
    return [ActionGetSoftwareVersion(), ActionRebootSystem(), ActionGetSystemTime(), 
            ActionForceGarbageCollection(), ActionGetSystemStats(), ActionGetMemoryStats(), 
            ActionGetCPUStats(), ActionStartLogRecording(), ActionStopLogRecording(), ActionFulfillTargetRequest(), 
            ActionStartTarget(), ActionListTargets(), ActionStopTarget(), ActionRestartTarget(), 
            ActionSubcribeChannel(), ActionUnSubcribeChannel(), ActionCreateChannel(), 
            ActionRemoveChannel(), ActionPublishChannel(), ActionRunDiagonitics(), ActionUnUpdateSoftwre(), 
            ActionHttpGet(), ActionSendMail(), ActionTest(), ActionWriteLogChunks(), ActionBotNotify(),
            ActionUpdateAccessiblePaths()]




def builtin_action_names() -> List[Text]:
    return [a.name() for a in builtin_actions()]




def action_from_name(name:Text) -> Action:
    defaults = {a.name(): a for a in builtin_actions()}
    if name in defaults:
        return defaults.get(name)
    
    return None



'''
Retreives program version
'''
class ActionGetSoftwareVersion(Action):


    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_GET_SOFTWARE_VERSION_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        __sysmon = None
        if modules.hasModule(SYSTEM_MODULE):
                __sysmon = modules.getModule(SYSTEM_MODULE)
                __ver = __sysmon.get_version()
                return ActionResponse(data = __ver, events=[])
        else:
                raise ModuleNotFoundError("`"+SYSTEM_MODULE+"` module does not exist")
        pass
         
    
    



'''
Reboots system [ needs admin rights to the python script ]
'''
class ActionRebootSystem(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_REBOOT_SYSTEM_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        __sysmon = None
        
        if modules.hasModule(SYSTEM_MODULE):
            __sysmon = modules.getModule(SYSTEM_MODULE)
            result =  __sysmon.rebootSystem()
            return ActionResponse(data = result, events=[])
        else:
            raise ModuleNotFoundError("`"+SYSTEM_MODULE+"` module does not exist")
        pass
        
         



'''
Triggers garbage collector on python
'''
class ActionForceGarbageCollection(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_FORCE_GARBAGE_COLLECTION_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        __sysmon = None
        
        if modules.hasModule("sysmon"):
            __sysmon = modules.getModule("sysmon")        
            __sysmon.force_gc()
            return ActionResponse(data = None, events=[])
        else:
            raise ModuleNotFoundError("`sysmon` module does not exist")
        
    
    
    
'''
Retreives system time
'''
class ActionGetSystemTime(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_GET_SYSTEM_TIME_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        __sysmon = None
        
        if modules.hasModule(SYSTEM_MODULE):
            __sysmon = modules.getModule(SYSTEM_MODULE) 
            result =  __sysmon.get_system_time()
            return ActionResponse(data = result, events=[])
        else:
            raise ModuleNotFoundError("`"+SYSTEM_MODULE+"` module does not exist")
        pass       
 
 
 
 
'''
Retreives system stats
'''
class ActionGetSystemStats(Action):
    
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_GET_SYSTEM_STATS_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        __sysmon = None
        
        if modules.hasModule(SYSTEM_MODULE):
            __sysmon = modules.getModule(SYSTEM_MODULE)        
            result =  __sysmon.get_last_system_stats_snapshot()
            return ActionResponse(data = result, events=[])
        else:
            raise ModuleNotFoundError("`"+SYSTEM_MODULE+"` module does not exist")
        
    

'''
Retreives memory stats
'''
class ActionGetMemoryStats(Action):
    
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_GET_MEMORY_STATS_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        __sysmon = None
        
        if modules.hasModule(SYSTEM_MODULE):
            __sysmon = modules.getModule(SYSTEM_MODULE)
            result =  __sysmon.get_memory_stats()
            await asyncio.sleep(.5)
            return ActionResponse(data = result, events=[])
        else:
            raise ModuleNotFoundError("`"+SYSTEM_MODULE+"` module does not exist")
    
    
    
'''
Retreives cpu stats
'''
class ActionGetCPUStats(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_GET_CPU_STATS_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        __sysmon = None
        
        if modules.hasModule(SYSTEM_MODULE):
            __sysmon = modules.getModule(SYSTEM_MODULE)        
            result =  __sysmon.get_cpu_stats()
            await asyncio.sleep(.5)
            return ActionResponse(data = result, events=[])
        else:
            raise ModuleNotFoundError("`"+SYSTEM_MODULE+"` module does not exist")
        
    
    




class ActionFulfillTargetRequest(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_INVOKE_ON_TARGET_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        __delegate = None
        
        if modules.hasModule(TARGET_DELEGATE_MODULE):
            __delegate = modules.getModule(TARGET_DELEGATE_MODULE)
            if(len(params)<1):
                raise Exception("Minimum of one parameter is required for this method call")            
            command = params["command"]
            del params["command"]
            result =  await __delegate.fulfillRequest(command, params)
            return ActionResponse(data = result, events=[])
        else:
            raise ModuleNotFoundError("`"+TARGET_DELEGATE_MODULE+"` module does not exist")
        pass
        
    
    


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
        
    
    


class ActionRunDiagonitics(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_RUN_DIAGNOSTICS_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        raise NotImplementedError()
        #return ActionResponse(data = None, events=[])
    
    

class ActionStartLogRecording(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_START_LOG_RECORDING_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        __logmon = None
        
        if modules.hasModule(LOG_MANAGER_MODULE):
            __logmon = modules.getModule(LOG_MANAGER_MODULE)
            handler = params["handler"]
            log_name = params["name"] # log name
            log_info = __logmon.get_log_info(log_name)
            
            if hasattr(handler, 'id') and "logrecordings" in handler.liveactions:
                rule_id = handler.id + '-' + log_name
                
                if rule_id in handler.liveactions['logrecordings']:
                    raise LookupError("log recording is already active for this log")
                
                topic_path = log_info["topic_path"]
                topic_path = topic_path.replace("logging", "logging/chunked") if 'logging/chunked' not in topic_path else topic_path
                filepath = log_info["log_file_path"]
                rule = buildLogWriterRule(rule_id, topic_path, filepath) #Dynamic rule generation
                
                # tell logmon to enable chunk generation
                __logmon.enable_chunk_generation(log_name)
                
                # store reference on client handler
                handler.liveactions['logrecordings'].add(rule_id) 
                event = StartLogRecordingEvent(topic=TOPIC_LOG_ACTIONS, data=rule)
                return ActionResponse(data = rule_id, events=[event])
        else:
            raise ModuleNotFoundError("`"+LOG_MANAGER_MODULE+"` module does not exist")
        
        




class ActionStopLogRecording(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_STOP_LOG_RECORDING_NAME
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        __logmon = None
        
        if modules.hasModule(LOG_MANAGER_MODULE):
            __logmon = modules.getModule(LOG_MANAGER_MODULE)
            handler = params["handler"]
            
            if hasattr(handler, 'id'):
                rule_id:str = params["rule_id"]
                log_name:str = rule_id.replace(handler.id + "-", "")
                log_info = __logmon.get_log_info(log_name)
                topic_path = log_info["topic_path"]
                topic_path = topic_path.replace("logging", "logging/chunked") if 'logging/chunked' not in topic_path else topic_path
                filepath = log_info["log_file_path"]
                
                if rule_id not in handler.liveactions['logrecordings']:
                    raise LookupError("There is no log recording active for this log.")
                
                # We dont tell logmon to disable chunk generation because theer might be others who still want chunk generation
                #__logmon.disable_chunk_generation(log_name)
                
                # remove reference on client handler
                handler.liveactions['logrecordings'].remove(rule_id) 
                rule = buildLogWriterRule(rule_id, topic_path, filepath)
                
            event = StopLogRecordingEvent(topic=TOPIC_LOG_ACTIONS, data=rule)
            return ActionResponse(data = rule_id, events=[event])
        
        else:
            raise ModuleNotFoundError("`"+LOG_MANAGER_MODULE+"` module does not exist")
        



class ActionWriteLogChunks(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_WRITE_LOG_CHUNKS_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        __filenamanger = None
        
        if modules.hasModule(FILE_MANAGER_MODULE):
            __filenamanger = modules.getModule(FILE_MANAGER_MODULE)
            chunks = params["__event__"]["data"]["chunk"]
            path = params["destination"]
            await __filenamanger.write_file_stream(path, chunks)
            return ActionResponse(data = None, events=[])
        else:
            raise ModuleNotFoundError("`"+FILE_MANAGER_MODULE+"` module does not exist")
            



class ActionListTargets(Action):

    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_LIST_TARGETS_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:

        allmodules = modules.getModules()    
        service_modules = []    
        for mod in allmodules:
            if isinstance(mod, TargetProcess):
                service_modules.append(mod.getAlias())

        return ActionResponse(data = service_modules, events=[])




class ActionStartTarget(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_START_TARGET_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        
        if "module" not in  params:
            raise MissingArgumentError("Module name not provided")
        
        module_alias = params["module"]

        allmodules = modules.getModules()
        for module_instance in allmodules:
            if isinstance(module_instance, TargetProcess):
                if module_instance.getAlias() == module_alias:
                    await module_instance.start_proc()
                    return ActionResponse(data = None, events=[])
        
        
        raise ModuleNotFoundError("No module by alias`"+module_alias+"` was found in the system")
        
    




class ActionStopTarget(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_STOP_TARGET_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        if "module" not in  params:
            raise MissingArgumentError("Module name not provided")
        
        module_alias = params["module"]

        allmodules = modules.getModules()
        for module_instance in allmodules:
            if isinstance(module_instance, TargetProcess):
                if module_instance.getAlias() == module_alias:
                    await module_instance.stop_proc()
                    return ActionResponse(data = None, events=[])
        
        
        raise ModuleNotFoundError("No module by alias`"+module_alias+"` was found in the system")





class ActionRestartTarget(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_RESTART_TARGET_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        if "module" not in  params:
            raise MissingArgumentError("Module name not provided")
        
        module_alias = params["module"]

        allmodules = modules.getModules()
        for module_instance in allmodules:
            if isinstance(module_instance, TargetProcess):
                if module_instance.getAlias() == module_alias:
                    await module_instance.restart_proc()
                    return ActionResponse(data = None, events=[])
        
        
        raise ModuleNotFoundError("No module by alias`"+module_alias+"` was found in the system")
        
        
    
    
    
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
            __pubsubhub = modules.getModule(PUBSUBHUB_MODULE)
        
        if(__pubsubhub != None):
            handler = params["handler"]
            topic = params["topic"]
            # finalparams = params.copy() 
            #if(len(finalparams)>1):
            #    finalparams = finalparams[2:]
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
            __pubsubhub = modules.getModule("pubsub")
            handler = params["handler"]
            topic = params["topic"]       
            __pubsubhub.unsubscribe(topic, handler)
            return ActionResponse(data = None, events=[])
        else:
            raise ModuleNotFoundError("`PubSub` module does not exist")
        
        



class ActionUnUpdateSoftwre(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_UPDATE_SOFTWARE_NAME
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        pass
        




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




class ActionSendMail(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_SEND_MAIL_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        
        
        if "subject" in params:
            subject = params["subject"]
        elif "__event__" in params:
            subject = "Event notification for " + params["__event__"]["name"]
        else:
            subject = "Send mail action!"
            
        
        if "content" in params:
            content = params["content"]
        elif "__event__" in params:
            content = "Event data for " + params["__event__"]["name"]
            content = content + "\n\r"
            content = "Event data for " + json.dumps(params["__event__"]["data"])
        else:
            content = "Send mail action content"
            content = content + "\n\r"
            if params != None:
                content = "Data " + json.dumps(params)
            else:
                content = " No content"
                
        
        __mailer:IMailer = None
        
        if modules.hasModule(SMTP_MAILER_MODULE):
            __mailer = modules.getModule(SMTP_MAILER_MODULE)
            if(__mailer != None):
                result = await __mailer.send_mail(subject, content)
                return ActionResponse(data = result, events=[])
            else:
                raise ModuleNotFoundError("`"+SMTP_MAILER_MODULE+"` module does not exist")
        else:
            raise ModuleNotFoundError("`"+SMTP_MAILER_MODULE+"` module does not exist")






    



class ActionBotNotify(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_BOT_NOTIFY_NAME
    
    
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        service_bot = None
        
        if modules.hasModule("service_bot"):
            service_bot = modules.getModule("service_bot")
            
            message:Text = None
            if "message" in params:
                message = params["message"]
            elif "__event__" in params and "message" in params["__event__"]["data"]:
                message = params["__event__"]["data"]["message"]
            
            if message != None:            
                await service_bot.send_notification(message)
            else:
                logger.warn("nothing to send")
                
            return ActionResponse(data = None, events=[])
        else:
            raise ModuleNotFoundError("`service_bot` module does not exist")
        pass








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



'''
Update accessible paths list in filesystem module
'''
class ActionUpdateAccessiblePaths(Action):
    
    
    '''
    Abstract method, must be defined in concrete implementation. action names must be unique
    '''
    def name(self) -> Text:
        return ACTION_UPDATE_ACCESSIBLE_PATHS_NAME
    
    
    
    '''
    async method that executes the actual logic
    '''
    async def execute(self, requester:IntentProvider, modules:types.Modules, params:dict=None) -> ActionResponse:
        __filemanager:IFileSystemOperator = modules.getModule(FILE_MANAGER_MODULE)
        path:Path = Path(params["path"])
        result = await __filemanager.add_accessible_path(path)
        return ActionResponse(data = result, events=[])