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



import asyncio
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
from cdscore.abstracts import ICloudisenseApplication, IFederationGateway, IMessagingClient, IPubSubHub, IRPCGateway, ITaskExecutor, IntentProvider, IClientChannel, IEventHandler, IEventDispatcher, IModule, IntentProvider
from cdscore.exceptions import ActionError, RPCError
from cdscore.helpers import formatErrorRPCResponse, formatFederationBroadcastRequest, formatOutgoingEvent, formatRemoteRPCRequest, formatSuccessRPCResponse
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




class PubSubHub(IModule, IPubSubHub):
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
        self.__message_flush_config = self.__config["message_flush"]
        self.__dynamic_topic_config = self.__config["dynamic_topics"]
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
    def supported_actions(self) -> List[Action]:
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
    
    
    def _format_topic_with_identity(self, identity: str, topicname: str) -> str:
        """
        Constructs a fully qualified topic path with optional identity prefix.

        If identity is provided, the topic will be prefixed with it (e.g., "/node-1/logs/error").
        If identity is None or empty, only the topic will be used (e.g., "/logs/error").

        Ensures the result starts with a single '/' and no duplicate slashes appear.

        Args:
            identity (str): The identity (e.g., service or node name). Optional.
            topicname (str): The raw topic string.

        Returns:
            str: A normalized topic string.
        """
        clean_topic = topicname.lstrip('/')
        if identity:
            clean_identity = identity.strip('/')
            return f"/{clean_identity}/{clean_topic}"
        else:
            return f"/{clean_topic}"


        

    def subscribe(self, topicname: str, client: IMessagingClient = None, to_identity: Optional[str] = None):
        """
        Subscribes a client to a namespaced topic channel.

        The topic is automatically prefixed with the target identity (default: local node identity).
        If the topic channel does not exist and dynamic topic creation is enabled,
        it will be created using the default configuration.

        Args:
            topicname (str): The raw topic name to subscribe to (e.g., "logs/system").
            client (IMessagingClient, optional): The client to subscribe to the topic.
            to_identity (str, optional): The identity to prefix the topic with. If None, uses CLOUDISENSE_IDENTITY.
        """
        topic = self._format_topic_with_identity(to_identity, topicname)

        if topic not in self.channels:
            if self.__config.get("allow_dynamic_topics", False):
                default_cfg = self.__dynamic_topic_config
                channel_info = {
                    "name": topic,
                    "type": default_cfg["type"],
                    "queue_size": default_cfg["queue_size"],
                    "max_users": default_cfg["max_users"]
                }
                self.createChannel(channel_info)
                self.logger.info("Created dynamic channel for topic: %s", topic)
            else:
                self.logger.error("Topic channel '%s' does not exist and dynamic topics are disabled", topic)
                return

        if client is not None:
            clients: Set[IMessagingClient] = self.channels[topic][3]  # assume index 3 holds the client set
            clients.add(client)
            self.logger.info("Client subscribed to topic '%s'. Total clients: %d", topic, len(clients))

        
    
    def subscribe_topics(self, topics:List[str], client:IMessagingClient, to_identity: Optional[str] = None):
        '''
        Client subscribe to multiple topics
        ''' 
        for topicname in topics:
            self.subscribe(topicname, client, to_identity)
            pass    
   
   
    
    def unsubscribe(self, topicname: str, client: IMessagingClient, to_identity: Optional[str] = None):
        """
        Unsubscribes a client from a namespaced topic channel.

        The topic is automatically prefixed with the given identity (or defaults to the local node's
        CLOUDISENSE_IDENTITY). If the topic exists, the client is removed from its subscriber set.

        Args:
            topicname (str): The raw topic name to unsubscribe from.
            client (IMessagingClient): The client to be removed.
            to_identity (str, optional): The identity to prefix the topic with. Defaults to local identity.
        """
        topic = self._format_topic_with_identity(to_identity, topicname)

        if topic in self.channels:
            clients: Set[IMessagingClient] = self.channels[topic][3]  # assume index 3 holds the client set
            clients.discard(client)
            self.logger.info("Client unsubscribed from topic '%s'. Total clients: %d", topic, len(clients))

            # Optional: remove dynamic channel if no clients remain
            # if len(clients) == 0 and self.is_dynamic_channel(topic):
            #     self.removeChannel(topic)
        else:
            self.logger.warning("Attempted to unsubscribe from unknown topic '%s'", topic)
    
    
    

    def clearsubscriptions(self, client:IMessagingClient):
        '''
        clear all subscriptions
        '''
        for key in list(self.channels):
            self.logger.info("Clearing subscriptions in topic %s", key)
            self.unsubscribe(key, client)
        pass
    
    
   
   
    def createChannel(self, channel_info, channel_type="bidirectional"):
        '''
        Creates a dynamic bidirectional communication channel
        '''
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
    
    

    def removeChannel(self, topicname):
        '''
        Removes a communication channel
        '''
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
    
    
    

    async def __submit(self, topicname, message):
        '''
        Accepts data submission for topic
        '''
        if topicname in self.channels:
            msgque:Queue = self.channels[topicname][2] #queue
            #await msgque.put(message)
            try:
                msgque.put_nowait(message)
            except asyncio.QueueFull:
                # handle overflow gracefully
                self.logger.warning(f"Queue full for topic {topicname}, dropping event.")
        pass
    
    

    async def publish_notification(self, event):
        '''
        Publishes event data to a events channel -
        *To be deprecated in favor of new event system*
        '''
        if TOPIC_NOTIFICATION in self.channels:
            if self.__isValidEvent(event):
                await self.__submit(TOPIC_NOTIFICATION, event)
        pass
    
    

    async def publish(self, topicname: str, message, client: IMessagingClient = None):
        """
        Publishes a message to the specified topic channel.

        If the topic does not exist and dynamic topic creation is enabled,
        a new channel is created with default configuration.

        Args:
            topicname (str): The name of the topic to publish to.
            message: The message payload to be submitted.
            client (IMessagingClient, optional): The originating client (if applicable).
        """
        if topicname not in self.channels:
            if self.__config.get("allow_dynamic_topics", False):
                default_cfg = self.__dynamic_topic_config
                channel_info = {
                    "name": topicname,
                    "type": default_cfg["type"],
                    "queue_size": default_cfg["queue_size"],
                    "max_users": default_cfg["max_users"]
                }
                self.createChannel(channel_info)
                self.logger.debug(f"Created dynamic channel for topic: {topicname}")
            else:
                self.logger.error(f"Topic '{topicname}' does not exist and dynamic topics are disabled.")
                return

        await self.__submit(topicname, message)





    async def publish_event(self, event: EventType, for_identity: str = None):
        """
        Publishes a **local event** to its associated topic channel.

        The topic will be prefixed with the identity of the publisher (default: this node's
        CLOUDISENSE_IDENTITY) to ensure consistent topic namespacing.

        If the topic is not yet registered and dynamic topic creation is allowed,
        a new channel will be created using default configuration.

        Args:
            event (EventType): The event dictionary, expected to contain a 'topic' field.
            for_identity (str, optional): Identity to prefix the topic with. Defaults to the local node's identity.
        """
        raw_topic = event.get("topic")
        if not raw_topic:
            return

        # Use provided identity or fallback to this node's identity
        identity = for_identity or os.environ.get("CLOUDISENSE_IDENTITY", "")

        topic = self._format_topic_with_identity(identity, raw_topic)

        # Optionally update the event with the fully qualified topic
        event["topic"] = topic

        # Create dynamic channel if needed
        if topic not in self.channels and self.__config.get("allow_dynamic_topics", False):
            default_cfg = self.__dynamic_topic_config
            self.createChannel({
                "name": topic,
                "type": default_cfg["type"],
                "queue_size": default_cfg["queue_size"],
                "max_users": default_cfg["max_users"]
            })

        # Submit if valid and channel exists
        if topic in self.channels and is_valid_event(event):
            await self.__submit(topic, event)


    
    
    
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
        batch_size = self.__message_flush_config["batch_size"]
        flush_interval = self.__message_flush_config["interval_seconds"] / 1000

        while True:
            try:
                if topic not in self.channels:
                    self.logger.info(f"Topic {topic} removed from system. Flusher shutting down.")
                    break

                channel = self.channels[topic]
                msgque: Queue = channel[2]  # queue
                clients: Set[IMessagingClient] = channel[3]  # subscribers

                batch = []

                # Try to build a batch
                start_time = asyncio.get_event_loop().time()

                while len(batch) < batch_size:
                    remaining_time = flush_interval - (asyncio.get_event_loop().time() - start_time)
                    if remaining_time <= 0:
                        break
                    try:
                        message = await asyncio.wait_for(msgque.get(), timeout=remaining_time)
                        batch.append(message)
                    except asyncio.TimeoutError:
                        break  # No more messages right now

                if batch:
                    if clients:
                        self.logger.debug(f"Pushing {len(batch)} messages to {len(clients)} subscribers...")

                        #payload = [message for message in batch]  # prepare payload
                        payload = batch #json.dumps(batch)

                        ''' pushing batch to clients '''
                        try:
                            for client in clients:
                                await client.message_to_client(payload)  # send entire batch at once
                        except Exception as e:
                            self.logger.error(f"Error pushing batch to client {client} for topic {topic}. Cause: {str(e)}")

                    ''' pushing each message to listeners '''
                    try:
                        for message in batch:
                            for listener in self.getEventListeners():
                                if is_valid_event(message):
                                    await listener._notifyEvent(message)
                    except Exception as e:
                        self.logger.error(f"Error notifying listeners for topic {topic}: {str(e)}")

                # Always mark all messages as task done
                for _ in batch:
                    msgque.task_done()

                await asyncio.sleep(0.01)  # Tiny sleep to avoid CPU burning

            except GeneratorExit:
                self.logger.info(f"GeneratorExit occurred for topic {topic}, shutting down flusher.")
                return

            except Exception as e:
                self.logger.error(f"Unexpected error in flusher for topic {topic}: {str(e)}")
                await asyncio.sleep(0.1)  # recover from temporary error




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

        queue_size = self.__conf["request_queue_size"]
        self.__action_book[intent_name] = {"action": action, "requests": Queue(maxsize=queue_size)}
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
                pubsub:IPubSubHub = self.__modules.getModule(PUBSUBHUB_MODULE)
                for event in events:
                    await pubsub.publish_event(event)


    
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
                    pubsub:IPubSubHub = self.__modules.getModule(PUBSUBHUB_MODULE)
                    for event in events:
                        await pubsub.publish_event(event)


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
    
    
    def is_subscribe_channel_rpc(self, message: Dict) -> bool:
        """True if the message is an subscribe request."""
        return message.get("type") == "rpc" and message.get("intent") == "subscribe_channel"
    
    
    def is_unsubscribe_channel_rpc(self, message: Dict) -> bool:
        """True if the message is an unsubscribe request."""
        return message.get("type") == "rpc" and message.get("intent") == "unsubscribe_channel"
    
    
    def is_local_rpc(self, message: Dict) -> bool:
        """True if the message is an RPC request."""
        return self.is_rpc(message) and message.get("serviceId") == os.environ["CLOUDISENSE_IDENTITY"]

    def is_rpc_response(self, message: Dict) -> bool:
        """True if the message is an RPC response (from service to service or back to client)."""
        return message.get("type") == "rpc_response"
    
    
    def is_event(self, message: Dict) -> bool:
        """True if the message is an event (push data)."""
        return message.get("type") == "event"

    
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



