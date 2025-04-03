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



import uuid
import json
import logging
import os
import random
import logging
import tornado
import copy

from typing import Dict, Set
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
from cdscore.helpers import formatErrorRPCResponse, formatSuccessRPCResponse
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
    '''
    classdocs
    '''


    def __init__(self, modules:Modules, conf = None, executor:ThreadPoolExecutor = None):
        '''
        Constructor
        '''
        super().__init__()
    
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__conf = conf
        self.__modules = modules
        self.__action_book = {}
        self.__request_register = {}
        self.__executor = executor  if executor is not None else executor        
        tornado.ioloop.IOLoop.current().spawn_callback(self.__initialize)
    pass



    def __initialize(self):
        
        # To do build intent-action map
        for intent_name in built_in_intents():
            
            try:
                action_name = str(intent_name).replace(INTENT_PREFIX, ACTION_PREFIX)
                action:Action = action_from_name(action_name)
                
                if action:
                    self.registerActionforIntent(intent_name, action)
                    self.logger.debug("Registered intent by name" + intent_name + " for action " + action_name)
                else:
                    raise TypeError("'action' for intent " + intent_name + " was None, where object of type 'Action' was expected") 
           
            except TypeError as te:
                self.logger.warning(str(te))
                pass





    def registerActionforIntent(self, intent_name:Text, action:Action):
        
        if intent_name in self.__action_book:
            raise ValueError("intent "+intent_name+" is already registered for an action")
        
        self.__action_book[intent_name] = {"action": action, "requests": Queue(maxsize=5)} 
        tornado.ioloop.IOLoop.current().spawn_callback(self.__task_processor, intent_name)
        
        pass
    
    
    
    
    
    def registerActionByNameforIntent(self, intent_name:Text, action_name:Text):
        
        
        actions_names = builtin_action_names()
        
        if action_name not in actions_names:
            raise ValueError("Invalid action name "+action_name)
        
        if intent_name in self.__action_book:
            raise ValueError("intent "+intent_name+" is already registered for an action")
        
        action:Action = action_from_name(action_name)
        
        self.__action_book[intent_name] =  {"action": action, "requests": Queue(maxsize=5)} # make 5 configurable
        tornado.ioloop.IOLoop.current().spawn_callback(self.__task_processor, intent_name)
        
        pass
    
    
    
    '''
        Accepts parameters and creates a request object
    '''     
    def _build_request(self, requester:IntentProvider, intent:Text, params:object):
        
        command_params = None
        
        if isinstance(params,str):
            params = json.loads(params)
        elif isinstance(params, list):
            it = iter(params)
            params = dict(zip(it, it))
        elif not isinstance(params, dict):
            raise ValueError("incompatible param type. dict is required")
            
        
        return {
            "requestid": SmallUUID().hex,
            "requester":requester,
            "intent": intent,
            "params": params,
            "timestamp": int(round(time() * 1000))
        }
        pass
    
    
    
    
    
    
    '''
        Handles intent requests from -> requesters must implement special interface to be notified of result, error or progress
    ''' 
    async def handle_request(self, requester:IntentProvider, intent:Text, params:dict, event:EventType=None):
        
        ''' if we have event info pass that to action as well '''
        if event:
            params = self.merge_parameters(params, event)
        
        intent_name = (INTENT_PREFIX + intent) if not intent.startswith(INTENT_PREFIX) else intent
        
        if intent_name not in self.__action_book:
            raise KeyError("Unknown intent " + intent_name)
        
        req_queue:Queue = self.__action_book[intent_name]["requests"]
        req = self._build_request(requester, intent, params)
        self.__request_register[req["requestid"]] = req
        
        await req_queue.put(req)
        return req["requestid"]
    
    
    
    
    '''
        Handles intent requests from -> requesters must implement special interface to be notified of result, error or progress
    ''' 
    async def handle_request_direct(self, requester:IntentProvider, intent:Text, params:dict):
        
        intent_name = (INTENT_PREFIX + intent) if not intent.startswith(INTENT_PREFIX) else intent
        
        if intent_name not in self.__action_book:
            raise KeyError("Unknown intent " + intent_name)
        
        response = None
        requester:IntentProvider = None
        events:List[EventType] = None
        executable:Action = None
    
        try:
            action:Action = self.__action_book[intent_name]["action"]
            executable = copy.deepcopy(action)          
            result:ActionResponse = None
            
            if action.is_async():
                result = await executable.execute(requester, self.__modules, params)
            else:
                result = await IOLoop.current().run_in_executor(
                    self.__executor,
                    executable.execute, requester, self.__modules, params
                    )
            
            events = result.events
            return result.data
                             
        except Exception as e:
            
            err = "Error executing action " + str(e)                
            self.logger.debug(err)
            raise ActionError(err)
                    
        finally:
            
            if executable != None:
                del executable 
                executable = None
            
            
            if events != None:
                pubsub = self.__modules.getModule(PUBSUBHUB_MODULE)
                for event in events:
                    await pubsub.publish_event_type(event)
    
    
    
    ''' Merges event sict into parameters dict '''
    def merge_parameters(self, params, event:EventType):
        event_dict = {EVENT_KEY:event}
        return{**params, **event_dict}        
    
    
    
    '''
        Task Queue Processor - (Per Intent loop)
    '''
    async def __task_processor(self, intent_name):
        while True:
            
            if not intent_name in self.__action_book:
                break
            
            task_queue:Queue = self.__action_book[intent_name]["requests"]
            requestid:str = None
            
            response = None
            requester:IntentProvider = None
            events:List[EventType] = None
        
            try:
                task_definition = await task_queue.get()
                
                requestid = task_definition["requestid"]
                intent:str = task_definition["intent"]
                args:dict = task_definition["params"]
                requester:IntentProvider = task_definition["requester"]
                action:Action = self.__action_book[intent_name]["action"]
                
                executable = copy.deepcopy(action)  
                # implement flywheeel pattern here              
                result:ActionResponse = await executable.execute(requester, self.__modules, args)
                events = result.events
                
                if requester:
                    await  requester.onIntentProcessResult(requestid, result.data)
                                 
            except Exception as e:
                
                err = "Error executing action " + str(e)                
                self.logger.debug(err)
                
                if requester:
                    await  requester.onIntentProcessError(requestid, e) 
                
            finally:
                task_queue.task_done()
                
                if requestid != None:
                    del self.__request_register[requestid]
                                
                if events != None:
                    pubsub = self.__modules.getModule(PUBSUBHUB_MODULE)
                    for event in events:
                        await pubsub.publish_event_type(event)


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
        return self.is_rpc(message) and "serviceId" in message and "clientId" not in message

    def is_service_to_service_response(self, message: Dict) -> bool:
        """
        Remote ➝ Local (response to direct RPC, not for browser)
        - 'rpc_response' without 'clientId'
        """
        return self.is_rpc_response(message) and "clientId" not in message
    


