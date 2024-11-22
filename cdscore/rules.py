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


import re
import time


from builtins import str
from enum import Enum
from typing import Any, Dict, List, Text, Union
from abc import ABCMeta, abstractmethod

from cdscore.event import EventType


SIMPLE_RULE_EVALUATOR = "SimpleRuleEvaluator"
REG_EX_RULE_EVALUATOR = "RegExRuleEvaluator"



class RuleResponseBehaviourType(Enum):
    
    NORMAL = "normal"
    JUSTONCE = "once"
    SLEEPY = "sleepy"


    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_ 



class RuleResponseBehaviour(metaclass=ABCMeta):
    
    @abstractmethod
    def name(self) -> Text:
        "Returns the string name of behaviour"
    

    @abstractmethod
    def type(self) -> RuleResponseBehaviourType:
        "Returns the type of behaviour"
    
    
    @abstractmethod
    def can_execute(self) -> bool:
        "Returns true if behaviour is executable, otherwise return false"




class NormalRuleResponseBehaviour(RuleResponseBehaviour):

    def __init__(self):
        '''
        Constructor
        '''

        super().__init__()
        self.__type:RuleResponseBehaviourType = RuleResponseBehaviourType.NORMAL


    def name(self) -> Text:
        return self.__type.value
    
    def type(self) -> RuleResponseBehaviourType:
        return self.__type
    
    def can_execute(self) -> bool:
        return True



class OneTimeRuleResponseBehaviour(RuleResponseBehaviour):


    def __init__(self):
        '''
        Constructor
        '''

        super().__init__()
        self.__type:RuleResponseBehaviourType = RuleResponseBehaviourType.JUSTONCE
        self.__use_count:int = 0


    def name(self) -> Text:
        return self.__type.value
    
    
    def type(self) -> RuleResponseBehaviourType:
        return self.__type
    
    
    def can_execute(self) -> bool:
        if self.__use_count > 0:
            return False
        
        self.__use_count = self.__use_count + 1
        return True



class SleepyRuleResponseBehaviour(RuleResponseBehaviour):


    def __init__(self):
        '''
        Constructor
        '''

        super().__init__()
        self.__type:RuleResponseBehaviourType = RuleResponseBehaviourType.SLEEPY
        self.__min_sleep_delay:int = 10000 # ms
        self.__last_exec_time:int = 0 # ms


    def name(self) -> Text:
        return self.__type.value
    
    
    
    def type(self) -> RuleResponseBehaviourType:
        return self.__type
    


    def can_execute(self) -> bool:
        nowtime = self.current_milli_time()
        if nowtime - self.__last_exec_time > self.__min_sleep_delay:            
            self.__last_exec_time = nowtime
            return True
        else:
            return False
    
    
    
    def current_milli_time(self):
        return round(time.time() * 1000)        

    
    @property
    def sleep_delay(self) ->RuleResponseBehaviour:
        return self.__min_sleep_delay
        
        
    @sleep_delay.setter
    def sleep_delay(self, _min_sleep_delay:int)->None:
        self.__min_sleep_delay = _min_sleep_delay



class IRuleResponseBehaviourBuilder(metaclass=ABCMeta):
    "The Builder Interface"

    @staticmethod
    @abstractmethod
    def build_response_behaviour():
        "Build response behaviour"

    @staticmethod
    @abstractmethod
    def get_behaviour():
        "Return the final behaviour object"



class RuleResponseBehaviourBuilder(IRuleResponseBehaviourBuilder):

    def __init__(self):
        '''
        Constructor
        '''
        self.__behaviour:RuleResponseBehaviour = None



    def from_behaviour_config(self, config:Dict)->IRuleResponseBehaviourBuilder:
        self.__behaviour_config = config
        return self
        


    def build_response_behaviour(self)->IRuleResponseBehaviourBuilder:

        if "type" not in self.__behaviour_config:
            self.__behaviour = NormalRuleResponseBehaviour()
        else:
            spec_type:str = str(self.__behaviour_config["type"])
            detected_type:RuleResponseBehaviourType = None
            
            for responsetype in RuleResponseBehaviourType:
                if spec_type.lower() == str(responsetype.value).lower():
                    detected_type = responsetype
                    break
            
            if detected_type == None:
                raise ValueError("Invalid behaviour type `"+ spec_type + "` specified")
            elif detected_type == RuleResponseBehaviourType.NORMAL:
                self.__behaviour = NormalRuleResponseBehaviour()
            elif detected_type == RuleResponseBehaviourType.JUSTONCE:
                self.__behaviour = OneTimeRuleResponseBehaviour()
            elif detected_type == RuleResponseBehaviourType.SLEEPY:
                self.__behaviour = SleepyRuleResponseBehaviour()

                if "sleep" in self.__behaviour_config:
                    sleep_delay:int = self.__behaviour_config["sleep"]
                    self.__behaviour.sleep_delay = sleep_delay

            return self



    def get_behaviour(self)->RuleResponseBehaviour:
        if self.__behaviour is None:
            raise RuntimeError("Behaviour was never built prior to access attempt")
        return self.__behaviour