class MessageRouter(IEventDispatcher, IEventHandler):
    
    def __init__(self, modules: Modules, conf=None, executor: ThreadPoolExecutor = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__modules = modules
        self.__message_classifier = MessageClassifier()
        self.__message_directory = SafeLookupStore()
        self.__incoming_messages = Queue()   
        self.initialize() 
        

    def initialize(self) -> None:
        
        self.set_topics_of_interests("*")        
        self.set_events_of_interests("*")
            
        if self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
            federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
            federation_gateway.on_message_handler = self._handle_remote_message
            
        tornado.ioloop.IOLoop.current().spawn_callback(self.__process_messages)   
    
    
    async def handleEvent(self, event: EventType) -> None:
        """
        Handles an incoming local event by checking if the federation gateway module is available
        and, if so, publishing the event to the appropriate topic.

        Args:
            event (EventType): The event object to handle. It is expected to be a dictionary-like
                            structure containing at least a "topic" key.

        Process:
        - Logs the received event at debug level.
        - Checks if the `FEDERATION_GATEWAY_MODULE` is available in the module registry.
        - If the module is present:
            - Formats the event into an outgoing message, tagging it with the current instance's identity.
            - Publishes the formatted message to the corresponding MQTT (or other) topic using the federation gateway.

        Returns:
            None
        """
        self.logger.debug(f"handleEvent {str(event)}")

        if self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
            federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
            identity:str = os.environ["CLOUDISENSE_IDENTITY"]
            message: Dict = formatOutgoingEvent(event, identity)
            topic:str = event["topic"]
            federation_gateway.send_event(topic=topic, payload=message)

     
    
    
    async def subscribe_remote_event(self, serviceId: str, topic: str) -> None:
        """
        Subscribes to a remote event from a specific service via the federation gateway.

        Args:
            serviceId (str): The identifier of the remote service (CloudiSENSE node) from which
                            to subscribe to events.
            topic (str): The event topic to subscribe to.

        Process:
        - Checks if the `FEDERATION_GATEWAY_MODULE` is available in the loaded modules.
        - If the module exists:
            - Retrieves the federation gateway instance.
            - Calls the gateway's `subscribe_to_event()` method to initiate a remote subscription
            for the specified topic from the given service ID.

        Returns:
            None
        """
        if self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
            federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
            federation_gateway.subscribe_to_event(serviceId=serviceId, topic=topic)


       
    async def unsubscribe_remote_event(self, serviceId: str, topic: str) -> None:
        """
        Unsubscribes from a previously subscribed remote event from a specific service 
        via the federation gateway.

        Args:
            serviceId (str): The identifier of the remote service (CloudiSENSE node) 
                            from which the event subscription should be removed.
            topic (str): The event topic to unsubscribe from.

        Process:
        - Checks if the `FEDERATION_GATEWAY_MODULE` is available in the loaded modules.
        - If the module exists:
            - Retrieves the federation gateway instance.
            - Calls the gateway's `unsubscribe_from_event()` method to cancel the 
            remote subscription for the specified topic from the given service ID.

        Returns:
            None
        """
        if self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
            federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
            federation_gateway.unsubscribe_from_event(serviceId=serviceId, topic=topic)
    
    
    
    
    async def handle_messages(self, message: Dict, client: IMessagingClient) -> None:
        """
        Processes an incoming message and determines the appropriate handling strategy 
        based on its classification (broadcast, local, or network RPC).

        Args:
            message (Dict): The incoming message dictionary to be classified and processed.
            client (IMessagingClient): The messaging client interface used to respond 
                                    or interact with the message source.

        Process:
        - Checks the type of RPC message using the internal message classifier.
        - If it is a **broadcast RPC**:
            - Currently not supported; logs an info message.
        - If it is a **local RPC**:
            - Passes the message to `_process_local_rpc()` for local processing.
        - If it is a **network RPC**:
            - Forwards the message to `_process_remote_rpc()` for network-level handling.
        - If the message doesn't match any known type:
            - Logs a warning about the unsupported message format.

        Returns:
            None
        """
        if self.__message_classifier.is_broadcast_rpc(message):
            self.logger.info("Broadcast RPCs are not currently handled.")
        elif self.__message_classifier.is_local_rpc(message):
            await self._process_local_rpc(message, client)
        elif self.__message_classifier.is_network_rpc(message):
            if self.__message_classifier.is_subscribe_channel_rpc(message):
                await self.subscribe_remote_event(message, client)
            elif self.__message_classifier.is_unsubscribe_channel_rpc(message):
                await self.unsubscribe_remote_event(message, client)
            else:
                await self._process_remote_rpc(message, client)
        else:
            self.logger.warning("Received unsupported message format.")



    async def _process_remote_event(self, topic: str, message: Dict) -> None:
        """
        Handles a remote event by publishing it to the local Pub/Sub hub.

        Args:
            topic (str): The topic under which the event should be published locally.
            message (Dict): The event payload received from a remote source.

        Process:
        - Logs the received remote event at debug level.
        - Retrieves the `PubSubHub` module instance from the registered modules.
        - Publishes the message to the local system under the specified topic via the Pub/Sub hub.

        Purpose:
        This method is used to bridge remote events into the local event system, allowing
        distributed CloudiSENSE nodes to propagate events across instances.

        Returns:
            None
        """
        self.logger.debug(f"Remote event : {str(message)}")

        pubsubhub: IPubSubHub = self.__modules.getModule(PUBSUBHUB_MODULE)
        await pubsubhub.publish(topic, message)

        
    
    
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

    
    
    async def subscribe_remote_event(self, message: Dict, client: IMessagingClient):
        """
        Handles a client request to subscribe to a remote event stream (e.g., logs, metrics,etc).

        This is a high-level entrypoint that delegates to a generic internal method
        which performs validation, message forwarding, and subscription handling via
        the Federation Gateway and local Pub/Sub hub.

        -------------------------
        Expected `message` format:
        -------------------------
        {
            "requestid": "<unique-request-id>",
            "serviceId": "<target-remote-service-id>",
            "params": {
                "topic": "<event-topic-name>"
            }
        }

        -------------------------
        Behavior:
        -------------------------
        - Validates federation and connectivity.
        - Forwards the RPC to the remote service.
        - Waits for an ACK response (timeout after 10s).
        - On success, subscribes to the specified event topic:
            - Remotely via the Federation Gateway.
            - Locally via the internal Pub/Sub system.
        - Any errors are reported back to the client.

        Args:
            message (Dict): The incoming RPC message from the client.
            client (IMessagingClient): The connected client instance.

        Raises:
            Sends a formatted error response back to the client if validation fails or federation is unreachable.
        """
        await self._handle_remote_event_subscription(message, client, action="subscribe")

    
    
    
    async def unsubscribe_remote_event(self, message: Dict, client: IMessagingClient):
        """
        Handles a client request to unsubscribe from a remote event stream (e.g., logs, metrics, etc).

        This method is the counterpart to `subscribe_remote_event()` and uses a shared internal handler
        to coordinate communication with the Federation Gateway and internal Pub/Sub system.

        -------------------------
        Expected `message` format:
        -------------------------
        {
            "requestid": "<unique-request-id>",
            "serviceId": "<target-remote-service-id>",
            "params": {
                "topic": "<event-topic-name>"
            }
        }

        -------------------------
        Behavior:
        -------------------------
        - Validates federation connectivity and request structure.
        - Forwards the unsubscribe RPC to the remote service.
        - Waits for an ACK response (timeout after 10s).
        - On success, unsubscribes from the specified event topic:
            - Remotely via the Federation Gateway.
            - Locally via the internal Pub/Sub system.
        - Any errors or failures are reported back to the client.

        Args:
            message (Dict): The incoming RPC message from the client.
            client (IMessagingClient): The connected client instance.

        Raises:
            Sends a formatted error response to the client if request validation fails, 
            federation is unreachable, or the unsubscribe operation times out.
        """
        await self._handle_remote_event_subscription(message, client, action="unsubscribe")

    
    
    
    async def _handle_remote_event_subscription(
        self,
        message: Dict,
        client: IMessagingClient,
        action: str  # either "subscribe" or "unsubscribe"
    ) -> None:
        """
        Generic handler to subscribe or unsubscribe a client to/from a remote event topic via Federation Gateway.

        Supported actions: 'subscribe', 'unsubscribe'.

        ---------------------
        Workflow:
        ---------------------
        1. Validate that the Federation Gateway module is enabled and connected.
        2. Extract required fields from the message:
        - `requestid`: for tracking and response correlation.
        - `serviceId`: the remote target service to contact.
        - `params.topic`: the name of the event topic to subscribe/unsubscribe.
        3. Enrich the message with client metadata:
        - `clientId`: to identify the source client.
        - `originId`: to identify the local CloudiSENSE node.
        4. Register the request and future in the internal message directory.
        5. Forward the RPC message to the remote service using the federation gateway.
        6. Wait asynchronously (with timeout) for an ACK or response from the remote service.
        7. If response is received:
        - Call `subscribe_to_event()` or `unsubscribe_from_event()` on the federation gateway.
        - Call `pubsub.subscribe()` or `pubsub.unsubscribe()` to update local delivery.
        8. If timeout or error occurs:
        - Send an error message to the client.
        9. Log each stage for traceability.

        Args:
            message (Dict): RPC request from the client, containing:
                - 'requestid': Unique request identifier.
                - 'serviceId': ID of the remote service.
                - 'params.topic': Event topic to subscribe/unsubscribe.
            client (IMessagingClient): The client initiating the request.
            action (str): Either 'subscribe' or 'unsubscribe'.

        Raises:
            Sends an error response to the client if:
            - Required fields are missing or invalid.
            - Federation is disconnected.
            - Timeout occurs while waiting for a response.
            - An unsupported action is specified.
        """
        requestid = message.get("requestid")

        if not self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
            if requestid:
                await client.message_to_client(formatErrorRPCResponse(requestid, "Feature unavailable"))
            return

        try:
            target_service_id = message.get("serviceId")
            topic = message.get("params", {}).get("topic")

            federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)

            if not federation_gateway.is_connected():
                raise ConnectionError("Federation not connected")

            if not requestid:
                raise ValueError("Request ID not provided")

            if not topic:
                raise ValueError("Event topic not specified")

            message["clientId"] = client.id
            message["originId"] = os.environ["CLOUDISENSE_IDENTITY"]

            future = asyncio.get_event_loop().create_future()
            self.__message_directory.set(requestid, (message, client, future))

            federation_gateway.send_message(target_service_id, message)
            self.logger.debug(f"Forwarded RPC '{action}' to remote service: {target_service_id}")

            try:
                response = await asyncio.wait_for(future, timeout=10)
                self.logger.debug(f"response : {str(response)}")
                await self.handle_remote_response(message, response, client)
            except asyncio.TimeoutError:
                err = f"Timed out waiting for RPC '{action}' ACK"
                self.logger.error(err)
                await client.message_to_client(formatErrorRPCResponse(requestid, err))
                return

            pubsub: IPubSubHub = self.__modules.getModule(PUBSUBHUB_MODULE)
            service_event_topic = federation_gateway.get_local_subscribable_topic(serviceId=target_service_id, topic=topic)

            if action == "subscribe":
                federation_gateway.subscribe_to_event(serviceId=target_service_id, topic=topic)
                pubsub.subscribe(service_event_topic, client)
                self.logger.debug(f"Subscribed to event topic: {service_event_topic}")
            elif action == "unsubscribe":
                federation_gateway.unsubscribe_from_event(serviceId=target_service_id, topic=topic)
                pubsub.unsubscribe(service_event_topic, client)
                self.logger.debug(f"Unsubscribed from event topic: {service_event_topic}")
            else:
                raise ValueError(f"Unknown action: {action}")

        except Exception as e:
            self.logger.error(f"Failed to handle RPC '{action}': {e}")
            if requestid:
                await client.message_to_client(formatErrorRPCResponse(requestid, str(e)))

 

    
    
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
        requestid = message.get("requestid")

        if not self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
            if requestid:
                await client.message_to_client(formatErrorRPCResponse(requestid, "Feature unavailable"))
            return

        try:
            federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)

            if not federation_gateway.is_connected():
                raise ConnectionError("Federation not connected")

            if not requestid:
                raise ValueError("Request ID not provided")

            future = asyncio.get_event_loop().create_future()
            self.__message_directory.set(requestid, (message, client, future))

            target_service_id = message["serviceId"]
            message["clientId"] = client.id
            message["originId"] = os.environ["CLOUDISENSE_IDENTITY"]

            federation_gateway.send_message(target_service_id, message)
            self.logger.info(f"Forwarded RPC to remote service: {target_service_id}")

            try:
                response = await asyncio.wait_for(future, timeout=10)
                self.logger.debug(f"response : {str(response)}")
                await self.handle_remote_response(message, response, client)
            except asyncio.TimeoutError:
                err = "Timed out waiting for RPC ACK"
                self.logger.error(err)
                msg = formatErrorRPCResponse(requestid, err)
                await client.message_to_client(msg)
                return

        except Exception as e:
            self.logger.error(f"Failed to forward RPC: {e}")
            if requestid:
                await client.message_to_client(formatErrorRPCResponse(requestid, str(e)))

        finally:
            # Always clean up to avoid dangling futures
            entry = self.__message_directory.pop(requestid, None)
            if isinstance(entry, tuple) and len(entry) == 3 and isinstance(entry[2], asyncio.Future):
                if not entry[2].done():
                    entry[2].cancel()




    async def _handle_remote_message(self, topic:str, message: Dict, client: "IMessagingClient" = None) -> None:
        """
        Handles incoming remote messages by adding them to the incoming messages queue.
        
        Parameters:
        - message (Dict): The incoming message to be processed.
        - client (IMessagingClient, optional): The client that sent the message (defaults to None).
        
        This function adds the message to the __incoming_messages queue for further processing.
        In case of an error, it catches and logs the exception without affecting the message queue.
        """
        try:
            # await self.__incoming_messages.put(message)
            try:
                self.__incoming_messages.put_nowait(message)
                self.logger.debug(f"Message successfully added to the queue: {message}")
            except asyncio.QueueFull:
                # handle overflow gracefully
                self.logger.warning(f"Queue full for topic {topic}, dropping event.")                
            
        except Exception as e:
            self.logger.error(f"Error while adding message to the queue: {e}")
        
    
    
    async def handle_remote_response(self, request:Dict, response: Dict, client:IMessagingClient) -> None:
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
        #client: IMessagingClient = self.__message_directory.pop(requestid, None)

        if not client:
            self.logger.warning(f"No client found for request ID: {requestid}")
            return

        if response.get("error"):
            message = response.get("error")
            await client.message_to_client(formatErrorRPCResponse(requestid, message))
        else:
            result = response.get("data")
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

        Responsibilities:
        - Waits for new messages on the `__incoming_messages` queue.
        - Classifies messages using `MessageClassifier`.
        - Routes messages based on type:
            - RPC responses: calls registered callback or resolves future.
            - Broadcast RPCs: executes locally if not from self.
            - RPC requests: executes locally, wrapping remote client.
            - Event messages: routes to appropriate handler (e.g., PubSub).
        - Handles batched event messages (lists).
        - Logs and skips any unrecognized or invalid message types.
        - Always calls `task_done()` after processing.
        """
        while True:
            try:
                incoming_message = await self.__incoming_messages.get()
                self.logger.debug(f"Processing message: {incoming_message}")

                # Handle batched event messages
                if isinstance(incoming_message, list):
                    for msg in incoming_message:
                        if isinstance(msg, dict):
                            await self.__process_message(msg)
                        else:
                            self.logger.warning(f"Invalid item in batch: {msg}")
                    continue

                # Handle single message
                if isinstance(incoming_message, dict):
                    await self.__process_message(incoming_message)

                else:
                    self.logger.warning(f"Ignoring invalid message type: {type(incoming_message)} - {incoming_message}")

            finally:
                self.__incoming_messages.task_done()



    
    async def __process_message(self, incoming_message: Dict):
        """
        Processes a single message (RPC or event) received from the queue.

        Supports:
        - Remote event messages → handled via Federation Gateway and PubSub.
        - RPC responses → resolves registered future or calls callback.
        - Broadcast RPCs → handled locally.
        - RPC requests → processed as if received from virtual remote client.

        Skips invalid or unrecognized messages gracefully.
        """
        try:
            requestid = incoming_message.get("requestid")
            origin_id = incoming_message.get("originId")

            if not requestid and not self.__message_classifier.is_event(incoming_message):
                self.logger.warning("Skipping message: No requestid and not an event")
                return

            # Remote Event
            if self.__message_classifier.is_event(incoming_message):
                self.logger.debug(f"Event message received from remote service {origin_id}")
                topic = incoming_message.get("topic")
                if topic and origin_id and self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
                    await self._process_remote_event(topic, incoming_message)

            # RPC Response
            elif self.__message_classifier.is_rpc_response(incoming_message):
                self.logger.debug("RPC response found")
                if self.__message_directory.has(requestid):
                    entry = self.__message_directory.pop(requestid)

                    if callable(entry):
                        await entry(incoming_message)

                    elif isinstance(entry, tuple):
                        if len(entry) == 3:
                            message, client, future = entry
                            if isinstance(future, asyncio.Future):
                                if not future.done():
                                    self.logger.debug(f"Resolving future for requestid: {requestid}")
                                    future.set_result(incoming_message)
                                else:
                                    self.logger.warning(f"Future already resolved for requestid: {requestid}")
                            else:
                                self.logger.warning(f"Expected Future as third element, got {type(future)}")
                        elif len(entry) == 2:
                            message, client = entry
                            await self.handle_remote_response(message, incoming_message, client)
                        else:
                            self.logger.error(f"Unexpected tuple length ({len(entry)}) for requestid: {requestid}")
                    else:
                        self.logger.error(f"Unsupported entry type in __message_directory for requestid: {requestid} ({type(entry)})")
                else:
                    self.logger.warning(f"Untracked RPC response with requestid: {requestid}")

            # Broadcast RPC
            elif self.__message_classifier.is_broadcast_rpc(incoming_message):
                self.logger.debug(f"Broadcast RPC received from {origin_id}")
                if origin_id and origin_id != os.environ["CLOUDISENSE_IDENTITY"]:
                    await self._handle_broadcast_rpc(incoming_message)

            # RPC Request
            elif self.__message_classifier.is_rpc(incoming_message):
                self.logger.debug(f"RPC message received from remote service {origin_id}")
                if origin_id and self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
                    federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
                    remote_client = RemoteMessagingClient(origin_id, federation_gateway)
                    await self._process_local_rpc(incoming_message, remote_client)

            else:
                self.logger.warning(f"Unknown message type received: {incoming_message.get('type')}")

            self.logger.debug(f"Finished processing message for requestid: {requestid}")

        except Exception as e:
            self.logger.error(f"Error while processing message: {e}", exc_info=True)

            