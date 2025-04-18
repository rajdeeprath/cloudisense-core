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



import threading
import uuid
import json
import logging
import os
import random
import logging
import tornado
import copy

from typing import Callable, Dict, Set
from tornado.queues import Queue
from smalluuid import SmallUUID
from time import time
from typing import Text, List
from builtins import str
from tornado.ioloop import IOLoop
from concurrent.futures.thread import ThreadPoolExecutor
from tornado.websocket import websocket_connect
from string import ascii_letters

from cdscore.constants import *
from cdscore.event import *
from cdscore.abstracts import ICloudisenseApplication, IFederationGateway, IMessagingClient, IRPCGateway, ITaskExecutor, IntentProvider, IClientChannel, IEventHandler, IEventDispatcher, IModule, IntentProvider
from cdscore.exceptions import ActionError, RPCError
from cdscore.helpers import formatErrorRPCResponse, formatFederationBroadcastRequest, formatRemoteRPCRequest, formatSuccessRPCResponse
from cdscore.intent import built_in_intents, INTENT_PREFIX
from cdscore.action import ACTION_PREFIX, ActionResponse, Action, builtin_action_names, action_from_name
from cdscore.types import Modules
from cdscore.event import EVENT_KEY
from cdscore.constants import built_in_client_types
from cdscore.exceptions import ConfigurationLoadError




class Configuration(object):
    '''
    classdoimport random
cs
    '''

    def __init__(self, conf_file):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.__conf_file = conf_file
        self.config = None
        import random

        
    def load(self):
        import random

        self.logger.info("Loading configuration data")
        
        try:
            self.logger.info("Loading %s", self.__conf_file)
            if os.path.exists(self.__conf_file):
                with open(self.__conf_file, 'r+') as json_data_file:
                    self.config = json.load(json_data_file)["configuration"]
            else:
                raise FileNotFoundError("File : " + self.__conf_file + " does not exist.")
        
        except Exception as e:
            err = "Unable to load primary configuration " + str(e)
            self.logger.error(err)
            raise ConfigurationLoadError(err)
        
        
    @property
    def data(self):
        return self.config


class PathConcealer(object):

    SUBSTITUTION_CIPHER_LETTERS = 'nzghqkcdmyfoialxevtswrupjbNZGHQKCDMYFOIALXEVTSWRUPJB'


    def __init__(self, randomize = False):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.cipherset = PathConcealer.SUBSTITUTION_CIPHER_LETTERS
        if randomize:            
            self.cipherset = ''.join(random.shuffle(list(PathConcealer.SUBSTITUTION_CIPHER_LETTERS)))

    
    def conceal(self, text:str)->Text:
        trans = str.maketrans(ascii_letters, self.cipherset)
        return text.translate(trans)
    

    def reveal(self, text:str)->Text:
        trans = str.maketrans(self.cipherset, ascii_letters)
        return text.translate(trans)




