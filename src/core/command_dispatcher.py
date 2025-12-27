"""
Command Dispatcher - handles execution and undo/redo of commands.
Implements command pattern for undo/redo functionality.
PyQt5 compatible version.
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json
from datetime import datetime


@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    message: str
    data: Any = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class Command(ABC):
    """Abstract base class for all commands"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.timestamp = datetime.now().isoformat()
        self.executed = False
        self.result: Optional[CommandResult] = None
    
    @abstractmethod
    def execute(self) -> CommandResult:
        """Execute the command"""
        pass
    
    @abstractmethod
    def undo(self) -> CommandResult:
        """Undo the command"""
        pass
    
    def redo(self) -> CommandResult:
        """Redo the command"""
        return self.execute()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary for serialization"""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.__class__.__name__,
            'timestamp': self.timestamp,
            'executed': self.executed
        }


class AddWidgetCommand(Command):
    """Command to add widget to canvas"""
    
    def __init__(self, widget_type: str, properties: Dict[str, Any], core):
        super().__init__("Add Widget", f"Add {widget_type} to canvas")
        self.widget_type = widget_type
        self.properties = properties
        self.core = core
        self.widget_data = None
    
    def execute(self) -> CommandResult:
        try:
            self.widget_data = self.core.add_widget(self.widget_type, self.properties)
            self.executed = True
            
            self.result = CommandResult(
                success=True,
                message=f"Added {self.widget_type} to canvas",
                data={'widget_data': self.widget_data}
            )
            
        except Exception as e:
            self.result = CommandResult(
                success=False,
                message=f"Failed to add widget: {e}",
                error=str(e)
            )
        
        return self.result
    
    def undo(self) -> CommandResult:
        if not self.executed or not self.widget_data:
            return CommandResult(
                success=False,
                message="Command not executed yet or no widget data"
            )
        
        try:
            widget_id = self.widget_data.get('id')
            success = self.core.remove_widget(widget_id)
            
            if success:
                return CommandResult(
                    success=True,
                    message=f"Removed {self.widget_type} from canvas",
                    data={'widget_id': widget_id}
                )
            else:
                return CommandResult(
                    success=False,
                    message=f"Failed to remove widget {widget_id}"
                )
                
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to undo: {e}",
                error=str(e)
            )


class GenerateCodeCommand(Command):
    """Command to generate code"""
    
    def __init__(self, core):
        super().__init__("Generate Code", "Generate GUI code from design")
        self.core = core
        self.generated_code = None
    
    def execute(self) -> CommandResult:
        try:
            self.generated_code = self.core.generate_gui_code()
            self.executed = True
            
            return CommandResult(
                success=True,
                message="Code generated successfully",
                data={'code': self.generated_code}
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to generate code: {e}",
                error=str(e)
            )
    
    def undo(self) -> CommandResult:
        return CommandResult(
            success=True,
            message="Code generation undone (code cleared from memory)",
            data={'code': None}
        )


class AnalyzeCodeCommand(Command):
    """Command to analyze code"""
    
    def __init__(self, code: str, core):
        super().__init__("Analyze Code", "Analyze code for issues and metrics")
        self.code = code
        self.core = core
        self.analysis_result = None
    
    def execute(self) -> CommandResult:
        try:
            self.analysis_result = self.core.analyze_code(self.code)
            self.executed = True
            
            return CommandResult(
                success=True,
                message="Code analysis completed",
                data={'analysis': self.analysis_result}
            )
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to analyze code: {e}",
                error=str(e)
            )
    
    def undo(self) -> CommandResult:
        return CommandResult(
            success=True,
            message="Analysis undone",
            data={'analysis': None}
        )


class CommandDispatcher:
    """Manages command execution, undo, and redo"""
    
    def __init__(self, max_history: int = 100):
        self.command_history: List[Command] = []
        self.undo_stack: List[Command] = []
        self.max_history = max_history
        self.registered_commands: Dict[str, Callable] = {}
        
        # Register default commands
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register default command types"""
        self.register_command_type("add_widget", AddWidgetCommand)
        self.register_command_type("generate_code", GenerateCodeCommand)
        self.register_command_type("analyze_code", AnalyzeCodeCommand)
    
    def register_command_type(self, command_type: str, command_class):
        """Register a new command type"""
        self.registered_commands[command_type] = command_class
    
    def execute_command(self, command: Command) -> CommandResult:
        """
        Execute a command and add to history.
        
        Args:
            command: Command to execute
            
        Returns:
            CommandResult: Execution result
        """
        result = command.execute()
        
        if result.success:
            # Add to history
            self.command_history.append(command)
            
            # Clear redo stack
            self.undo_stack.clear()
            
            # Limit history size
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)
            
            print(f"✓ Command executed: {command.name}")
        else:
            print(f"✗ Command failed: {command.name} - {result.message}")
        
        return result
    
    def create_and_execute(self, command_type: str, **kwargs) -> CommandResult:
        """
        Create and execute a command by type.
        
        Args:
            command_type: Type of command to create
            **kwargs: Arguments for command constructor
            
        Returns:
            CommandResult: Execution result
        """
        if command_type not in self.registered_commands:
            return CommandResult(
                success=False,
                message=f"Unknown command type: {command_type}"
            )
        
        command_class = self.registered_commands[command_type]
        command = command_class(**kwargs)
        
        return self.execute_command(command)
    
    def undo(self) -> CommandResult:
        """
        Undo last command.
        
        Returns:
            CommandResult: Undo result
        """
        if not self.command_history:
            return CommandResult(
                success=False,
                message="No commands to undo"
            )
        
        command = self.command_history.pop()
        result = command.undo()
        
        if result.success:
            self.undo_stack.append(command)
            print(f"✓ Command undone: {command.name}")
        else:
            print(f"✗ Undo failed: {command.name} - {result.message}")
        
        return result
    
    def redo(self) -> CommandResult:
        """
        Redo last undone command.
        
        Returns:
            CommandResult: Redo result
        """
        if not self.undo_stack:
            return CommandResult(
                success=False,
                message="No commands to redo"
            )
        
        command = self.undo_stack.pop()
        result = command.redo()
        
        if result.success:
            self.command_history.append(command)
            print(f"✓ Command redone: {command.name}")
        else:
            print(f"✗ Redo failed: {command.name} - {result.message}")
        
        return result
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get command history as list of dictionaries"""
        return [cmd.to_dict() for cmd in self.command_history]
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
        self.undo_stack.clear()
        print("✓ Command history cleared")
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return len(self.command_history) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible"""
        return len(self.undo_stack) > 0
    
    def get_last_command(self) -> Optional[Command]:
        """Get last executed command"""
        if self.command_history:
            return self.command_history[-1]
        return None
    
    def save_history(self, filepath: str) -> bool:
        """
        Save command history to file.
        
        Args:
            filepath: Path to save file
            
        Returns:
            bool: Success status
        """
        try:
            history_data = {
                'commands': self.get_history(),
                'total_commands': len(self.command_history),
                'saved_at': datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2)
            
            print(f"✓ Command history saved to {filepath}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to save history: {e}")
            return False
    
    def load_history(self, filepath: str) -> bool:
        """
        Load command history from file.
        
        Args:
            filepath: Path to load file from
            
        Returns:
            bool: Success status
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            print(f"✓ Loaded {history_data.get('total_commands', 0)} commands from history")
            # Note: This only loads metadata, not actual command objects
            return True
            
        except Exception as e:
            print(f"✗ Failed to load history: {e}")
            return False


# Test the command dispatcher
if __name__ == "__main__":
    dispatcher = CommandDispatcher()
    
    # Test basic functionality
    print(f"Can undo: {dispatcher.can_undo()}")
    print(f"Can redo: {dispatcher.can_redo()}")
    
    # Test command registration
    print(f"Registered commands: {list(dispatcher.registered_commands.keys())}")