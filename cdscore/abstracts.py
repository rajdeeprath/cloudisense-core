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


import string
import os
import logging
import asyncio

from abc import ABC, abstractmethod

from builtins import int, str
from typing import List, Text, Callable, Dict
from abc import abstractmethod


from cdscore.event import EventType, EVENT_ANY
from cdscore.constants import TOPIC_ANY
from cdscore.rules import ReactionRule
from cdscore.types import Modules
from cdscore.uielements import ActionItem


class IFileSystemOperator(ABC):
    
    @abstractmethod
    def add_accessible_path(self, path: str) -> None:
        pass
    
    @abstractmethod
    def get_accessible_paths(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_exposable_accessible_paths(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_real_path(self, path: str) -> str:
        pass
    
    @abstractmethod
    def browse_content(self, path: str) -> List:
        pass
    
    @abstractmethod
    def delete_file(self, path: str) -> None:
        pass
    
    @abstractmethod
    def delete_directory(self, path: str) -> None:
        pass
    
    @abstractmethod
    def make_downloadable_tmp_link(self, file_path: str) -> None:
        pass
    
    @abstractmethod
    def handle_upload(self, chunk: bytes, tmp_buffer: bytes, permit: Text) -> None:
        pass
    
    @property
    @abstractmethod
    def max_stream_size(self):
        pass
    
    @abstractmethod
    def generate_upload_permit(self, upload_path: str, filename: str, filesize: int = 0) -> object:
        pass
    
    @abstractmethod
    def get_upload_progress(self, permit: Text) -> int:
        pass
    
    @abstractmethod
    def handle_upload_complete(self, permit: Text, data, filename: str, args: Dict) -> None:
        pass
    
    @abstractmethod
    def download_file_async(self, file_path: str, chunksize: int, callback: Callable) -> None:
        pass
    
    @abstractmethod
    def read_file(self, filepath: str, base64_encoded: bool = False) -> any:
        pass
    
    @abstractmethod
    def write_file(self, filepath: str, content: str, reserved: bool = False, must_exist: bool = True, base64_encoded: bool = False) -> None:
        pass
    
    @abstractmethod
    def append_allowed_download_paths(self, paths: List) -> None:
        pass
    
    @abstractmethod
    def read_master_configuration(self) -> Dict:
        pass
    
    @abstractmethod
    def write_master_configuration(self, new_config: Dict) -> Dict:
        pass
    
    @abstractmethod
    async def write_file_stream(self, filepath, content, must_exist = False) ->None:
        pass



class IMessagingClient(ABC):  
    
    def __init__(self):
        pass
    

    @abstractmethod
    async def message_to_client(self, message: Dict) -> None:
        """Send a message to the client asynchronously."""
        pass  
    
    
    @abstractmethod
    def is_closed(self) -> bool:
        """Returns True if the client is closed, otherwise False."""
        pass
   

    @property
    @abstractmethod
    def id(self):
        """Unique identifier for the client."""
        pass
    



class IRPCGateway(ABC):
    
    @abstractmethod
    def handleRPC(self, wshandler, message):
        raise NotImplementedError       


class IFederationGateway(ABC):

    @abstractmethod
    async def prepare_client(self) -> None:
        """
        Asynchronously prepares the client for federation.
        """
        pass

    @abstractmethod
    async def connect_broker(self, client) -> None:
        """
        Asynchronously connects to the MQTT broker.
        """
        pass


    @abstractmethod
    def is_connected(self) -> bool:
        """Returns True if federation is connected, otherwise False."""
        pass
    
    
    @abstractmethod
    def is_client_online(self, client_id:str) -> bool:
        """
        Checks whether a remote Cloudisense node is currently connected to the federation mesh.
        """
        pass    
        
    
    @abstractmethod
    def send_message(self, serviceId: str, payload: Dict, headers=None) -> None:
        """Sends a message to a given topic."""
        pass
    
    
    @abstractmethod
    def send_broadcast(self, payload:Dict, headers=None)-> None:
        """Sends a broadcast to all clients."""
        pass
    
    
    @abstractmethod
    def on_connect(self, client, flags, rc, properties):
        """Handles MQTT connection events."""
        pass
    
    @abstractmethod
    def on_message(self, client, topic, payload, qos, properties):
        """Handles incoming MQTT messages."""
        pass
    
    @abstractmethod
    def on_disconnect(self, client, packet):
        """Handles MQTT disconnection events."""
        pass
    
    @abstractmethod
    def on_subscribe(self, client, mid, qos, properties):
        """Handles subscription events."""
        pass
    
    @abstractmethod
    def on_unsubscribe(self, client, mid, qos, properties):
        """Handles unsubscription events."""
        pass
    
    @abstractmethod
    def handle_client_presence(self, client, topic: str, payload: str):
        """Handles client presence updates."""
        pass
    
    @abstractmethod
    def listen_to_client_directory(self, client, qos: int = 1):
        """Subscribes to presence updates for all clients."""
        pass
    
    @abstractmethod
    def listen_for_private_messages(self, client, qos: int = 1):
        """Subscribes to private messages for the client."""
        pass
    
    @abstractmethod
    def on_message_handler(self) -> Callable:
        """Getter for the on_message_handler."""
        pass

    @abstractmethod
    def on_message_handler(self, handler: Callable) -> None:
        """Setter for the on_message_handler."""
        pass
    
    
    @abstractmethod
    def on_client_connect_handler(self) -> Callable:
        """Getter for the on_client_connect_handler."""
        pass

    @abstractmethod
    def on_client_connect_handler(self, handler: Callable) -> None:
        """Setter for the on_client_connect_handler."""
        pass
    
    
    @abstractmethod
    def on_client_disconnect_handler(self) -> Callable:
        """Getter for the on_client_disconnect_handler."""
        pass

    @abstractmethod
    def on_client_disconnect_handler(self, handler: Callable) -> None:
        """Setter for the on_client_disconnect_handler."""
        pass
    
    
    @abstractmethod
    def publish_event(self, topic: str, payload: Dict, qos: int = 0) -> None:
        """
        Publishes an event to the specified topic.

        Args:
            topic (str): The topic to publish the event to.
            payload (Dict): The message content.
            qos (int): Quality of Service level (0, 1, or 2). Defaults to 0.
        """
        pass


    @abstractmethod
    def subscribe_to_event(self, serviceId: str, topic: str, qos: int = 1) -> None:
        """
        Subscribes to an event topic for a given remote service.

        Args:
            serviceId (str): Identifier of the target service to subscribe to.
            topic (str): The event topic to subscribe to.
            qos (int): Quality of Service level (default is 1).
        """
        pass


    @abstractmethod
    def unsubscribe_from_event(self, serviceId: str, topic: str, qos: int = 1) -> None:
        """
        Unsubscribes from an event topic for a given remote service.

        Args:
            serviceId (str): Identifier of the target service.
            topic (str): The topic to unsubscribe from.
            qos (int): Quality of Service level (default is 1).
        """
        pass
        


class IScriptRunner(ABC):
    
    @abstractmethod
    def start_script(self, name: Text) -> Text:
        pass
    
    @abstractmethod
    def stop_script(self, script_id: Text) -> Text:
        pass




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
    
    

class IClientChannel(ABC):
    pass



class IMailer(ABC):
    
    @abstractmethod
    async def send_mail(self, subject: Text, body: Text) -> None:
        pass



class IMQTTClient(ABC):
    
    def __init__(self):
        self.__topic_data_handler = None
    
    @abstractmethod
    async def publish_to_topic(self, topic: str, message: str, callback: Callable = None) -> None:
        pass
    
    @abstractmethod
    async def publish_to_topics(self, topics: List[str], message: str, callback: Callable = None) -> None:
        pass


class ILogMonitor(ABC):
    
    @abstractmethod
    def get_log_targets(self):
        pass
    
    @abstractmethod
    def register_log_file(self, log_info: Dict):
        pass
    
    @abstractmethod
    def deregister_log_file(self, name: str):
        pass
    
    @abstractmethod
    def get_log_keys(self):
        pass
    
    @abstractmethod
    def get_log_info(self, name: str) -> Dict:
        pass
    
    @abstractmethod
    def get_log_path(self, name: str) -> Text:
        pass
    
    @abstractmethod
    def enable_chunk_generation(self, logname: str) -> None:
        pass
    
    @abstractmethod
    def disable_chunk_generation(self, logname: str) -> None:
        pass
    
    

class ISystemCore(ABC):
    
    @abstractmethod
    async def systemctl_command(self, action: str, service: str) -> None:
        pass
    
    @abstractmethod
    def get_persistent_id(self, file_path: str = "unique_id.txt") -> str:
        pass
    
    @abstractmethod
    def get_open_files_limits(self) -> int:
        pass

    @property
    @abstractmethod
    def identity(self) -> str:
        pass
    
    @identity.setter
    @abstractmethod
    def identity(self, uuid: str):
        pass
    
    @abstractmethod
    def restart(self) -> Dict:
        pass
    
    @abstractmethod
    def read_module_configuration(self, module_file_name: str) -> Dict:
        pass
    
    @abstractmethod
    def read_all_module_configurations(self) -> Dict:
        pass
    
    @abstractmethod
    def read_master_configuration(self) -> Dict:
        pass
    
    @abstractmethod
    def is_restart_allowed(self) -> bool:
        pass
    
    @abstractmethod
    async def update(self):
        pass


class IPubSubHub(ABC):
    """
    Abstract interface for a Pub/Sub event hub that supports
    channel-based communication and streaming between clients.
    """

    @property
    @abstractmethod
    def channels(self) -> Dict[str, tuple]:
        """Returns the current channel configuration."""
        pass

    @channels.setter
    @abstractmethod
    def channels(self, _channels: Dict[str, tuple]) -> None:
        """Sets the entire channels structure (used during initialization)."""
        pass

    @abstractmethod
    def addEventListener(self, listener: 'IEventHandler') -> None:
        """Registers an event listener for channel events."""
        pass

    @abstractmethod
    def removeEventListener(self, listener: 'IEventHandler') -> None:
        """Removes a previously registered event listener."""
        pass

    @abstractmethod
    def getEventListeners(self) -> List['IEventHandler']:
        """Returns a list of all currently registered event listeners."""
        pass

    @abstractmethod
    def subscribe(self, topicname: str, client: IMessagingClient = None) -> None:
        """Subscribes a client to a specific topic."""
        pass

    @abstractmethod
    def subscribe_topics(self, topics: List[str], client: IMessagingClient) -> None:
        """Subscribes a client to multiple topics."""
        pass

    @abstractmethod
    def unsubscribe(self, topicname: str, client: IMessagingClient) -> None:
        """Unsubscribes a client from a specific topic."""
        pass

    @abstractmethod
    def clearsubscriptions(self, client: IMessagingClient) -> None:
        """Unsubscribes the given client from all channels it is part of."""
        pass

    @abstractmethod
    def createChannel(self, channel_info: Dict, channel_type: str = "bidirectional") -> None:
        """Creates a new channel using the given channel info and type."""
        pass

    @abstractmethod
    def removeChannel(self, topicname: str) -> None:
        """Deletes the specified channel and all of its subscriptions."""
        pass

    @abstractmethod
    async def publish(self, topicname: str, message: Dict, client: IMessagingClient = None) -> None:
        """Publishes a message to a topic (optionally from a specific client)."""
        pass

    @abstractmethod
    async def publish_notification(self, event: Dict) -> None:
        """Publishes a generic event notification to interested clients."""
        pass

    @abstractmethod
    async def publish_event_type(self, event: EventType) -> None:
        """Publishes a structured event to all subscribed clients."""
        pass


class ISystemMonitor(ABC):
    
    @abstractmethod
    def get_cpu_stats(self, cached=False) -> Dict:
        pass
    
    @abstractmethod
    def get_memory_stats(self, unit="b", cached=False) -> Dict:
        pass
    
    @abstractmethod
    def force_gc(self) -> None:
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        pass
    
    @abstractmethod
    def get_last_system_stats_snapshot(self) -> Dict:
        pass
    
    @abstractmethod
    def get_system_time(self) -> str:
        pass

    


class IReactionEngine(ABC):
    
    @abstractmethod
    def has_rule(self, id: str) -> bool:
        pass
    
    @abstractmethod
    def register_rule(self, rule: 'ReactionRule') -> None:
        pass
    
    @abstractmethod
    def get_rules(self) -> List:
        pass
    
    @abstractmethod
    def reload_rules(self) -> None:
        pass
    
    @abstractmethod
    def reload_rule(self, id: str) -> None:
        pass
    
    @abstractmethod
    def generate_sample_rule(self) -> Dict:
        pass
    
    @abstractmethod
    def write_rule(self, rule: Dict, update=False) -> None:
        pass
    
    @abstractmethod
    def delete_rule(self, id: str) -> None:
        pass
    
    @abstractmethod
    def get_rule(self, id: str) -> Dict:
        pass
    
    @abstractmethod
    async def process_event_with_rules(self, event: 'EventType'):
        pass
    
    @abstractmethod
    def deregister_rule(self, id: str) -> None:
        pass
    


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
    
    
    @abstractmethod
    async def handleEvent(self, event:EventType):
        pass



class IUIModeler(ABC):
    
    @abstractmethod
    def generate_ui_guide(self, ui_guide_folder: str, ui_guide_file: str, modules: 'Modules', handler=None) -> None:
        pass



class IStatsProvider(ABC):
    
    @abstractmethod
    def get_render_map(self) -> Dict:
        pass




class ICloudisenseApplication(ABC):
    
    @abstractmethod
    async def handle_event(self, event: 'EventType'):
        pass
    
    @abstractmethod
    async def handle_intent_request(self, source: 'IntentProvider', intent: Text, args: Dict, event: 'EventType' = None):
        pass
    
    @abstractmethod
    def handle_client_close(self, client: 'IMessagingClient') -> None:
        pass
    
    @abstractmethod
    async def handle_client_join(self, client: 'IMessagingClient') -> None:
        pass
    
    @property
    @abstractmethod
    def identity(self):
        pass
    
    @identity.setter
    @abstractmethod
    def identity(self, uid) -> None:
        pass
    
    @property
    @abstractmethod
    def totalclients(self):
        pass
    
    @property
    @abstractmethod
    def clients(self):
        pass
    
    @abstractmethod
    def register_client(self, client: object) -> None:
        pass
    
    @abstractmethod
    def unregister_client(self, client: object) -> None:
        pass
    
    @property
    @abstractmethod
    def configuration(self) -> Dict:
        pass
    
    @configuration.setter
    @abstractmethod
    def configuration(self, config: Dict) -> None:
        pass
    
    @property
    @abstractmethod
    def modules(self) -> 'Modules':
        pass
    
    @property
    @abstractmethod
    def action_dispatcher(self):
        pass
    
    @abstractmethod
    async def handle_socket_message(self, message: Dict, client: 'IMessagingClient') -> None:
        pass
    


class IContainerManagerInterface(ABC):
    @abstractmethod
    def start_container(self, container_id: str) -> str:
        """Start a container given its ID."""
        pass

    @abstractmethod
    def stop_container(self, container_id: str) -> str:
        """Stop a container given its ID."""
        pass

    @abstractmethod
    def remove_container(self, container_id: str) -> str:
        """Remove a container given its ID."""
        pass

    @abstractmethod
    def restart_container(self, container_id: str) -> str:
        """Restart a container given its ID."""
        pass

    @abstractmethod
    def inspect_container(self, container_id: str) -> Dict:
        """Inspect a container and return detailed information."""
        pass

    @abstractmethod
    def run_container(
        self, 
        image: str, 
        name: Optional[str] = None, 
        command: Optional[str] = None, 
        detach: bool = True, 
        ports: Optional[Dict[str, int]] = None
    ) -> str:
        """Run a new container from an image."""
        pass

    @abstractmethod
    def get_swarm_status(self) -> Dict:
        """Get the current swarm status."""
        pass

    @abstractmethod
    def list_swarm_services(self) -> List[Dict]:
        """List all swarm services."""
        pass

    @abstractmethod
    def list_swarm_nodes(self) -> List[Dict]:
        """List all swarm nodes."""
        pass

    @abstractmethod
    def inspect_swarm_service(self, service_id: str) -> Dict:
        """Inspect a swarm service."""
        pass

    @abstractmethod
    def remove_swarm_service(self, service_id: str) -> str:
        """Remove a swarm service."""
        pass