class PubSubHub(IModule):
    '''
    classdocs
    '''
    NAME = "pubsub"        

    def __init__(self, config):
        '''
        Constructor
        '''        
        super().__init__()
        
        self.logger = logging.getLogger(self.__class__.__name__)

        self.__config = config
        self.__channels = {}
        self.__listeners = []
        pubsub_channels = self.__config["topics"]
        
        for channel_info in pubsub_channels:
            topicname = channel_info["name"]
            topictype = channel_info["type"]
            queuesize = channel_info["queue_size"]
            max_users = channel_info["max_users"]
            self.channels[topicname] = (topicname, topictype, Queue(maxsize=queuesize), set(), max_users)
        
        '''
        channels["topic_name"] = ('topic_type', 'public_or_private', {message_queue}, {subscribers_list}, max_users)
        '''        
        self.logger.debug("total channels = %d", len(self.channels))
    



    def initialize(self) ->None:
        self.logger.debug("Module init")                
        pass


    
    def valid_configuration(self, conf:Dict) ->bool:
        return True



    def get_url_patterns(self)->List:
        return []
    
    
    
    def getname(self) ->Text:
        return PubSubHub.NAME
  


    '''
        Returns a list of supported actions
    '''
    def supported_actions(self) -> List[object]:
        return []



    '''
        Returns a list supported of action names
    '''
    def supported_action_names(self) -> List[Text]:
        return [a.name() for a in self.supported_actions()]
    
    


    '''
        Returns a list supported of intents
    '''
    def supported_intents(self) -> List[Text]:
        return []    
    
    
    
    def is_dynamic_channel(self, topicname):
        
        pubsub_channels = self.__config["topics"]
        
        for channel_info in pubsub_channels:
            if topicname == channel_info["name"]:
                return False
        
        return True 
        
    
    @property    
    def channels(self):
        return self.__channels
        
    
    @channels.setter
    def channels(self, _channels):
        self.__channels = _channels        
        
        
    def addEventListener(self, listener:IEventHandler)->None:
        self.__listeners.append(listener)
        
        
    def removeEventListener(self, listener:IEventHandler)->None:
        self.__listeners.remove(listener)


    def getEventListeners(self)->List[IEventHandler]:
        return self.__listeners
       
        
    def subscribe(self, topicname, client:IMessagingClient = None):
        
        if topicname not in self.channels:
            if self.__config["allow_dynamic_topics"] == True:
                channel_info = {}
                channel_info["name"] = topicname  
                channel_info['type'] = "bidirectional"
                channel_info["queue_size"] = 1
                channel_info["max_users"]  = 0
                self.createChannel(channel_info)
                if client != None:
                    clients:Set[IMessagingClient] = self.channels[topicname][3] #set
                    clients.add(client);                
                    self.logger.info("Total clients in %s = %d", topicname, len(clients))
            else:
                self.logger.error("Topic channel %s does not exist and cannot be created either", topicname)
        else:
            clients:Set[IMessagingClient] = self.channels[topicname][3] #set
            clients.add(client);                
            self.logger.info("Total clients in %s = %d", topicname, len(clients))
        pass
    
    
    '''
        Client subscribe to multiple topics
    ''' 
    def subscribe_topics(self, topics, client:IMessagingClient):
        for topicname in topics:
            self.subscribe(topicname, client)
            pass    
    
    
    '''
        Client unsubscribes from topic
    '''
    def unsubscribe(self, topicname, client:IMessagingClient):
        if topicname in self.channels:
            clients:Set[IMessagingClient] = self.channels[topicname][3] #set
            clients.discard(client);
            self.logger.info("Total clients in %s = %d", topicname, len(clients))
            
            '''
            if len(clients) == 0 and self.is_dynamic_channel(topicname):
                self.removeChannel(topicname)
            '''
        pass
    
    
    
    '''
        clear all subscriptions
    '''
    def clearsubscriptions(self, client:IMessagingClient):
        for key in list(self.channels):
            self.logger.info("Clearing subscriptions in topic %s", key)
            self.unsubscribe(key, client)
        pass
    
    
    
    '''
        Creates a dynamic bidirectional communication channel
    '''
    def createChannel(self, channel_info, channel_type="bidirectional"):
        if "name" in channel_info and not channel_info["name"] in self.channels:
            topicname = channel_info["name"]
            topictype = channel_type
            queuesize = channel_info["queue_size"]
            max_users = channel_info["max_users"]
            self.logger.info("Registering channel %s", topicname)
            self.channels[topicname] = (topicname, topictype, Queue(maxsize=queuesize), set(), max_users)
            self.logger.debug("Activating message flush for topic %s", topicname)
            tornado.ioloop.IOLoop.current().spawn_callback(self.__flush_messages, topicname)
        pass
    
    
    '''
        Removes a communication channel
    '''
    def removeChannel(self, topicname):
        for k in list(self.channels.keys()):
            if k == topicname:
                channel = self.channels[topicname]
                
                # possible logic to cleanly dispose queue content
                msgque:Queue = channel[2] #queue
                while msgque.qsize() > 0:
                    item = msgque.get_nowait()
                    msgque.task_done()
                                        
                del msgque
                del self.channels[topicname]
                self.logger.info("Removed channel %s", topicname)
        pass
    
    
    
    '''
        Accepts data submission for topic
    '''
    async def __submit(self, topicname, message):
        if topicname in self.channels:
            msgque:Queue = self.channels[topicname][2] #queue
            await msgque.put(message)
        pass
    
    
    '''
        Publishes data to a specified topic, if it exists.
        If topic channel does not exist, it is created based on configuration
        parameter `allow_dynamic_topic`
    '''
    async def publish(self, topicname, message, client:IMessagingClient=None):
        if topicname not in self.channels:
            if self.__config["allow_dynamic_topics"] == True:
                channel_info = {}
                channel_info["name"] = topicname  
                channel_info['type'] = "bidirectional"
                channel_info["queue_size"] = 1
                channel_info["max_users"]  = 0
                self.createChannel(channel_info)
                await self.__submit(topicname, message)
            else:
                self.logger.error("Topic channel does not exist and cannot be created either")
        else:
            await self.__submit(topicname, message)
        pass
    
    
    '''
        Publishes event data to a events channel -
        *To be deprecated in favor of new event system*
    '''
    async def publish_notification(self, event):
        if TOPIC_NOTIFICATION in self.channels:
            if self.__isValidEvent(event):
                await self.__submit(TOPIC_NOTIFICATION, event)
        pass
    
    
    
    
    '''
        Publishes event to designated channel
    '''
    async def publish_event_type(self, event:EventType):
        
        if "topic"in event:
            
            if event["topic"] not in self.channels and self.__config["allow_dynamic_topics"] == True:
                self.createChannel({"name": event["topic"], "type": "bidirectional", "queue_size": 0, "max_users": 0})
        
            if event["topic"] in self.channels:
                if is_valid_event(event):
                    await self.__submit(event["topic"], event)
            pass
    
    
    
    
    
    '''
    Activate auto message flush for all channels
    '''
    def activate_message_flush(self):
        for topic in self.channels:
            self.logger.debug("Activating message flush for topic %s", topic)
            tornado.ioloop.IOLoop.current().spawn_callback(self.__flush_messages, topic)
            pass
    pass



    
    
    '''
    Flushes messages from  channel queue into client's message queue actively
    '''
    async def __flush_messages(self, topic):        
        while True:
            
            try:
                if(not topic in self.channels):
                    break
                
                channel = self.channels[topic]
                msgque:Queue = channel[2] #queue
                clients:Set[IMessagingClient]  = channel[3] #set
                
                message = await msgque.get()                
                
                if len(clients) > 0:
                    self.logger.debug("Pushing message %s to %s subscribers...",format(message), len(clients))
                    
                    ''' pushing to clients '''
                    try:    
                        for client in clients:
                            await client.message_to_client(message)
                    except Exception as e:
                        logging.error("An error occurred pushing messages to client %s for topic %s. Cause : %s.", str(client), topic, str(e))
                    
                
                ''' pushing to listeners '''
                try:
                    for listener in self.getEventListeners():
                        if is_valid_event(message):
                            await listener._notifyEvent(message)                            
                except Exception as e:
                        self.logger.error("An error occurred notifying %s while reacting to this event.%s", str(listener), str(e))
                
            except GeneratorExit as ge:
                logging.error("GeneratorExit occurred")
                return
            
            except Exception as re:
                logging.error("Unexpected error occurred, which caused by %s", str(re))
                
            finally:
                msgque.task_done()



