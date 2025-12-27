"""
Analysis Plugin - provides code analysis and metrics.
Example plugin for project analysis features.
"""

from core.plugin_manager import BasePlugin, PluginInfo
from typing import List, Dict, Any
import ast
import os


class AnalysisPlugin(BasePlugin):
    """Plugin providing code analysis tools"""
    
    def __init__(self, core):
        super().__init__(core)
        self.info = PluginInfo(
            name="Code Analysis",
            version="1.1.0",
            author="GUI Constructor Team",
            description="Static code analysis and quality metrics"
        )
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        print(f"Initializing {self.info.name}")
        return True
    
    def get_actions(self) -> List[Dict[str, Any]]:
        """Get plugin actions"""
        return [
            {
                'name': '📈 Analyze Project',
                'callback': self.analyze_project_structure,
                'tooltip': 'Analyze project structure and dependencies',
                'category': 'Analysis'
            },
            {
                'name': '⚠️ Find Issues',
                'callback': self.find_code_issues,
                'tooltip': 'Find potential issues and bugs',
                'category': 'Analysis'
            },
            {
                'name': '📊 Complexity Report',
                'callback': self.generate_complexity_report,
                'tooltip': 'Generate code complexity report',
                'category': 'Analysis'
            },
            {
                'name': '🔗 Dependency Graph',
                'callback': self.generate_dependency_graph,
                'tooltip': 'Generate module dependency graph',
                'category': 'Analysis'
            }
        ]
    
    def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze project directory structure"""
        if not os.path.exists(project_path):
            return {'error': 'Project path does not exist'}
        
        results = {
            'path': project_path,
            'files': [],
            'directories': [],
            'file_types': {},
            'total_size': 0,
            'python_files': 0,
            'total_lines': 0
        }
        
        for root, dirs, files in os.walk(project_path):
            # Skip virtual environments and hidden directories
            if any(skip in root for skip in ['venv', '.git', '__pycache__', '.idea']):
                continue
            
            for dir_name in dirs:
                if not dir_name.startswith('.'):
                    results['directories'].append(os.path.join(root, dir_name))
            
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_ext = os.path.splitext(file_name)[1].lower()
                
                # Update file type statistics
                results['file_types'][file_ext] = results['file_types'].get(file_ext, 0) + 1
                
                # Get file size
                try:
                    file_size = os.path.getsize(file_path)
                    results['total_size'] += file_size
                    
                    file_info = {
                        'name': file_name,
                        'path': file_path,
                        'size': file_size,
                        'extension': file_ext
                    }
                    
                    # Count Python files and lines
                    if file_ext == '.py':
                        results['python_files'] += 1
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                file_info['lines'] = len(lines)
                                results['total_lines'] += len(lines)
                        except:
                            file_info['lines'] = 0
                    
                    results['files'].append(file_info)
                    
                except OSError:
                    continue
        
        # Sort files by size
        results['files'].sort(key=lambda x: x['size'], reverse=True)
        
        return results
    
    def find_code_issues(self, code: str) -> List[Dict[str, Any]]:
        """Find potential issues in code"""
        issues = []
        
        try:
            tree = ast.parse(code)
            
            # Check for issues using AST
            for node in ast.walk(tree):
                # Check for bare except
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append({
                        'type': 'warning',
                        'message': 'Bare except clause',
                        'line': node.lineno if hasattr(node, 'lineno') else 0,
                        'severity': 'medium'
                    })
                
                # Check for too many branches (simplified)
                if isinstance(node, ast.If):
                    # Count nested ifs
                    nested_level = self._count_nested_level(node)
                    if nested_level > 3:
                        issues.append({
                            'type': 'complexity',
                            'message': f'Deeply nested if statements ({nested_level} levels)',
                            'line': node.lineno if hasattr(node, 'lineno') else 0,
                            'severity': 'low'
                        })
        
        except SyntaxError as e:
            issues.append({
                'type': 'error',
                'message': f'Syntax error: {e.msg}',
                'line': e.lineno,
                'severity': 'high'
            })
        
        # Simple pattern checks
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for print statements (might want to use logging)
            if line_stripped.startswith('print(') and not line_stripped.startswith('# print('):
                issues.append({
                    'type': 'style',
                    'message': 'Consider using logging instead of print',
                    'line': i,
                    'severity': 'low'
                })
            
            # Check for long lines
            if len(line) > 100:
                issues.append({
                    'type': 'style',
                    'message': f'Line too long ({len(line)} characters)',
                    'line': i,
                    'severity': 'low'
                })
        
        return issues
    
    def _count_nested_level(self, node, current_level=0):
        """Count nested level of if statements"""
        if isinstance(node, ast.If):
            current_level += 1
            max_level = current_level
            
            # Check else/elif branches
            for child in ast.iter_child_nodes(node):
                child_level = self._count_nested_level(child, current_level)
                max_level = max(max_level, child_level)
            
            return max_level
        
        # Check children
        max_level = current_level
        for child in ast.iter_child_nodes(node):
            child_level = self._count_nested_level(child, current_level)
            max_level = max(max_level, child_level)
        
        return max_level
    
    def generate_complexity_report(self, code: str) -> Dict[str, Any]:
        """Generate code complexity report"""
        try:
            tree = ast.parse(code)
            
            metrics = {
                'functions': 0,
                'classes': 0,
                'imports': 0,
                'if_statements': 0,
                'loops': 0,
                'try_blocks': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    metrics['classes'] += 1
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    metrics['imports'] += 1
                elif isinstance(node, ast.If):
                    metrics['if_statements'] += 1
                elif isinstance(node, (ast.For, ast.While)):
                    metrics['loops'] += 1
                elif isinstance(node, ast.Try):
                    metrics['try_blocks'] += 1
            
            # Calculate complexity score
            complexity_score = (
                metrics['functions'] * 2 +
                metrics['classes'] * 3 +
                metrics['if_statements'] * 1 +
                metrics['loops'] * 2 +
                metrics['try_blocks'] * 1
            )
            
            # Determine complexity level
            if complexity_score > 50:
                complexity_level = "Very High"
            elif complexity_score > 30:
                complexity_level = "High"
            elif complexity_score > 15:
                complexity_level = "Medium"
            else:
                complexity_level = "Low"
            
            return {
                'metrics': metrics,
                'complexity_score': complexity_score,
                'complexity_level': complexity_level,
                'recommendations': self._generate_recommendations(metrics)
            }
            
        except SyntaxError as e:
            return {
                'error': f'Syntax error: {e.msg}',
                'line': e.lineno
            }
    
    def _generate_recommendations(self, metrics: Dict[str, int]) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []
        
        if metrics['functions'] > 10:
            recommendations.append("Consider splitting large module into smaller ones")
        
        if metrics['if_statements'] > 15:
            recommendations.append("High number of if statements - consider polymorphism")
        
        if metrics['try_blocks'] > 5:
            recommendations.append("Multiple try blocks - consider error handling strategy")
        
        if not recommendations:
            recommendations.append("Code structure looks good")
        
        return recommendations
    
    def generate_dependency_graph(self, project_path: str) -> Dict[str, Any]:
        """Generate module dependency graph (simplified)"""
        # This is a simplified version
        dependencies = {}
        
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    module_name = os.path.splitext(file)[0]
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Simple import detection
                        imports = []
                        lines = content.split('\n')
                        for line in lines:
                            line_stripped = line.strip()
                            if line_stripped.startswith('import '):
                                imports.extend([i.strip() for i in line_stripped[7:].split(',')])
                            elif line_stripped.startswith('from '):
                                # Extract module from "from module import ..."
                                parts = line_stripped.split(' ')
                                if len(parts) > 1:
                                    imports.append(parts[1])
                        
                        dependencies[module_name] = imports
                        
                    except:
                        continue
        
        return {
            'nodes': list(dependencies.keys()),
            'edges': [(source, target) for source, targets in dependencies.items() 
                     for target in targets if target in dependencies],
            'dependency_count': sum(len(v) for v in dependencies.values())
        }
    
    def cleanup(self):
        """Cleanup plugin resources"""
        print(f"Cleaning up {self.info.name}")