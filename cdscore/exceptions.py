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

class TargetServiceError(Exception):
    """Base class for other exceptions"""
    pass


class FileSystemOperationError(Exception):
    """Base class for other exceptions"""
    pass

class FileUploadError(Exception):
    """Base class for other exceptions"""
    pass


class AccessPermissionsError(Exception):
    """Base class for other exceptions"""
    pass


class ConfigurationLoadError(Exception):
    """Base class for other exceptions"""
    pass

class RPCError(Exception):
    """Base class for other exceptions"""
    pass


class ModuleNotFoundError(Exception):
    """Base class for other exceptions"""
    pass


class RunnableScriptError(Exception):
    """Base class for other exceptions"""
    pass

class RulesError(Exception):
    """Base class for other exceptions"""
    pass

class ActionError(Exception):
    """Base class for other exceptions"""
    pass