@DeprecationWarning
class VirtualHandler(object):
    '''
    Acts as a handler delegate on behalf of client channels
    '''
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.messages = Queue()
        self.id = str(uuid.uuid4())
        self.liveactions = {}
        self.liveactions['logrecordings'] = set()
        self.liveactions['scriptexecutions'] = set()
        self.finished = False
        tornado.ioloop.IOLoop.current().spawn_callback(self.__run)
        pass
    
    
    
    def close(self):
        self.finished = True
        pass
    
    
    
    async def submit(self, message):
        await self.messages.put(message) 
        pass
    
    
    
    async def __run(self):
        while not self.finished:
            try:
                message = await self.messages.get()
                self.send(message)
            except Exception as e:
                pass
            finally:
                self.messages.task_done()



class ActionDispatcher(ITaskExecutor):
    """
    Responsible for registering and executing actions associated with intents.
    Handles both queue-based and direct execution of asynchronous or synchronous actions.
    Supports automatic mapping of built-in intents to built-in actions.
    """

    def __init__(self, modules: Modules, conf=None, executor: ThreadPoolExecutor = None):
        """
        Initializes the ActionDispatcher.

        Args:
            modules (Modules): Module registry.
            conf (dict, optional): Configuration dictionary.
            executor (ThreadPoolExecutor, optional): Optional executor for running synchronous actions.
        """
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__conf = conf
        self.__modules = modules
        self.__action_book = {}
        self.__request_register = {}
        self.__executor = executor if executor is not None else executor
        tornado.ioloop.IOLoop.current().spawn_callback(self.__initialize)

    
    async def __initialize(self):
        """
        Initializes internal mappings of built-in intents to corresponding actions.
        """
        for intent_name in built_in_intents():
            try:
                action_name = str(intent_name).replace(INTENT_PREFIX, ACTION_PREFIX)
                action: Action = action_from_name(action_name)

                if action:
                    self.registerActionforIntent(intent_name, action)
                    self.logger.debug("Registered intent by name " + intent_name + " for action " + action_name)
                else:
                    raise TypeError("'action' for intent " + intent_name + " was None, expected Action object")

            except TypeError as te:
                self.logger.warning(str(te))

    
    def registerActionforIntent(self, intent_name: Text, action: Action):
        """
        Registers a specific Action object for a given intent.

        Args:
            intent_name (str): The intent identifier.
            action (Action): The action implementation.
        """
        if intent_name in self.__action_book:
            raise ValueError("Intent " + intent_name + " is already registered")

        self.__action_book[intent_name] = {"action": action, "requests": Queue(maxsize=5)}
        tornado.ioloop.IOLoop.current().spawn_callback(self.__task_processor, intent_name)

    
    def registerActionByNameforIntent(self, intent_name: Text, action_name: Text):
        """
        Registers an Action object for a given intent using the action's name.

        Args:
            intent_name (str): The intent identifier.
            action_name (str): The string name of the action to bind.
        """
        if action_name not in builtin_action_names():
            raise ValueError("Invalid action name " + action_name)

        if intent_name in self.__action_book:
            raise ValueError("Intent " + intent_name + " is already registered")

        action: Action = action_from_name(action_name)
        self.__action_book[intent_name] = {"action": action, "requests": Queue(maxsize=5)}
        tornado.ioloop.IOLoop.current().spawn_callback(self.__task_processor, intent_name)

    
    def _build_request(self, requester: IntentProvider, intent: Text, params: object):
        """
        Builds a well-structured request object from incoming parameters.

        Args:
            requester (IntentProvider): The source of the request.
            intent (str): Intent identifier.
            params (object): Parameter payload (dict, JSON string, or list).

        Returns:
            dict: Structured request object.
        """
        if isinstance(params, str):
            params = json.loads(params)
        elif isinstance(params, list):
            params = dict(zip(params[::2], params[1::2]))
        elif not isinstance(params, dict):
            raise ValueError("Incompatible param type. dict is required")

        return {
            "requestid": SmallUUID().hex,
            "requester": requester,
            "intent": intent,
            "params": params,
            "timestamp": int(round(time() * 1000))
        }

    
    async def handle_request(self, requester: IntentProvider, intent: Text, params: dict, event: EventType = None):
        """
        Handles an intent request by queuing it for background processing.

        Args:
            requester (IntentProvider): Caller to notify about result.
            intent (str): Intent name.
            params (dict): Intent parameters.
            event (EventType, optional): Optional event info to merge into params.

        Returns:
            str: The generated request ID.
        """
        if event:
            params = self.merge_parameters(params, event)

        intent_name = (INTENT_PREFIX + intent) if not intent.startswith(INTENT_PREFIX) else intent
        if intent_name not in self.__action_book:
            raise KeyError("Unknown intent " + intent_name)

        req_queue: Queue = self.__action_book[intent_name]["requests"]
        req = self._build_request(requester, intent, params)
        self.__request_register[req["requestid"]] = req

        await req_queue.put(req)
        return req["requestid"]

    
    async def handle_request_direct(self, requester: IntentProvider, intent: Text, params: dict):
        """
        Executes an intent request immediately, without queuing.

        Args:
            requester (IntentProvider): Caller to notify.
            intent (str): Intent name.
            params (dict): Intent parameters.

        Returns:
            any: Result returned by the action.
        """
        intent_name = (INTENT_PREFIX + intent) if not intent.startswith(INTENT_PREFIX) else intent

        if intent_name not in self.__action_book:
            raise KeyError("Unknown intent " + intent_name)

        events = None
        executable = None

        try:
            action: Action = self.__action_book[intent_name]["action"]
            executable = copy.deepcopy(action)

            if action.is_async():
                result: ActionResponse = await executable.execute(requester, self.__modules, params)
            else:
                result: ActionResponse = await IOLoop.current().run_in_executor(
                    self.__executor,
                    executable.execute, requester, self.__modules, params
                )

            events = result.events
            return result.data

        except Exception as e:
            self.logger.debug("Error executing action: %s", str(e))
            raise ActionError("Error executing action " + str(e))

        finally:
            if executable:
                del executable
            if events:
                pubsub = self.__modules.getModule(PUBSUBHUB_MODULE)
                for event in events:
                    await pubsub.publish_event_type(event)

    
    def merge_parameters(self, params, event: EventType):
        """
        Merges event metadata into the parameter dictionary.

        Args:
            params (dict): Base parameters.
            event (EventType): Event metadata.

        Returns:
            dict: Merged parameter dictionary.
        """
        return {**params, EVENT_KEY: event}

    
    async def __task_processor(self, intent_name):
        """
        Task queue processor loop for an intent. Handles requests one by one.

        Args:
            intent_name (str): The intent to process.
        """
        while True:
            if intent_name not in self.__action_book:
                break

            task_queue: Queue = self.__action_book[intent_name]["requests"]
            requestid = None
            events = None

            try:
                task_definition = await task_queue.get()
                requestid = task_definition["requestid"]
                requester: IntentProvider = task_definition["requester"]
                args: dict = task_definition["params"]

                action: Action = self.__action_book[intent_name]["action"]
                executable = copy.deepcopy(action)

                result: ActionResponse = await executable.execute(requester, self.__modules, args)
                events = result.events

                if requester:
                    await requester.onIntentProcessResult(requestid, result.data)

            except Exception as e:
                self.logger.debug("Error executing action: %s", str(e))
                if requester:
                    await requester.onIntentProcessError(requestid, e)

            finally:
                task_queue.task_done()
                if requestid in self.__request_register:
                    del self.__request_register[requestid]
                if events:
                    pubsub = self.__modules.getModule(PUBSUBHUB_MODULE)
                    for event in events:
                        await pubsub.publish_event_type(event)


class SafeLookupStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._store = {}

    def set(self, key, value):
        with self._lock:
            self._store[key] = value

    def get(self, key, default=None):
        with self._lock:
            return self._store.get(key, default)

    def pop(self, key, default=None):
        with self._lock:
            return self._store.pop(key, default)

    def has(self, key):
        with self._lock:
            return key in self._store
        

class MessageClassifier(object):
    
    def __init__(self) -> None:
        super().__init__()
        
    
    def is_rpc(self, message: Dict) -> bool:
        """True if the message is an RPC request."""
        return message.get("type") == "rpc"
    
    def is_local_rpc(self, message: Dict) -> bool:
        """True if the message is an RPC request."""
        return self.is_rpc(message)

    def is_rpc_response(self, message: Dict) -> bool:
        """True if the message is an RPC response (from service to service or back to client)."""
        return message.get("type") == "rpc_response"

    def is_browser_to_local(self, message: Dict) -> bool:
        """
        Client ➝ Local Service
        - No 'serviceId' (means it's for the local service)
        - No 'clientId' (client does not self-identify)
        """
        return self.is_rpc(message) and "serviceId" not in message and "clientId" not in message

    def is_browser_to_remote(self, message: Dict) -> bool:
        """
        Client ➝ Local ➝ Remote
        - No 'clientId' yet (will be added by local service)
        - Has 'serviceId' set to remote target
        """
        return self.is_rpc(message) and "serviceId" in message and "clientId" not in message

    def is_local_to_remote(self, message: Dict) -> bool:
        """
        Local ➝ Remote
        - Has 'serviceId' (target)
        - Has 'clientId' (to return result to browser)
        """
        return self.is_rpc(message) and "serviceId" in message and "clientId" in message
    
    def is_network_rpc(self, message: Dict) -> bool:
        """
        Determines if the given message is a network RPC (with serviceId).
        """
        return self.is_rpc(message) and "serviceId" in message and bool(message.get("serviceId"))

    def is_broadcast_rpc(self, message: Dict) -> bool:
        """
        Determines if the given message is a broadcast RPC.
        """
        return self.is_rpc(message) and "serviceId" in message and message.get("serviceId") == "*"

    def is_remote_to_local_response(self, message: Dict) -> bool:
        """
        Remote ➝ Local (RPC response)
        - Type: 'rpc_response'
        - Has 'clientId' to forward to browser
        """
        return self.is_rpc_response(message) and "clientId" in message

    def is_service_to_service_rpc(self, message: Dict) -> bool:
        """
        Local Service ➝ Remote Service (not browser-originated)
        - RPC
        - No clientId (not related to browser)
        """
        return self.is_rpc(message) and "serviceId" in message and "clientId" in message and message.get("clientId") == os.environ["CLOUDISENSE_IDENTITY"]

    def is_service_to_service_response(self, message: Dict) -> bool:
        """
        Remote ➝ Local (response to direct RPC, not for browser)
        - 'rpc_response' without 'clientId'
        """
        return self.is_rpc_response(message) and "serviceId" in message and message.get("serviceId") == os.environ["CLOUDISENSE_IDENTITY"]
    

