"""
Refactor Plugin - provides code refactoring tools.
Example plugin demonstrating plugin system capabilities.
"""

from core.plugin_manager import BasePlugin, PluginInfo
from typing import List, Dict, Any
import re


class RefactorPlugin(BasePlugin):
    """Plugin providing code refactoring tools"""
    
    def __init__(self, core):
        super().__init__(core)
        self.info = PluginInfo(
            name="Refactor Tools",
            version="1.2.0",
            author="GUI Constructor Team",
            description="Advanced code refactoring and optimization tools"
        )
        self.refactoring_patterns = self._load_refactoring_patterns()
    
    def _load_refactoring_patterns(self) -> Dict[str, Any]:
        """Load refactoring patterns and rules"""
        return {
            'optimize_imports': {
                'description': 'Optimize and organize import statements',
                'patterns': [
                    (r'^import (\w+)$', r'import \1'),
                    (r'^from (\w+) import \*$', r'from \1 import *  # TODO: Specify imports')
                ]
            },
            'rename_variables': {
                'description': 'Rename variables to follow naming conventions',
                'patterns': [
                    (r'(\w+) = ', r'\1 = '),  # Placeholder
                ]
            },
            'extract_method': {
                'description': 'Extract code block to new method',
                'template': '''def {method_name}({params}):
    {code}
'''
            },
            'inline_variable': {
                'description': 'Inline temporary variables',
                'patterns': [
                    (r'temp_(\w+) = (.+)\n(.+?)temp_\1', r'\3\2')
                ]
            }
        }
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        print(f"Initializing {self.info.name} v{self.info.version}")
        
        # Register with core if available
        if hasattr(self.core, 'register_refactoring_tool'):
            self.core.register_refactoring_tool(self)
        
        return True
    
    def get_actions(self) -> List[Dict[str, Any]]:
        """Get plugin actions for menu/toolbar"""
        return [
            {
                'name': '🔧 Optimize Imports',
                'callback': self.optimize_imports,
                'tooltip': 'Organize and optimize import statements',
                'icon': 'import_icon',
                'category': 'Refactoring'
            },
            {
                'name': '📝 Rename Variables',
                'callback': self.rename_variables,
                'tooltip': 'Rename variables to follow conventions',
                'icon': 'rename_icon',
                'category': 'Refactoring'
            },
            {
                'name': '🧩 Extract Method',
                'callback': self.extract_method,
                'tooltip': 'Extract selected code to new method',
                'icon': 'extract_icon',
                'category': 'Refactoring'
            },
            {
                'name': '⚡ Inline Variable',
                'callback': self.inline_variable,
                'tooltip': 'Inline temporary variables',
                'icon': 'inline_icon',
                'category': 'Refactoring'
            },
            {
                'name': '📊 Code Metrics',
                'callback': self.show_code_metrics,
                'tooltip': 'Show code complexity and metrics',
                'icon': 'metrics_icon',
                'category': 'Analysis'
            }
        ]
    
    def optimize_imports(self, code: str) -> str:
        """Optimize import statements in code"""
        lines = code.split('\n')
        import_lines = []
        other_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                import_lines.append(line)
            else:
                other_lines.append(line)
        
        # Sort imports
        import_lines.sort(key=lambda x: (
            0 if x.startswith('from __future__') else
            1 if x.startswith('import ') else
            2 if x.startswith('from ') else 3
        ))
        
        # Combine with blank line between imports and code
        optimized = '\n'.join(import_lines)
        if import_lines and other_lines:
            optimized += '\n\n'
        optimized += '\n'.join(other_lines)
        
        return optimized
    
    def rename_variables(self, code: str, old_name: str, new_name: str) -> str:
        """Rename variables in code"""
        # Simple rename - in real implementation would use AST
        pattern = r'\b' + re.escape(old_name) + r'\b'
        return re.sub(pattern, new_name, code)
    
    def extract_method(self, code_block: str, method_name: str, params: str = "") -> Dict[str, Any]:
        """Extract code block to new method"""
        indentation = '    '
        
        # Create method definition
        method_def = f"def {method_name}({params}):\n"
        method_body = '\n'.join([indentation + line for line in code_block.split('\n')])
        
        return {
            'method_code': method_def + method_body,
            'call_code': f"{method_name}({params})"
        }
    
    def inline_variable(self, code: str, var_name: str) -> str:
        """Inline a variable (simplified)"""
        # This is a simplified version
        lines = code.split('\n')
        result = []
        var_value = None
        
        for line in lines:
            # Look for variable assignment
            match = re.match(rf'^\s*{re.escape(var_name)}\s*=\s*(.+)$', line)
            if match:
                var_value = match.group(1)
            else:
                # Replace variable usage with its value
                if var_value:
                    line = re.sub(rf'\b{re.escape(var_name)}\b', var_value, line)
                result.append(line)
        
        return '\n'.join(result)
    
    def show_code_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate code metrics"""
        lines = code.split('\n')
        
        # Basic metrics
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        comment_lines = len([l for l in lines if l.strip().startswith('#')])
        blank_lines = total_lines - code_lines - comment_lines
        
        # Estimate complexity (simplified)
        complexity_points = 0
        for line in lines:
            if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'def ', 'class ']):
                complexity_points += 1
            if ' and ' in line or ' or ' in line:
                complexity_points += 0.5
        
        complexity_level = "Low"
        if complexity_points > 20:
            complexity_level = "High"
        elif complexity_points > 10:
            complexity_level = "Medium"
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines,
            'complexity_score': round(complexity_points, 1),
            'complexity_level': complexity_level,
            'comment_ratio': round(comment_lines / max(code_lines, 1) * 100, 1)
        }
    
    def cleanup(self):
        """Cleanup plugin resources"""
        print(f"Cleaning up {self.info.name}")
    
    def get_refactoring_options(self) -> Dict[str, Any]:
        """Get available refactoring options"""
        return self.refactoring_patterns