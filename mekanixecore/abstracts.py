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


import string
import os
import logging
import asyncio
from abc import abstractmethod
from builtins import int, str
from typing import List, Text, Callable, Dict
from abc import abstractmethod


from mekanixecore.event import EventType, EVENT_ANY
from mekanixecore.constants import TOPIC_ANY
from mekanixecore.rules import ReactionRule
from mekanixecore.types import Modules
from mekanixecore.uielements import ActionItem


class IEventDispatcher(object):
    
    def __init__(self, handler:Callable=None):
        super().__init__()
        self.__eventHandler = None if handler == None else handler
        pass
    
    
    @property
    def eventhandler(self) ->Callable:
        return self.__eventHandler
    
    @eventhandler.setter
    def eventhandler(self, handler:Callable) ->None:
        self.__eventHandler = handler
        

    async def dispatchevent(self, event:EventType) -> None:
        if self.__eventHandler:
            await self.__eventHandler(event)
        pass




class IFileSystemOperator(object):

    def add_accessible_path(self, path:str) ->None:
        raise NotImplementedError
    
    def get_accessible_paths(self)->List[str]:
        raise NotImplementedError    
    
    def get_exposable_accessible_paths(self)->List[str]:
        raise NotImplementedError
    
    def get_real_path(self, path:str)->str:
        raise NotImplementedError

    def browse_content(self, path)->List:
        raise NotImplementedError
    
    def deleteFile(self, path)->None:
        raise NotImplementedError
    
    def delete_directory(self, path)->None:
        raise NotImplementedError
    
    def make_downloadable_tmp_link(file_path:str)->None:
        raise NotImplementedError
    
    def handleUpload(self, chunk:bytes, tmp_buffer:bytes, permit:Text)->None:
        raise NotImplementedError
    
    @property
    def maxstreamsize(self):
        raise NotImplementedError
    
    def generateUploadPermit(self, upload_path:str, filename:str, filesize:int=0)->object:
        raise NotImplementedError
    
    def getUploadProgress(self, permit:Text)->int:
        raise NotImplementedError
    
    def handleUploadComplete(self, permit:Text, data, filename:str, args:Dict)->None:
        raise NotImplementedError
    
    def download_file_async(self, file_path:str, chunksize:int, callback:Callable)->None:
        raise NotImplementedError
    
    def readFile(self, filepath:str, base64Encoded:bool = False)->any:
        raise NotImplementedError
    
    def writeFile(self, filepath:str, content:str, reserved:bool = False, must_exist:bool = True, base64Encoded:bool = False)->None:
        raise NotImplementedError
    
    def append_allowed_download_paths(self, paths:List)->None:
        raise NotImplementedError




class ITaskExecutor(object):
    
    def __init__(self):
        super().__init__()
        pass    
    
    
    @property
    def taskexecutor(self):
        return self.__taskexecutor
    

    @taskexecutor.setter
    def taskexecutor(self, taskexecutor):
        self.__taskexecutor = taskexecutor
        
    
    
class IModule(IEventDispatcher, ITaskExecutor):    
    
    def __init__(self):
        super().__init__()
    
    
    def initialize(self) ->None:
        raise NotImplementedError
    
    
    '''
        Returns the name of a module
    '''
    def getname(self) ->Text:
        raise NotImplementedError

    
    '''
        Validates configuration object for the module. Every module should implement its own
        validation logic to verify a passed configuration object
    '''
    def valid_configuration(self, conf:Dict) ->bool:
        return True
    
    
    '''
        Returns a list of supported url patterns in modules
    '''
    def get_url_patterns(self) ->List:
        return list() 
    
    
    '''
        Returns a list of supported actions
    '''
    def supported_actions(self) -> List[object]:
        return list() 


    '''
        Returns a list supported of action names
    '''
    def supported_action_names(self) -> List[Text]:
        return list() 
    
    
    
    '''
        Returns a list supported of intents
    '''
    def supported_intents(self) -> List[Text]:
        return list() 
    


    '''
        Get actions definition object for UI
    '''
    def get_ui_actions(self) -> List[ActionItem]:
        return None

    
    
    '''
        Lookup an Action object instance by string name
    '''
    def action_from_name(self, name:Text) -> object:
        defaults = {a.name(): a for a in self.supported_actions()}
        if name in defaults:
            return defaults.get(name)
                
        return None
    
    
    
    '''
        Request to broadcast any data update for potential clients of the system
    '''
    def notify_updates(self)->None:
        pass