class RuleResponse(object):
    
    def __init__(self):
        '''
        Constructor
        '''

        self.__behaviour:RuleResponseBehaviour = None
        self.__intent:str = None
        self.__parameters:Dict = {}
    
    
    @property
    def behaviour(self) ->RuleResponseBehaviour:
        return self.__behaviour
        
        
    @behaviour.setter
    def behaviour(self, _behaviour:RuleResponseBehaviour)->None:
        self.__behaviour = _behaviour
    
    
    @property
    def intent(self) ->Text:
        return self.__intent
        
        
    @intent.setter
    def intent(self, _intent:Text) -> None:
        self.__intent = _intent
    
    
    @property
    def parameters(self):
        return self.__parameters
        
        
    @parameters.setter
    def parameters(self, _parameters):
        self.__parameters = _parameters



class RuleExecutionEvaluator(object):
    
    @abstractmethod
    def name(self) -> Text:
        raise NotImplementedError()
    
    
    @abstractmethod
    def evaluate(self, haystack, needle, condition) -> bool:
        raise NotImplementedError();
        pass



class SimpleRuleEvaluator(RuleExecutionEvaluator):
    
    
    def name(self) -> Text:
        return SIMPLE_RULE_EVALUATOR
    
    
    def evaluate(self, data:Any, expected_content:Union[str, int, bool], condition_clause:str)-> bool:
        
        if condition_clause =="contains":
            if str(data).contains(expected_content):
                return True
            return False
        elif condition_clause =="equals":
            if str(data) == expected_content:
                return True
            return False
        elif condition_clause =="startswith":
            if str(data).startswith(expected_content):
                return True
            return False
        elif condition_clause =="endswith":
            if str(data).endswith(expected_content):
                return True
        elif condition_clause =="lessthan":
            if int(data) < int(expected_content):
                return True
            return False
        elif condition_clause =="lessthanorequal":
            if int(data) <= int(expected_content):
                return True
            return False
        elif condition_clause =="greaterthan":
            if int(data) > int(expected_content):
                return True
            return False
        elif condition_clause =="greaterthanorequal":
            if int(data) >= int(expected_content):
                return True
            return False
    

class RegExRuleEvaluator(RuleExecutionEvaluator):
    
    
    def name(self) -> Text:
        return REG_EX_RULE_EVALUATOR
    
    
    def evaluate(self, haystack, regex, condition=None)-> bool:
        pattern = re.compile(condition)
        if pattern.match(haystack):
            return True
        return False



