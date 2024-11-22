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

from typing import List, Text


INTENT_PREFIX = "intent_"


'''
Intent name constants
'''

INTENT_TEST_NAME = INTENT_PREFIX + "test"

INTENT_GET_SOFTWARE_VERSION_NAME = INTENT_PREFIX + "get_software_version"

INTENT_HTTP_GET_NAME = INTENT_PREFIX + "http_get"

INTENT_REBOOT_SYSTEM_NAME = INTENT_PREFIX + "reboot_system"

INTENT_GET_SYSTEM_TIME_NAME = INTENT_PREFIX + "get_system_time"

INTENT_FORCE_GARBAGE_COLLECTION_NAME = INTENT_PREFIX + "force_garbage_collection"

INTENT_GET_SYSTEM_STATS_NAME = INTENT_PREFIX + "get_system_stats"

INTENT_GET_MEMORY_STATS_NAME = INTENT_PREFIX + "get_memory_stats"

INTENT_GET_CPU_STATS_NAME = INTENT_PREFIX + "get_cpu_stats"

INTENT_START_LOG_RECORDING_NAME = INTENT_PREFIX + "start_log_recording"

INTENT_STOP_LOG_RECORDING_NAME = INTENT_PREFIX + "stop_log_recording"

INTENT_INVOKE_ON_TARGET_NAME = INTENT_PREFIX + "fulfill_target_request"

INTENT_RESTART_TARGET_NAME = INTENT_PREFIX + "restart_target"

INTENT_STOP_TARGET_NAME = INTENT_PREFIX + "stop_target"

INTENT_START_TARGET_NAME = INTENT_PREFIX + "start_target"

INTENT_LIST_TARGETS_NAME = INTENT_PREFIX + "list_targets"

INTENT_SUBSCRIBE_CHANNEL_NAME = INTENT_PREFIX + "subscribe_channel"

INTENT_UNSUBSCRIBE_CHANNEL_NAME = INTENT_PREFIX + "unsubscribe_channel"

INTENT_REMOVE_CHANNEL_NAME = INTENT_PREFIX + "remove_channel"

INTENT_CREATE_CHANNEL_NAME = INTENT_PREFIX + "create_channel"

INTENT_PUBLISH_CHANNEL_NAME = INTENT_PREFIX + "publish_channel"

INTENT_RUN_DIAGNOSTICS_NAME = INTENT_PREFIX + "run_diagnostics"

INTENT_SEND_MAIL_NAME = INTENT_PREFIX + "send_mail"

INTENT_WRITE_LOG_CHUNKS_NAME = INTENT_PREFIX + "write_log_chunks"

INTENT_BOT_NOTIFY_NAME = INTENT_PREFIX + "bot_notify"

INTENT_UPDATE_ACCESSIBLE_PATHS_NAME = INTENT_PREFIX + "update_accessible_paths"




def built_in_intents() -> List[Text]:
    return [INTENT_REBOOT_SYSTEM_NAME, INTENT_GET_SYSTEM_TIME_NAME, INTENT_FORCE_GARBAGE_COLLECTION_NAME, INTENT_GET_SYSTEM_STATS_NAME, INTENT_GET_MEMORY_STATS_NAME, INTENT_GET_CPU_STATS_NAME, 
            INTENT_START_LOG_RECORDING_NAME, INTENT_STOP_LOG_RECORDING_NAME, INTENT_INVOKE_ON_TARGET_NAME, INTENT_RESTART_TARGET_NAME, INTENT_LIST_TARGETS_NAME, INTENT_STOP_TARGET_NAME, INTENT_START_TARGET_NAME, INTENT_SUBSCRIBE_CHANNEL_NAME, 
            INTENT_UNSUBSCRIBE_CHANNEL_NAME, INTENT_REMOVE_CHANNEL_NAME, INTENT_CREATE_CHANNEL_NAME, INTENT_PUBLISH_CHANNEL_NAME, INTENT_RUN_DIAGNOSTICS_NAME, INTENT_GET_SOFTWARE_VERSION_NAME, INTENT_HTTP_GET_NAME,
            INTENT_SEND_MAIL_NAME, INTENT_TEST_NAME, INTENT_WRITE_LOG_CHUNKS_NAME, INTENT_BOT_NOTIFY_NAME,
            INTENT_UPDATE_ACCESSIBLE_PATHS_NAME]
    


def str_to_intent(command:str):
    
    if not command.startswith("intent_"):
        return "intent_" + command
    



def is_valid_intent(command:str):
    
    if command in built_in_intents():
        return True
    
    return False
    
