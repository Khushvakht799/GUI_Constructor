"""
Plugin Manager - handles dynamic loading and management of plugins.
PyQt5 compatible version.
"""

import os
import importlib
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class PluginInfo:
    """Plugin metadata"""
    name: str
    version: str
    author: str
    description: str
    enabled: bool = True


class BasePlugin(ABC):
    """Base class for all plugins"""
    
    def __init__(self, core):
        self.core = core
        self.info = PluginInfo(
            name=self.__class__.__name__,
            version="1.0.0",
            author="Unknown",
            description="No description"
        )
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def get_actions(self) -> List[Dict[str, Any]]:
        """Get list of actions provided by plugin"""
        pass
    
    def cleanup(self):
        """Cleanup resources"""
        pass


class PluginManager:
    """Manages loading and unloading of plugins"""
    
    def __init__(self, core):
        self.core = core
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugins_dir = self._get_plugins_dir()
        
    def _get_plugins_dir(self) -> str:
        """Get plugins directory path"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        plugins_dir = os.path.join(current_dir, '..', 'plugins')
        
        # Create directory if it doesn't exist
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir, exist_ok=True)
            # Create example plugin
            self._create_example_plugin(plugins_dir)
        
        return plugins_dir
    
    def _create_example_plugin(self, plugins_dir: str):
        """Create example plugin for demonstration"""
        example_plugin = os.path.join(plugins_dir, 'example_plugin.py')
        
        if not os.path.exists(example_plugin):
            example_code = '''"""
Example Plugin - demonstrates plugin structure.
"""

from core.plugin_manager import BasePlugin, PluginInfo
from typing import List, Dict, Any


class ExamplePlugin(BasePlugin):
    """Example plugin with basic functionality"""
    
    def __init__(self, core):
        super().__init__(core)
        self.info = PluginInfo(
            name="Example Plugin",
            version="1.0.0",
            author="GUI Constructor Team",
            description="Example plugin demonstrating plugin system"
        )
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        print(f"Initializing {self.info.name}")
        return True
    
    def get_actions(self) -> List[Dict[str, Any]]:
        """Get plugin actions"""
        return [
            {
                'name': 'Example Action',
                'callback': self.example_action,
                'tooltip': 'Example plugin action',
                'icon': None,
                'category': 'Examples'
            },
            {
                'name': 'Show Info',
                'callback': self.show_info,
                'tooltip': 'Show plugin information',
                'icon': None,
                'category': 'Examples'
            }
        ]
    
    def example_action(self):
        """Example action method"""
        print("Example action executed!")
        return {"message": "Example action completed successfully"}
    
    def show_info(self):
        """Show plugin information"""
        info = f"""
        Plugin: {self.info.name}
        Version: {self.info.version}
        Author: {self.info.author}
        Description: {self.info.description}
        """
        print(info)
        return {"info": info}
    
    def cleanup(self):
        """Cleanup plugin"""
        print(f"Cleaning up {self.info.name}")
'''
            with open(example_plugin, 'w', encoding='utf-8') as f:
                f.write(example_code)
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins in plugins directory"""
        if not os.path.exists(self.plugins_dir):
            return []
        
        plugins = []
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith('_plugin.py'):
                plugin_name = filename[:-3]  # Remove .py extension
                plugins.append(plugin_name)
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        Load a plugin by name.
        
        Args:
            plugin_name: Name of plugin to load
            
        Returns:
            BasePlugin: Loaded plugin instance or None
        """
        try:
            # Add plugins directory to Python path
            if self.plugins_dir not in sys.path:
                sys.path.insert(0, self.plugins_dir)
            
            # Import plugin module
            module = importlib.import_module(plugin_name)
            
            # Find plugin class (class name should match filename without _plugin)
            class_name = ''.join(word.capitalize() for word in plugin_name.split('_'))
            
            if hasattr(module, class_name):
                plugin_class = getattr(module, class_name)
                plugin_instance = plugin_class(self.core)
                
                # Initialize plugin
                if plugin_instance.initialize():
                    self.plugins[plugin_name] = plugin_instance
                    print(f"✓ Plugin loaded: {plugin_name}")
                    return plugin_instance
                else:
                    print(f"✗ Failed to initialize plugin: {plugin_name}")
            else:
                print(f"✗ Plugin class {class_name} not found in {plugin_name}")
                
        except ImportError as e:
            print(f"✗ Failed to import plugin {plugin_name}: {e}")
        except Exception as e:
            print(f"✗ Error loading plugin {plugin_name}: {e}")
        
        return None
    
    def load_all_plugins(self) -> Dict[str, BasePlugin]:
        """Load all available plugins"""
        plugin_names = self.discover_plugins()
        
        for plugin_name in plugin_names:
            if plugin_name not in self.plugins:
                self.load_plugin(plugin_name)
        
        return self.plugins
    
    def get_plugin_actions(self) -> List[Dict[str, Any]]:
        """Get all actions from all loaded plugins"""
        actions = []
        
        for plugin_name, plugin in self.plugins.items():
            try:
                plugin_actions = plugin.get_actions()
                for action in plugin_actions:
                    action['plugin'] = plugin_name
                actions.extend(plugin_actions)
            except Exception as e:
                print(f"✗ Error getting actions from {plugin_name}: {e}")
        
        return actions
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of plugin to unload
            
        Returns:
            bool: Success status
        """
        if plugin_name in self.plugins:
            try:
                plugin = self.plugins[plugin_name]
                plugin.cleanup()
                del self.plugins[plugin_name]
                print(f"✓ Plugin unloaded: {plugin_name}")
                return True
            except Exception as e:
                print(f"✗ Error unloading plugin {plugin_name}: {e}")
        
        return False
    
    def unload_all_plugins(self):
        """Unload all plugins"""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a plugin"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].info
        return None
    
    def is_plugin_loaded(self, plugin_name: str) -> bool:
        """Check if plugin is loaded"""
        return plugin_name in self.plugins
    
    def execute_plugin_action(self, plugin_name: str, action_name: str, **kwargs) -> Any:
        """
        Execute a specific action from a plugin.
        
        Args:
            plugin_name: Name of the plugin
            action_name: Name of the action to execute
            **kwargs: Arguments to pass to the action
            
        Returns:
            Any: Result of the action execution
        """
        if plugin_name not in self.plugins:
            return {"error": f"Plugin '{plugin_name}' not loaded"}
        
        plugin = self.plugins[plugin_name]
        
        # Find the action by name
        actions = plugin.get_actions()
        for action in actions:
            if action['name'] == action_name:
                try:
                    callback = action['callback']
                    if callable(callback):
                        return callback(**kwargs)
                    else:
                        return {"error": f"Action '{action_name}' is not callable"}
                except Exception as e:
                    return {"error": f"Error executing action '{action_name}': {str(e)}"}
        
        return {"error": f"Action '{action_name}' not found in plugin '{plugin_name}'"}