class Trigger(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.__evaluator = None
    

    def __str__(self):
        return (self.__class__.__name__).lower()
        
    
    @property
    def evaluator(self) -> RuleExecutionEvaluator:
        return self.__evaluator
        
        
    @evaluator.setter
    def evaluator(self, _evaluator:RuleExecutionEvaluator):
        self.__evaluator = _evaluator



class TimeTrigger(Trigger):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.__recurring = False
        self.__time_expression = None
    
    
    @property
    def recurring(self):
        return self.__recurring
        
        
    @recurring.setter
    def recurring(self, _recurring):
        self.__recurring = _recurring
        
    
    @property
    def time_expression(self):
        return self.__time_expression
        
        
    @time_expression.setter
    def time_expression(self, _time_expression):
        self.__time_expression = _time_expression



class PayloadTrigger(Trigger):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.__payload_object_key = None
        self.__expected_content = None
        self.__condition_clause = None
    
    
    
    @property
    def expected_content(self) ->str:
        return self.__expected_content
        
        
    @expected_content.setter
    def expected_content(self, _expected_content:str) ->None:
        self.__expected_content = _expected_content
        
        
    @property
    def payload_object_key(self) ->str:
        return self.__payload_object_key
        
        
    @payload_object_key.setter
    def payload_object_key(self, _payload_object_key:str) -> None:
        self.__payload_object_key = _payload_object_key
        
        
    @property
    def condition_clause(self) ->str:
        return self.__condition_clause
        
        
    @condition_clause.setter
    def condition_clause(self, _condition_clause:str) -> None:
        self.__condition_clause = _condition_clause
    

        
        


class ReactionRule(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.__id = None
        self.__description = None
        self.__trigger = None
        self.__response = None
        self.__enabled = False
        self.__target_topic = "*"
        self.__target_event = "*"
    
    
    def _deep_access(self, x,keylist):
        val = x
        for key in keylist:
            val = val[key]
        return val
    

    def _deep_access2(self, d:dict, keys:str):
        if "." in keys:
            key, rest = keys.split(".", 1)
            return self._deep_access2(d[key], rest)
        else:
            return d[keys]
        
    
    def __can_execute(self, event:EventType):
        
        evaluator = self.trigger.evaluator 
        if evaluator:
            if isinstance(self.trigger, PayloadTrigger):
                expected_content = self.trigger.expected_content 
                condition_clause = self.trigger.condition_clause
                key = self.trigger.payload_object_key
                data = self._deep_access2(event,key)

                return evaluator.evaluate(data, expected_content, condition_clause)
             
            elif isinstance(self.trigger, TimeTrigger):
                # To Do
                pass
            
            else:
                raise TypeError("Unknown trigger type")
                pass       
        return True
    
    
    
    def __is_eligible(self, event:EventType):
        
        if self.__target_topic != "{time}":
            if self.__target_topic != "*":
                if  self.__target_topic == event["topic"]:
                    if self.__target_event != "*":
                        if self.__target_event == event["name"].lower():
                            return True
                    else:
                        return True
            else:
                if self.__target_event != "*":
                    if self.__target_event == event["name"].lower():
                            return True
                else:
                    return True
        else:
            return False
    
    
    '''
        Determines if the rule can be applied based on topic path 
        and event name.
    '''
    def is_applicable(self, event:EventType) ->bool:
        
        return self.__is_eligible(event)

        '''
        if self.__is_eligible(event):
            return self.__can_execute(event)
        else:
            return False
        '''



    '''
        Determines if the rule can be executed based trigger condition
    '''
    def is_executable(self, event:EventType) ->bool:        
        return self.__can_execute(event)

        
        
    
    @property
    def id(self) -> Text:
        return self.__id
    

    @id.setter
    def id(self, _id:Text) -> None:
        self.__id = _id
        
        
    @property
    def description(self) -> Text:
        return self.__description
    

    @description.setter
    def description(self, _description:Text):
        self.__description = _description
    
    
    @property
    def target_topic(self) -> Text:
        return self.__target_topic
        
        
    @target_topic.setter
    def target_topic(self, _target_topic:Text) -> None:
        self.__target_topic = _target_topic


    @property
    def target_event(self) -> Text:
        return self.__target_event
        
        
    @target_event.setter
    def target_event(self, _target_event:Text) -> None:
        self.__target_event = _target_event
    
    
    @property
    def enabled(self) -> bool:
        return self.__enabled
        
        
    @enabled.setter
    def enabled(self, _enabled:bool) -> None:
        self.__enabled = _enabled    
        
        
    @property
    def trigger(self) -> Trigger:
        return self.__trigger
        
        
    @trigger.setter
    def trigger(self, _trigger:Trigger) -> None:
        self.__trigger = _trigger
    
    
    @property
    def response(self) -> RuleResponse:
        return self.__response
        
        
    @response.setter
    def response(self, _response:RuleResponse) -> None:
        self.__response = _response
        



def built_in_evaluators()->List[RuleExecutionEvaluator]:
    return [SimpleRuleEvaluator(), RegExRuleEvaluator()]



def built_in_evaluator_names():
    return [SIMPLE_RULE_EVALUATOR, REG_EX_RULE_EVALUATOR]



def get_evaluator_by_name(name:Text) ->RuleExecutionEvaluator:
   
    for evaluator in built_in_evaluators():
        if evaluator.name().lower() == name.lower():
            return evaluator
    
    return None 