'''
Base class for a target delegate implementation used to manage and monitor a system process/software
'''
class TargetProcess(IModule):
    '''
    classdocs
    '''


    def __init__(self, alias, procname=None, root=None, service_path=None, invocable_namespace="do_fulfill"):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(self.__class__.__name__)

        self.__root=root
        self.__allowed_read_extensions = ['*']
        self.__allowed_write_extensions = ['*']
        self.__accessible_paths = []
        self.__procname=procname
        self.__alias=alias
        self.__pid_procname=procname
        self.__service__path = service_path 
        self.__pid=None
        self.__starting_proc=False
        self.__stopping_proc=False
        self.__running_proc=False
        self.__log_paths = []
        self.__target_version = None
        self.__target_installed = False     
        self.__target_stats = None  
        
    
    
    
    def initialize(self) ->None:
        self.logger.debug("Module init")
        
        
        
    @property
    def eventcallback(self):
        return self.__event_callback
    
    
    
    @eventcallback.setter
    def eventcallback(self, fun):
        self.__event_callback = fun
    
    
    '''
        Checks to see if target is installed on the system or not
    '''
    def isTargetInstalled(self):
        return self.__target_installed
    
    
    '''
        Sets the installed state of target on the system or not
    '''
    def setTargetInstalled(self, installed):
        self.__target_installed = installed
            
        
    '''
        Returns root path of the target
    '''
    def getRoot(self):
        return self.__root
    
    
    
    def getAllowedReadExtensions(self):
        return self.__allowed_read_extensions
    
    
    
    def setAllowedReadExtensions(self, extensions):
        if not isinstance(extensions, list):
            raise ValueError("Parameters should be of type `list`")
        self.__allowed_read_extensions = extensions
    
    
    
    def getAllowedWriteExtensions(self):
        return self.__allowed_write_extensions
    


    def getAccessiblePaths(self):
        return self.__accessible_paths
    
    
    
    def setAllowedWriteExtensions(self, extensions):
        if not isinstance(extensions, list):
            raise ValueError("Parameters should be of type `list`")
        self.__allowed_write_extensions = extensions
    
    
    '''
        Returns process service file path (for systemd daemon). 
    '''
    def getServicePath(self):
        return self.__service__path
    
    
    '''
        Sets process service file path (for systemd daemon). 
    '''
    def setServicePath(self, path):
        self.__service__path = path
    
    '''
        Returns process name of the target
    '''
    def getProcName(self):
        return self.__procname   
    
    
    '''
        Returns process name for the PID representing the process
    '''
    def getPidProcName(self):
        return self.__pid_procname
    
    
    '''
        Sets process name for the PID representing the process
    '''
    def setPidProcName(self, procname):
        self.__pid_procname = procname
        
        
    
    '''
        Returns target alias if available otherwise return modulename
    '''
    def getAlias(self):
        name:str = string.capwords(self.getname().replace("_", " ")).replace(" ", "")
        return self.__alias if self.__alias != None else name.lower()
    
    
    '''
        Sets target alias
    '''
    def setAlias(self, alias):
        self.__alias = alias
    
    
    
     
    
    '''
        Returns version of the target
    '''
    def getProcVersion(self):
        return self.__target_version
    
    
    '''
        Returns target specific stats
    '''
    def getTargetStats(self):
        return self.__target_stats
    
    
    '''
        Sets target specific stats
    '''
    def setTargetStats(self, stats):
        self.__target_stats = stats
    
    
    '''
        Process log line. This is called by log tailer.
        Original data is not changed. This is simply a hook to provide 
        log data to the TargetDelegate for analysis and consumption 
    '''
    async def processLogLine(self, line):
        await asyncio.sleep(.01)
        pass 
    
    
    def setProcVersion(self, ver):
        self.__target_version = ver
    
    '''
        Returns PID of the target
    '''
    def getTargetPid(self):
        return self.__pid 
    
    
    
    '''
        Sets target process id (PID)
    '''
    def setTargetPid(self, pid):
        self.__pid = pid
        
        
    
    '''
        Gets list of log paths for the target
    '''
    def getLogFiles(self):
        return self.__log_paths
    
    
    
    '''
        Sets list of log paths for the target
    '''
    def setLogFiles(self, log_paths):
        self.__log_paths = log_paths
        
    
    
    '''
        Checks to see if target is starting up or not.
        Returns true if running, false otherwise
    '''
    def is_proc_starting(self):
        return self.__starting_proc
    
    
    
    '''
        Sets primary log path of the target
    '''
    def set_proc_starting(self, starting):
        self.__starting_proc = starting
    

    
    '''
        Checks to see if target is stopping or not.
        Returns true if stopping, false otherwise
    '''
    def is_proc_stopping(self):
        return self.__stopping_proc
    
    
    
    '''
        Sets process stopping state
    '''
    def set_proc_stopping(self, stopping):
        self.__stopping_proc = stopping
    
    

    '''
        Checks to see if target is running or not.
        Returns true if running, false otherwise
    '''
    def is_proc_running(self):
        return self.__running_proc
    
    
    
    '''
        Sets process running state
    '''
    def set_proc_running(self, running):
        self.__running_proc = running
    
    
    '''
        Attempts to start process if not already started
    '''
    @abstractmethod
    def start_proc(self): 
        pass
    
    

    '''
        Attempts to stop process if not already stopped
    '''
    @abstractmethod
    def stop_proc(self):
        pass
    
    
    
    '''
        Attempts to restart process
    '''
    @abstractmethod
    def restart_proc(self):
        pass

    
    
    '''
        Checks to see if os level service is installed for the process
    '''
    def is_service_installed(self):
        if(not self.__service__path is None):
            return self._file_exists(self.__service__path)
        else:
            return False
       
            

    '''
        Method to handle reaction from reaction engine
    '''
    async def on_reaction(self, ruleid, event, params=None):
        self.logger.debug("Event reaction for rule %s", ruleid)
        asyncio.sleep(.5)
        pass
    
    
    
    def _file_exists(self, path):
        if os.path.isfile(path):
            return True
        else:
            return False