class RemoteMessagingClient(IMessagingClient):
    """
    Virtual client wrapper for a remote Cloudisense instance that sent a message via Federation (MQTT).
    This allows the system to treat remote services like clients and route responses uniformly.
    """

    def __init__(self, origin_id: str, federation: IFederationGateway):
        self._id = origin_id # every cloudisense instance must have a uniue id
        self._federation = federation



    def is_closed(self) -> bool:
        """
        Always returns False — federation is considered always available for routing.
        """
        return not self._federation.is_connected()
    
    @property
    def id(self) -> str:
        """
        Required by IMessagingClient. Returns the client ID.
        """
        return self._id

    async def message_to_client(self, message: Dict) -> None:
        """
        Sends the response back to the origin via the Federation Gateway.
        """
        if not self._federation.is_connected():
            raise ConnectionError(f"Cannot send message: federation disconnected (target: {self.id})")
        
        if not self._federation.is_client_online(self._id):
            raise ConnectionError(f"Cannot send message: client is not connected to federation anymore (target: {self.id})")

        self._federation.send_message(self._id, message)

    
    def __repr__(self):
        return f"<RemoteMessagingClient id={self._id}>"



class MessageRouter(IEventDispatcher):
    
    def __init__(self, modules: Modules, conf=None, executor: ThreadPoolExecutor = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__modules = modules
        self.__message_classifier = MessageClassifier()
        self.__message_directory = SafeLookupStore()
        self.__incoming_messages = Queue()   
        self.initialize() 


    def initialize(self) -> None:
        if self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
            federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
            federation_gateway.on_message_handler = self._handle_remote_message
            
        tornado.ioloop.IOLoop.current().spawn_callback(self.__process_messages)   
    
    
    
    async def handle_messages(self, message: Dict, client: IMessagingClient) -> None:
        """
        Processes incoming messages and determines how to handle them. 
        """
        if self.__message_classifier.is_broadcast_rpc(message):
            self.logger.info("Broadcast RPCs are not currently handled.")
        elif self.__message_classifier.is_local_rpc(message):
            await self._process_local_rpc(message, client)
        elif self.__message_classifier.is_network_rpc(message):
            await self._process_remote_rpc(message, client)        
        else:
            self.logger.warning("Received unsupported message format.")

    
    
    async def _process_local_rpc(self, message: Dict, client: IMessagingClient) -> None:
        """
        Handles incoming RPC messages intended for local services/modules.

        - Validates the presence of the RPC Gateway module.
        - Forwards the message to the local RPC handler if valid.
        - Sends an error response to the client if the message is not a valid RPC
        or if an error occurs during processing.

        Args:
            message (Dict): The incoming RPC message from the client.
            client (IMessagingClient): The client connection that sent the message.
        """
        if not self.__modules.hasModule(RPC_GATEWAY_MODULE):
            await client.message_to_client(formatErrorRPCResponse(message["requestid"], "Feature unavailable"))
            return

        rpcgateway: IRPCGateway = self.__modules.getModule(RPC_GATEWAY_MODULE)
        err = None

        try:
            if self.__message_classifier.is_rpc(message):
                await rpcgateway.handleRPC(client, message)
            else:
                self.logger.warning("Unknown message type received")
        except (RPCError, Exception) as e:
            err = str(e) if isinstance(e, RPCError) else f"Unknown error occurred: {e}"
            self.logger.error(err)

        if err and not client.is_closed():
            try:
                await client.message_to_client(formatErrorRPCResponse(message["requestid"], err))
            except:
                self.logger.warning(f"Unable to write message to client {client.id}")


    
    
    async def _process_remote_rpc(self, message: Dict, client: IMessagingClient) -> None:
        """
        Sends RPC requests to a remote service via the Federation Gateway (typically using MQTT).

        - Adds metadata (clientId and originId) to the message.
        - Tracks the message in a directory for future response mapping.
        - Sends the message to the target service if federation is connected.
        - If the federation is unavailable or an error occurs, sends an error response to the client.

        Args:
            message (Dict): The RPC message to forward, expected to contain 'requestid' and 'serviceId'.
            client (IMessagingClient): The client that initiated the request.
        """
        if not self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
            await client.message_to_client(formatErrorRPCResponse(message["requestid"], "Feature unavailable"))
            return

        federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)

        # append additional properties
        message["clientId"] = client.id
        message["originId"] = os.environ["CLOUDISENSE_IDENTITY"]

        requestid = message.get("requestid")
        

        try:
            if not federation_gateway.is_connected():
                raise ConnectionError("Federation not connected")
            
            if requestid:
                self.__message_directory.set(requestid, tuple(message, client))  # Track for response mapping
                

            target_service_id = message["serviceId"]
            
            await federation_gateway.send_message(target_service_id, message)
            self.logger.info(f"Forwarded RPC to remote service: {target_service_id}")
        except Exception as e:
            self.logger.error(f"Failed to forward RPC: {e}")
            if requestid:
                await client.message_to_client(formatErrorRPCResponse(requestid, str(e)))




    async def _handle_remote_message(self, message: Dict, client: "IMessagingClient" = None) -> None:
        """
        Handles incoming remote messages by adding them to the incoming messages queue.
        
        Parameters:
        - message (Dict): The incoming message to be processed.
        - client (IMessagingClient, optional): The client that sent the message (defaults to None).
        
        This function adds the message to the __incoming_messages queue for further processing.
        In case of an error, it catches and logs the exception without affecting the message queue.
        """
        try:
            await self.__incoming_messages.put(message)
            self.logger.debug(f"Message successfully added to the queue: {message}")
        except Exception as e:
            self.logger.error(f"Error while adding message to the queue: {e}")
        
    
    
    
    async def handle_remote_response(self, response: Dict) -> None:
        """
        Handles RPC responses received from remote services via the Federation Gateway.

        - Looks up the original client associated with the request using the request ID.
        - If the client is found:
            - Forwards either the result or error message back to the client.
        - If the client is not found:
            - Logs a warning indicating that the response could not be routed.

        Args:
            response (Dict): The RPC response from the remote service. Should contain:
                            - 'requestid': ID used to map the response to a client.
                            - 'result' or 'error': Response payload or error message.
        """
        requestid = response.get("requestid")
        client: IMessagingClient = self.__message_directory.pop(requestid, None)

        if not client:
            self.logger.warning(f"No client found for request ID: {requestid}")
            return

        if response.get("error"):
            message = response.get("error")
            await client.message_to_client(formatErrorRPCResponse(requestid, message))
        else:
            result = response.get("result")
            await client.message_to_client(formatSuccessRPCResponse(requestid, result))




    async def _handle_broadcast_rpc(self, message: Dict) -> None:
        """
        Handles broadcast RPC messages (serviceId="*") received from the cluster.
        Invokes the RPC locally without expecting a response (fire-and-forget).
        """
        if not self.__modules.hasModule(RPC_GATEWAY_MODULE):
            self.logger.warning("Broadcast RPC ignored: RPC_GATEWAY_MODULE is not available.")
            return
        
        rpcgateway: IRPCGateway = self.__modules.getModule(RPC_GATEWAY_MODULE)
        
        try:
            self.logger.debug(f"Executing broadcast RPC request {str(message)}")
            await rpcgateway.handleRPC(None, message)  # No client context
        except Exception as e:
            self.logger.error(f"Broadcast RPC handling failed: {e}")




    async def initiate_remote_rpc(self, service_id: str, intent: str, params: Dict, on_response: Callable):
        """
        Initiates an RPC call from the local Cloudisense instance to a remote Cloudisense service.

        This method is used internally (not by browser clients) to invoke a method on a remote node 
        via the Federation Gateway (MQTT). Optionally registers a callback to handle the response 
        when it returns.

        Args:
            service_id (str): The target Cloudisense instance to route the RPC to.
            intent (str): The name of the remote method or action to call.
            params (Dict): Dictionary of parameters to pass along with the RPC call.
            on_response (Callable, optional): A coroutine or function to handle the response.
                                            If provided, it is stored and triggered when
                                            the response arrives via federation.

        Behavior:
            - Generates a unique request ID.
            - Constructs a well-formed RPC message including origin metadata.
            - Stores the request ID and response handler (if any) in `__message_directory`.
            - Sends the message over the Federation Gateway to the target service.
        """
        requestid = str(uuid.uuid4())
        message =  formatRemoteRPCRequest(requestid, intent, params, service_id, os.environ["CLOUDISENSE_IDENTITY"])
        
        if on_response:
            self.__message_directory.set(requestid, on_response)
            
        federation: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
        
        try:
            federation.send_message(service_id, message)
        except Exception as e:
            self.logger.error(f"Failed to send federation message to {service_id}: {e}")
    
    
    
    async def initiate_remote_broadcast(self, intent: str, params: Dict) -> None:
        
        requestid = str(uuid.uuid4())
        message =  formatFederationBroadcastRequest(requestid, intent, params, os.environ["CLOUDISENSE_IDENTITY"])
        federation: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
        
        try:
            federation.send_broadcast(message)
        except Exception as e:
            self.logger.error(f"Failed to send federation broadcast of {str(message)}: {e}")        
        
    
    
    async def __process_messages(self):
        """
        Background task that continuously processes incoming messages from the queue.

        - Waits for new messages on the `__incoming_messages` queue.
        - Classifies the message type using the message classifier.
        - If the message is an RPC response and matches a tracked request ID:
            - Retrieves the associated client and forwards the response.
        - Logs and handles other message types such as broadcasts and new RPC requests.
        - Marks the message as processed via `task_done()` once handling is complete.
        """
        while True:
            incoming_message: Dict = await self.__incoming_messages.get()
            self.logger.debug(f"Processing message: {incoming_message}")            
            requestid = incoming_message.get("requestid")     
            origin_id = incoming_message.get("originId")  
            
            if not requestid:
                self.logger.warning("Received message without requestid")
                self.__incoming_messages.task_done()
                continue             

            if self.__message_classifier.is_rpc_response(incoming_message):
                self.logger.debug(f"RPC response found")                    
                if self.__message_directory.has(requestid):                    
                    entry = self.__message_directory.pop(requestid)
                    if callable(entry):
                        await entry(incoming_message)
                    elif isinstance(entry, tuple):
                        message, client = entry
                        await self.handle_remote_response(message, client)
                    
                    
            elif self.__message_classifier.is_broadcast_rpc(incoming_message):
                self.logger.debug(f"Broadcast message received from {origin_id}")
                if origin_id and origin_id != os.environ["CLOUDISENSE_IDENTITY"]:
                    await self._handle_broadcast_rpc(incoming_message)
            
            
            elif self.__message_classifier.is_rpc(incoming_message):
                self.logger.debug(f"RPC message received from remote service {origin_id}")  
                if origin_id and self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
                    federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
                    remote_client = RemoteMessagingClient(origin_id, federation_gateway)
                    await self._process_local_rpc(incoming_message, remote_client)                                        
            
            else:
                self.logger.warning(f"Unknown message type received")

            
            self.logger.debug(f"Finished processing message for requestid: {requestid}")
            self.__incoming_messages.task_done()