"""
Central application core - main controller for GUI Constructor platform.
Manages all modules, plugins, and application state.
PyQt5 compatible version.
"""

import os
import sys
import importlib
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ProjectState:
    """Current project state data class"""
    path: Optional[str] = None
    name: Optional[str] = None
    widgets: List[Dict] = field(default_factory=list)
    code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    modified: bool = False
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_modified: str = field(default_factory=lambda: datetime.now().isoformat())


class AppCore:
    """Central brain of the application. Manages state and logic."""
    
    def __init__(self):
        self.project = ProjectState()
        self.settings = self._load_settings()
        self.modules = {}
        self.commands = []
        
        print("✓ AppCore initialized")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load application settings from file or create defaults"""
        settings_file = "gui_constructor_settings.json"
        default_settings = {
            "theme": "light",
            "autosave": True,
            "autosave_interval": 300,  # 5 minutes
            "ai_enabled": False,
            "code_style": "pep8",
            "recent_projects": [],
            "window_width": 1400,
            "window_height": 800,
            "plugins_enabled": True
        }
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                # Merge with defaults
                default_settings.update(loaded_settings)
                print(f"✓ Settings loaded from {settings_file}")
            except Exception as e:
                print(f"✗ Error loading settings: {e}")
        
        return default_settings
    
    def save_settings(self):
        """Save current settings to file"""
        settings_file = "gui_constructor_settings.json"
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"✓ Settings saved to {settings_file}")
            return True
        except Exception as e:
            print(f"✗ Error saving settings: {e}")
            return False
    
    def load_project(self, project_path: str) -> bool:
        """
        Load and analyze project directory.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            bool: Success status
        """
        if not os.path.exists(project_path):
            print(f"✗ Project path does not exist: {project_path}")
            return False
        
        try:
            self.project.path = project_path
            self.project.name = os.path.basename(project_path)
            self.project.modified = False
            self.project.last_modified = datetime.now().isoformat()
            
            # Analyze project structure
            self._analyze_project_structure(project_path)
            
            # Add to recent projects
            self._add_to_recent_projects(project_path)
            
            print(f"✓ Project loaded: {self.project.name}")
            return True
            
        except Exception as e:
            print(f"✗ Error loading project: {e}")
            return False
    
    def _analyze_project_structure(self, path: str):
        """Analyze project directory structure"""
        try:
            analysis = {
                'files': [],
                'directories': [],
                'python_files': 0,
                'total_size': 0,
                'file_types': {}
            }
            
            for root, dirs, files in os.walk(path):
                # Skip virtual environments and hidden directories
                skip_dirs = ['venv', '.venv', '.git', '__pycache__', '.idea', '.vscode']
                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]
                
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    analysis['directories'].append(dir_path)
                
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    
                    # Get file info
                    try:
                        file_size = os.path.getsize(file_path)
                        file_ext = os.path.splitext(file_name)[1].lower()
                        
                        file_info = {
                            'name': file_name,
                            'path': file_path,
                            'size': file_size,
                            'extension': file_ext,
                            'relative_path': os.path.relpath(file_path, path)
                        }
                        
                        analysis['files'].append(file_info)
                        analysis['total_size'] += file_size
                        
                        # Count file types
                        analysis['file_types'][file_ext] = analysis['file_types'].get(file_ext, 0) + 1
                        
                        # Count Python files
                        if file_ext == '.py':
                            analysis['python_files'] += 1
                            # Try to get line count
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    file_info['lines'] = len(lines)
                            except:
                                file_info['lines'] = 0
                        
                    except OSError:
                        continue
            
            self.project.metadata['analysis'] = analysis
            print(f"✓ Project analyzed: {len(analysis['files'])} files, {analysis['python_files']} Python files")
            
        except Exception as e:
            print(f"✗ Error analyzing project: {e}")
            self.project.metadata['analysis'] = {'error': str(e)}
    
    def _add_to_recent_projects(self, project_path: str):
        """Add project to recent projects list"""
        recent = self.settings.get('recent_projects', [])
        
        # Remove if already in list
        if project_path in recent:
            recent.remove(project_path)
        
        # Add to beginning
        recent.insert(0, project_path)
        
        # Keep only last 10
        recent = recent[:10]
        
        self.settings['recent_projects'] = recent
        self.save_settings()
    
    def save_project(self, file_path: Optional[str] = None) -> bool:
        """
        Save current project.
        
        Args:
            file_path: Optional custom save path
            
        Returns:
            bool: Success status
        """
        if not file_path and not self.project.path:
            print("✗ No project path specified")
            return False
        
        save_path = file_path or self.project.path
        
        try:
            # Create project data
            project_data = {
                'name': self.project.name,
                'path': self.project.path,
                'widgets': self.project.widgets,
                'metadata': self.project.metadata,
                'created': self.project.created,
                'last_modified': datetime.now().isoformat()
            }
            
            # Save to file
            project_file = os.path.join(save_path, 'gui_constructor_project.json')
            with open(project_file, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            self.project.modified = False
            self.project.last_modified = datetime.now().isoformat()
            
            print(f"✓ Project saved: {project_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving project: {e}")
            return False
    
    def generate_gui_code(self) -> str:
        """
        Generate Python GUI code based on current design.
        
        Returns:
            str: Generated Python code
        """
        if not self.project.widgets:
            return "# No widgets to generate code for\n# Add widgets using the designer tools."
        
        code_lines = [
            "# Generated by GUI Constructor",
            "# Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "",
            "import sys",
            "from PyQt5.QtWidgets import (",
            "    QApplication, QMainWindow, QWidget,",
            "    QVBoxLayout, QHBoxLayout, QPushButton,",
            "    QLabel, QTextEdit, QLineEdit, QCheckBox,",
            "    QRadioButton, QComboBox, QListWidget, QTreeWidget,",
            "    QTableWidget, QGroupBox, QTabWidget, QToolBox,",
            "    QScrollArea, QFrame, QSlider, QProgressBar",
            ")",
            "from PyQt5.QtCore import Qt, QSize",
            "from PyQt5.QtGui import QFont, QIcon",
            "",
            "",
            f"class {self.project.name.replace(' ', '_')}Window(QMainWindow):",
            "    \"\"\"Generated GUI Window\"\"\"",
            "",
            "    def __init__(self):",
            "        super().__init__()",
            f"        self.setWindowTitle('{self.project.name}')",
            "        self.setGeometry(100, 100, 800, 600)",
            "        self._setup_ui()",
            "",
            "    def _setup_ui(self):",
            "        \"\"\"Setup user interface\"\"\"",
            "        central_widget = QWidget()",
            "        self.setCentralWidget(central_widget)",
            "        main_layout = QVBoxLayout(central_widget)",
            ""
        ]
        
        # Add widget creation code
        for i, widget in enumerate(self.project.widgets):
            widget_type = widget.get('type', 'QPushButton')
            widget_name = widget.get('name', f'widget_{i+1}')
            widget_text = widget.get('text', widget_name)
            
            if widget_type == 'QPushButton':
                code_lines.append(f"        {widget_name} = QPushButton('{widget_text}')")
                code_lines.append(f"        main_layout.addWidget({widget_name})")
            elif widget_type == 'Label':
                code_lines.append(f"        {widget_name} = QLabel('{widget_text}')")
                code_lines.append(f"        main_layout.addWidget({widget_name})")
            elif widget_type == 'Text Edit':
                code_lines.append(f"        {widget_name} = QTextEdit()")
                code_lines.append(f"        {widget_name}.setPlaceholderText('{widget_text}')")
                code_lines.append(f"        main_layout.addWidget({widget_name})")
            elif widget_type == 'Line Edit':
                code_lines.append(f"        {widget_name} = QLineEdit()")
                code_lines.append(f"        {widget_name}.setPlaceholderText('{widget_text}')")
                code_lines.append(f"        main_layout.addWidget({widget_name})")
            elif widget_type == 'Check Box':
                code_lines.append(f"        {widget_name} = QCheckBox('{widget_text}')")
                code_lines.append(f"        main_layout.addWidget({widget_name})")
            
            # Add connections for buttons
            if widget_type == 'QPushButton':
                code_lines.append(f"        {widget_name}.clicked.connect(self.on_{widget_name}_clicked)")
        
        # Add event methods
        for i, widget in enumerate(self.project.widgets):
            widget_type = widget.get('type', 'QPushButton')
            widget_name = widget.get('name', f'widget_{i+1}')
            
            if widget_type == 'QPushButton':
                code_lines.append("")
                code_lines.append(f"    def on_{widget_name}_clicked(self):")
                code_lines.append(f"        \"\"\"Handle {widget_name} click\"\"\"")
                code_lines.append(f"        print('{widget_name} clicked')")
        
        code_lines.extend([
            "",
            "",
            "def main():",
            "    \"\"\"Main application entry point\"\"\"",
            "    app = QApplication(sys.argv)",
            f"    window = {self.project.name.replace(' ', '_')}Window()",
            "    window.show()",
            "    sys.exit(app.exec_())",
            "",
            "",
            "if __name__ == '__main__':",
            "    main()",
            ""
        ])
        
        self.project.code = '\n'.join(code_lines)
        print(f"✓ Generated GUI code with {len(self.project.widgets)} widgets")
        return self.project.code
    
    def add_widget(self, widget_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add widget to current project.
        
        Args:
            widget_type: Type of widget (button, label, etc.)
            properties: Widget properties
            
        Returns:
            Dict: Created widget data
        """
        widget_id = f"widget_{len(self.project.widgets) + 1}"
        widget_data = {
            'id': widget_id,
            'type': widget_type,
            'name': properties.get('name', widget_id),
            'text': properties.get('text', widget_type),
            'properties': properties,
            'position': properties.get('position', (10, 10)),
            'size': properties.get('size', (100, 30)),
            'created': datetime.now().isoformat()
        }
        
        self.project.widgets.append(widget_data)
        self.project.modified = True
        self.project.last_modified = datetime.now().isoformat()
        
        print(f"✓ Added widget: {widget_type} ({widget_id})")
        return widget_data
    
    def remove_widget(self, widget_id: str) -> bool:
        """
        Remove widget from project.
        
        Args:
            widget_id: ID of widget to remove
            
        Returns:
            bool: Success status
        """
        for i, widget in enumerate(self.project.widgets):
            if widget['id'] == widget_id:
                del self.project.widgets[i]
                self.project.modified = True
                self.project.last_modified = datetime.now().isoformat()
                print(f"✓ Removed widget: {widget_id}")
                return True
        
        print(f"✗ Widget not found: {widget_id}")
        return False
    
    def update_widget(self, widget_id: str, properties: Dict[str, Any]) -> bool:
        """
        Update widget properties.
        
        Args:
            widget_id: ID of widget to update
            properties: New properties
            
        Returns:
            bool: Success status
        """
        for widget in self.project.widgets:
            if widget['id'] == widget_id:
                widget['properties'].update(properties)
                widget['last_modified'] = datetime.now().isoformat()
                self.project.modified = True
                self.project.last_modified = datetime.now().isoformat()
                print(f"✓ Updated widget: {widget_id}")
                return True
        
        print(f"✗ Widget not found: {widget_id}")
        return False
    
    def refactor_code(self, code: str, refactor_type: str = 'optimize') -> str:
        """
        Refactor code based on type.
        
        Args:
            code: Source code to refactor
            refactor_type: Type of refactoring
            
        Returns:
            str: Refactored code
        """
        try:
            if refactor_type == 'optimize':
                # Simple optimization: remove duplicate empty lines
                lines = code.split('\n')
                optimized_lines = []
                prev_empty = False
                
                for line in lines:
                    is_empty = line.strip() == ''
                    if not (prev_empty and is_empty):
                        optimized_lines.append(line)
                    prev_empty = is_empty
                
                optimized = '\n'.join(optimized_lines)
                print("✓ Code optimized")
                return optimized
                
            elif refactor_type == 'format':
                # Simple formatting: ensure consistent indentation
                lines = code.split('\n')
                formatted_lines = []
                indent_level = 0
                
                for line in lines:
                    stripped = line.strip()
                    if stripped.endswith(':'):
                        formatted_lines.append('    ' * indent_level + line.strip())
                        indent_level += 1
                    elif stripped in ['pass', 'return', 'break', 'continue']:
                        indent_level = max(0, indent_level - 1)
                        formatted_lines.append('    ' * indent_level + line.strip())
                    else:
                        formatted_lines.append('    ' * indent_level + line.strip())
                
                formatted = '\n'.join(formatted_lines)
                print("✓ Code formatted")
                return formatted
                
            else:
                print(f"✗ Unknown refactor type: {refactor_type}")
                return code
                
        except Exception as e:
            print(f"✗ Error refactoring code: {e}")
            return code
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze code for issues and metrics.
        
        Args:
            code: Source code to analyze
            
        Returns:
            Dict: Analysis results
        """
        try:
            lines = code.split('\n')
            
            metrics = {
                'total_lines': len(lines),
                'code_lines': 0,
                'comment_lines': 0,
                'blank_lines': 0,
                'imports': 0,
                'functions': 0,
                'classes': 0,
                'average_line_length': 0,
                'issues': []
            }
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Count line types
                if stripped == '':
                    metrics['blank_lines'] += 1
                elif stripped.startswith('#'):
                    metrics['comment_lines'] += 1
                else:
                    metrics['code_lines'] += 1
                
                # Count imports
                if stripped.startswith(('import ', 'from ')):
                    metrics['imports'] += 1
                
                # Count functions and classes
                if stripped.startswith('def '):
                    metrics['functions'] += 1
                elif stripped.startswith('class '):
                    metrics['classes'] += 1
                
                # Calculate average line length
                metrics['average_line_length'] += len(line)
                
                # Check for issues
                if len(line) > 100:
                    metrics['issues'].append({
                        'line': i,
                        'type': 'style',
                        'message': 'Line too long (> 100 characters)',
                        'severity': 'low'
                    })
                
                if 'print(' in line and not stripped.startswith('#'):
                    metrics['issues'].append({
                        'line': i,
                        'type': 'style',
                        'message': 'Consider using logging instead of print',
                        'severity': 'low'
                    })
            
            # Calculate averages
            if metrics['code_lines'] > 0:
                metrics['average_line_length'] = metrics['average_line_length'] / len(lines)
            
            # Determine complexity level
            complexity_score = metrics['functions'] * 2 + metrics['classes'] * 3
            if complexity_score > 20:
                complexity = 'high'
            elif complexity_score > 10:
                complexity = 'medium'
            else:
                complexity = 'low'
            
            metrics['complexity'] = complexity
            metrics['complexity_score'] = complexity_score
            
            print(f"✓ Code analyzed: {metrics['total_lines']} lines, {len(metrics['issues'])} issues found")
            return metrics
            
        except Exception as e:
            print(f"✗ Error analyzing code: {e}")
            return {'error': str(e), 'total_lines': 0, 'issues': []}
    
    def load_module(self, module_name: str) -> bool:
        """
        Dynamically load a module.
        
        Args:
            module_name: Name of module to load
            
        Returns:
            bool: Success status
        """
        try:
            module = importlib.import_module(module_name)
            self.modules[module_name] = module
            print(f"✓ Module loaded: {module_name}")
            return True
        except ImportError as e:
            print(f"✗ Failed to load module {module_name}: {e}")
            return False
    
    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """
        Execute a command.
        
        Args:
            command_name: Name of command to execute
            *args: Command arguments
            **kwargs: Command keyword arguments
            
        Returns:
            Any: Command result
        """
        try:
            # Simple command execution
            if command_name == 'add_widget':
                return self.add_widget(*args, **kwargs)
            elif command_name == 'generate_code':
                return self.generate_gui_code()
            elif command_name == 'analyze_code':
                return self.analyze_code(*args, **kwargs)
            elif command_name == 'refactor_code':
                return self.refactor_code(*args, **kwargs)
            else:
                print(f"✗ Unknown command: {command_name}")
                return None
                
        except Exception as e:
            print(f"✗ Error executing command {command_name}: {e}")
            return None
    
    def get_project_summary(self) -> Dict[str, Any]:
        """Get summary of current project"""
        return {
            'name': self.project.name,
            'path': self.project.path,
            'widget_count': len(self.project.widgets),
            'modified': self.project.modified,
            'created': self.project.created,
            'last_modified': self.project.last_modified,
            'has_code': self.project.code is not None
        }
    
    def clear_project(self):
        """Clear current project"""
        self.project = ProjectState()
        print("✓ Project cleared")


if __name__ == "__main__":
    # Test the core
    core = AppCore()
    print("AppCore test completed")