class ServiceBot(IModule):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.__webhook = False
        self.__supports_webhook = False
        self.__webhook_handler_url_config = None
        self.__webhook_secret = None
        pass
    
    
    
    def initialize(self) ->None:
        self.logger.debug("Module init")
    
    
    
    def is_webhook_supported(self):
        return self.__supports_webhook
    
    
    def set_webhook_supported(self, supports):
        self.__supports_webhook = bool(supports)
    
    
    def set_webhook(self, url):
        self.__webhook = url
        return False
    
    
    def get_webhook(self):
        return self.__webhook
    
    
    def get_webhook_url_config(self):
        return self.__webhook_handler_url_config
    
    
    def set_webhook_url_config(self, urlconfig):
        self.__webhook_handler_url_config = urlconfig
        
    
    async def sendEventAsMessage(self, event)-> None:
        raise NotImplementedError()
    
    
    async def send_notification(self, message:Text)-> None:
        raise NotImplementedError()


    async def sendImage(self, image, message:str=None)-> None:
        raise NotImplementedError()
        


class IntentProvider(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.__intenthandler = None
    
    
    @property
    def intenthandler(self) ->Callable:
        return self.__intenthandler
    
    
    
    @intenthandler.setter
    def intenthandler(self, handler:Callable) ->None:
        self.__intenthandler = handler


    
    async def notifyintent(self, intent:Text, args:Dict, event:EventType=None) -> None:
        if self.__intenthandler:
            return await self.__intenthandler(self, intent, args, event)
        pass
    

    async def onIntentProcessResult(self, requestid:str, result:object) -> None:
        pass


    async def onIntentProcessError(self, e:object, message:str = None) -> None:
        pass
    
    

class IClientChannel(object):
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        
        
        
class IMailer(object):
    
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        
    
    async def send_mail(self, subject:Text, body:Text) ->None:
        raise NotImplementedError()
        pass
    



class IMQTTClient(object):
    
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.__topic_data_handler = None
        
    
    async def publish_to_topic(self, topic:str, message:str, callback:Callable=None)->None:
        raise NotImplementedError()
        pass
    
    
    
    async def publish_to_topics(self, topics:List[str], message:str, callback:Callable=None)->None:
        raise NotImplementedError()
        pass
        
        


class IScriptRunner(object):
    
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        

    
    def start_script(self, name:Text) ->Text:
        raise NotImplementedError()
        pass
    
    
    
    def stop_script(self, script_id:Text)->Text:
        raise NotImplementedError()
    


class ILogMonitor(object):
    
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
    
    
    def get_log_targets(self):
        raise NotImplementedError()
        pass
    
    
    def register_log_file(self, log_info:Dict):
        raise NotImplementedError()
        pass
    
    
    def deregister_log_file(self, name:str):
        raise NotImplementedError()
        pass
    
    
    def get_log_keys(self):
        raise NotImplementedError()
        pass
    
    
    def get_log_info(self, name:str) ->Dict:
        raise NotImplementedError()
        pass
    
    def get_log_path(self, name:str) ->Text:
        raise NotImplementedError()
        pass
    
    
    def enable_chunk_generation(self, logname:str) ->None:
        raise NotImplementedError()
        pass
    
    
    
    def disable_chunk_generation(self, logname:str) ->None:
        raise NotImplementedError()
        pass


class ISystemMonitor(object):
    
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
    
    
    
    def start_monitor(self) -> None:
        raise NotImplementedError()
        pass
    
    
    def get_cpu_stats(self, cached=False) ->Dict:
        raise NotImplementedError()
        pass
    
    
    def get_memory_stats(self, unit = "b", cached=False) ->Dict:
        raise NotImplementedError()
        pass
    
    
    def schedule__update(self, updater_script:str) ->str:
        raise NotImplementedError()
        pass
    
    
    def force_gc(self) ->None:
        raise NotImplementedError()
        pass
    
    
    def get_version(self) -> str:
        raise NotImplementedError()
        pass
    
    
    def get_last_system_stats_snapshot(self) -> Dict:
        raise NotImplementedError()
        pass
    
    
    def get_system_time(self) -> str:
        raise NotImplementedError()
        pass
    
    


class IReactionEngine(object):
    
    
    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
    
    
    
    def has_rule(self, id:str)->bool:
        raise NotImplementedError()
    
    
    
    def register_rule(self, rule:ReactionRule) ->None:
        raise NotImplementedError()

    

    def get_rules(self) ->List:
        raise NotImplementedError()


    def reload_rules(self) ->None:
        raise NotImplementedError()
    

    def reload_rule(self, id:str)->None:
        raise NotImplementedError()
        

    def generate_sample_rule(self)->Dict:
        raise NotImplementedError()


    def write_rule(self, rule:Dict, update=False) ->None:
        raise NotImplementedError()    
    


    def delete_rule(self, id:str) ->None:
        raise NotImplementedError()  



    def get_rule(self, id:str) ->Dict:
        raise NotImplementedError()   
    


    async def process_event_with_rules(self, event:EventType):
        raise NotImplementedError()
    
    
    
    def deregister_rule(self, id:str)->None:
        raise NotImplementedError()
    


class IEventHandler(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.__topics_of_interest = [TOPIC_ANY]
        self.__events_of_interest = [EVENT_ANY]
      
    
    def get_events_of_interests(self)-> List:
        return self.__events_of_interest 
    
    
    def set_events_of_interests(self, events:List)-> None:
        self.__events_of_interest = events
    
    
    def get_topics_of_interests(self)-> List:
        return self.__topics_of_interest
    
    
    def set_topics_of_interests(self, topics:List)-> None:
        self.__topics_of_interest = topics        
        
        
    async def _notifyEvent(self, event:EventType):
        if event["topic"] in self.get_topics_of_interests() or TOPIC_ANY in self.get_topics_of_interests():
            if event["name"] in self.get_events_of_interests() or EVENT_ANY in self.get_events_of_interests():
                await self.handleEvent(event)
        pass
    
    
    async def handleEvent(self, event):
        pass



class IUIModeler(object):
    '''
    classdocs
    '''


    def __init__(self):
        pass


    def generate_ui_guide(self, ui_guide_folder:str, ui_guide_file:str, modules:Modules, handler = None)->None:
        pass




class IStatsProvider(object):
    '''
    classdocs
    '''


    def __init__(self):
        pass

    
    def get_render_map(self)->Dict:
        pass