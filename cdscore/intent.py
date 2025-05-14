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


INTENT_PREFIX = "intent_"


'''
Intent name constants
'''

INTENT_TEST_NAME = INTENT_PREFIX + "test"

INTENT_HTTP_GET_NAME = INTENT_PREFIX + "http_get"

INTENT_SUBSCRIBE_CHANNEL_NAME = INTENT_PREFIX + "subscribe_channel"

INTENT_UNSUBSCRIBE_CHANNEL_NAME = INTENT_PREFIX + "unsubscribe_channel"

INTENT_REMOVE_CHANNEL_NAME = INTENT_PREFIX + "remove_channel"

INTENT_CREATE_CHANNEL_NAME = INTENT_PREFIX + "create_channel"

INTENT_PUBLISH_CHANNEL_NAME = INTENT_PREFIX + "publish_channel"

INTENT_START_LOG_RECORDING_NAME = INTENT_PREFIX + "start_log_recording"

INTENT_STOP_LOG_RECORDING_NAME = INTENT_PREFIX + "stop_log_recording"

INTENT_WRITE_LOG_CHUNKS_NAME = INTENT_PREFIX + "write_log_chunks"

INTENT_SET_SERVICE_OF_INTEREST_NAME = INTENT_PREFIX + "notify_service_of_interest"



def built_in_intents() -> List[Text]:
    return [INTENT_SET_SERVICE_OF_INTEREST_NAME, INTENT_SUBSCRIBE_CHANNEL_NAME, INTENT_UNSUBSCRIBE_CHANNEL_NAME, INTENT_REMOVE_CHANNEL_NAME, 
            INTENT_CREATE_CHANNEL_NAME, INTENT_PUBLISH_CHANNEL_NAME, INTENT_HTTP_GET_NAME,INTENT_TEST_NAME]
    


def str_to_intent(command:str):
    
    if not command.startswith("intent_"):
        return "intent_" + command
    



def is_valid_intent(command:str):
    
    if command in built_in_intents():
        return True
    
    return False
    