class MessageRouter(IEventDispatcher):
    
    def __init__(self, modules: Modules, conf=None, executor: ThreadPoolExecutor = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__modules = modules
        self.__message_classifier = MessageClassifier()
        self.__message_directory = {}  # requestid -> client
        self.__messages = Queue()    

    
    
    async def process_messages(self, message: Dict, client: IMessagingClient) -> None:
        """
        Processes incoming messages and determines how to handle them.
        """
        if self.__message_classifier.is_local_rpc(message):
            await self._process_local_rpc_messages(message, client)
        elif self.__message_classifier.is_network_rpc(message):
            await self._forward_to_remote_service(message, client)
        elif self.__message_classifier.is_broadcast_rpc(message):
            self.logger.info("Broadcast RPCs are not currently handled.")
        else:
            self.logger.warning("Received unsupported message format.")

    
    
    async def _process_local_rpc_messages(self, message: Dict, client: IMessagingClient) -> None:
        if not self.__modules.hasModule(RPC_GATEWAY_MODULE):
            await client.message_to_client(formatErrorRPCResponse(message["requestid"], "Feature unavailable"))
            return

        rpcgateway: IRPCGateway = self.__modules.getModule(RPC_GATEWAY_MODULE)
        err = None

        try:
            if rpcgateway.isRPC(message):
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

    
    
    async def _forward_to_remote_service(self, message: Dict, client: IMessagingClient) -> None:
        """
        Adds metadata and sends the RPC request to the remote service over MQTT.
        """
        
        if not self.__modules.hasModule(FEDERATION_GATEWAY_MODULE):
            await client.message_to_client(formatErrorRPCResponse(message["requestid"], "Feature unavailable"))
            return

        federation_gateway: IFederationGateway = self.__modules.getModule(FEDERATION_GATEWAY_MODULE)
        
        
        message["clientId"] = client.id
        message["origin"] = os.environ["CLOUDISENSE_IDENTITY"]

        requestid = message.get("requestid")
        if requestid:
            self.__message_directory[requestid] = client  # Track for response mapping

        target_service_id = message["serviceId"]
        topic = f"cloudisense/service/{target_service_id}/inbox"

        try:
            await federation_gateway.send_message(topic, message)
            self.logger.info(f"Forwarded RPC to remote service: {target_service_id}")
        except Exception as e:
            self.logger.error(f"Failed to forward RPC: {e}")
            if requestid:
                await client.message_to_client(formatErrorRPCResponse(requestid, str(e)))

    
    
    async def handle_remote_response(self, response: Dict) -> None:
        """
        Handles RPC response from remote service and routes it to the correct client.
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
