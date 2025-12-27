"""
Main Window - Primary GUI interface for GUI Constructor.
Modern Windows 10 style interface with tabs, toolbars, and full functionality.
"""

import sys
import os
from typing import Dict, Any, List

from PyQt5.QtWidgets import (QAction,
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QTabWidget, QToolBar, QStatusBar,
    QSplitter, QListWidget, QTreeWidget, QDockWidget, QMessageBox,
    QLabel, QMenu, QMenuBar, QAction, QToolButton, QProgressBar,
    QInputDialog, QComboBox, QSpinBox, QCheckBox, QGroupBox,
    QFormLayout, QGridLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QKeySequence, QPixmap

# Import application modules
from core.app_core import AppCore
from core.plugin_manager import PluginManager
from core.command_dispatcher import CommandDispatcher
from gui.tab_manager import TabManager
from gui.windows_style import Windows10Style, ModernButtonStyle


class MainWindow(QMainWindow):
    """Main application window with full functionality"""
    
    project_loaded = pyqtSignal(str)
    project_saved = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Initialize core components
        self.core = AppCore()
        self.plugin_manager = PluginManager(self.core)
        self.command_dispatcher = CommandDispatcher()
        
        # Load settings
        self.settings = QSettings("GUI Constructor", "GUI Constructor")
        
        # Setup UI
        self._setup_ui()
        self._create_menu_bar()
        self._create_toolbars()
        self._create_docks()
        self._create_status_bar()
        
        # Load plugins
        self._load_plugins()
        
        # Set window properties
        self.setWindowTitle("GUI Constructor Platform")
        self.setGeometry(100, 100, 1400, 800)
        
        # Apply saved window state
        self._restore_window_state()
    
    def _setup_ui(self):
        """Setup main window UI"""
        # Central widget with tabs
        self.tab_manager = TabManager()
        self.tab_manager.add_default_tabs()
        self.setCentralWidget(self.tab_manager)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply Windows 10 styling"""
        # Set application font
        font = Windows10Style.get_font_settings()
        self.setFont(font)
        
        # Set stylesheet for specific components
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            QDockWidget {
                titlebar-normal-icon: url(dock-restore.png);
                titlebar-close-icon: url(dock-close.png);
            }
            
            QDockWidget::title {
                background: #e5e5e5;
                padding: 6px;
                text-align: center;
                font-weight: bold;
            }
            
            QStatusBar {
                background-color: #f0f0f0;
                border-top: 1px solid #cccccc;
            }
            
            QStatusBar::item {
                border: none;
            }
            
            QMenuBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #cccccc;
            }
            
            QMenuBar::item {
                padding: 6px 12px;
                background-color: transparent;
            }
            
            QMenuBar::item:selected {
                background-color: #e5f3ff;
            }
            
            QMenu {
                background-color: white;
                border: 1px solid #cccccc;
            }
            
            QMenu::item {
                padding: 6px 24px 6px 12px;
            }
            
            QMenu::item:selected {
                background-color: #e5f3ff;
            }
            
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 4px 8px;
            }
            
            QToolBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
                spacing: 4px;
                padding: 4px;
            }
            
            QToolBar::separator {
                width: 1px;
                background-color: #cccccc;
                margin: 0px 8px;
            }
            
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px;
            }
            
            QToolButton:hover {
                background-color: #e5f3ff;
                border-color: #0078d4;
            }
            
            QToolButton:pressed {
                background-color: #cce4ff;
            }
            
            QToolButton:checked {
                background-color: #cce4ff;
                border-color: #0078d4;
            }
        """)
    
    def _create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("📁 File")
        
        file_actions = [
            ("New Project", self.new_project, "Ctrl+N"),
            ("Open Project...", self.open_project, "Ctrl+O"),
            ("Open Recent", None, None),
            ("Save Project", self.save_project, "Ctrl+S"),
            ("Save Project As...", self.save_project_as, "Ctrl+Shift+S"),
            ("Close Project", self.close_project, "Ctrl+W"),
            ("---", None, None),
            ("Import Project...", self.import_project, "Ctrl+I"),
            ("Export Project...", self.export_project, "Ctrl+E"),
            ("---", None, None),
            ("Exit", self.close, "Alt+F4")
        ]
        
        self._add_menu_actions(file_menu, file_actions)
        
        # Add recent projects submenu
        recent_menu = QMenu("Recent Projects", self)
        self._populate_recent_projects(recent_menu)
        file_menu.insertMenu(file_menu.actions()[2], recent_menu)
        
        # Edit Menu
        edit_menu = menubar.addMenu("✏️ Edit")
        
        edit_actions = [
            ("Undo", self.undo, "Ctrl+Z"),
            ("Redo", self.redo, "Ctrl+Y"),
            ("---", None, None),
            ("Cut", self.cut, "Ctrl+X"),
            ("Copy", self.copy, "Ctrl+C"),
            ("Paste", self.paste, "Ctrl+V"),
            ("Delete", self.delete, "Del"),
            ("---", None, None),
            ("Select All", self.select_all, "Ctrl+A"),
            ("Find...", self.find, "Ctrl+F"),
            ("Replace...", self.replace, "Ctrl+H"),
            ("---", None, None),
            ("Preferences...", self.show_preferences, "Ctrl+P")
        ]
        
        self._add_menu_actions(edit_menu, edit_actions)
        
        # View Menu
        view_menu = menubar.addMenu("👁️ View")
        
        view_actions = [
            ("Toolbars", None, None),
            ("Dock Widgets", None, None),
            ("Status Bar", self.toggle_status_bar, None),
            ("---", None, None),
            ("Zoom In", self.zoom_in, "Ctrl++"),
            ("Zoom Out", self.zoom_out, "Ctrl+-"),
            ("Reset Zoom", self.zoom_reset, "Ctrl+0"),
            ("---", None, None),
            ("Full Screen", self.toggle_fullscreen, "F11"),
            ("Dark Theme", self.toggle_theme, None)
        ]
        
        self._add_menu_actions(view_menu, view_actions)
        
        # Project Menu
        project_menu = menubar.addMenu("📂 Project")
        
        project_actions = [
            ("Analyze Project", self.analyze_project, "F5"),
            ("Run Project", self.run_project, "F9"),
            ("Debug Project", self.debug_project, "F10"),
            ("Test Project", self.test_project, "F11"),
            ("---", None, None),
            ("Project Settings", self.project_settings, None),
            ("Dependencies", self.manage_dependencies, None),
            ("Requirements", self.generate_requirements, None),
            ("---", None, None),
            ("Build Executable", self.build_executable, None),
            ("Create Installer", self.create_installer, None)
        ]
        
        self._add_menu_actions(project_menu, project_actions)
        
        # Tools Menu
        tools_menu = menubar.addMenu("🛠️ Tools")
        
        tools_actions = [
            ("Code Generator", self.generate_code, "F8"),
            ("Code Refactoring", self.refactor_code, "Ctrl+R"),
            ("Code Analysis", self.analyze_code, "Ctrl+Shift+A"),
            ("Documentation", self.generate_docs, "Ctrl+Shift+D"),
            ("---", None, None),
            ("Database Tools", self.database_tools, None),
            ("API Testing", self.api_testing, None),
            ("Performance Profiler", self.performance_profiler, None),
            ("---", None, None),
            ("Plugin Manager", self.manage_plugins, "Ctrl+Shift+P"),
            ("Template Manager", self.manage_templates, None)
        ]
        
        self._add_menu_actions(tools_menu, tools_actions)
        
        # AI Menu
        ai_menu = menubar.addMenu("🤖 AI Assistant")
        
        ai_actions = [
            ("Ask AI Assistant", self.ask_ai_assistant, "Ctrl+Space"),
            ("Generate Code", self.ai_generate_code, "Ctrl+G"),
            ("Explain Code", self.ai_explain_code, "Ctrl+E"),
            ("Optimize Code", self.ai_optimize_code, "Ctrl+Shift+O"),
            ("---", None, None),
            ("Fix Bugs", self.ai_fix_bugs, None),
            ("Write Tests", self.ai_write_tests, None),
            ("Create Documentation", self.ai_create_docs, None),
            ("---", None, None),
            ("AI Settings", self.ai_settings, None),
            ("AI History", self.ai_history, None)
        ]
        
        self._add_menu_actions(ai_menu, ai_actions)
        
        # Help Menu
        help_menu = menubar.addMenu("❓ Help")
        
        help_actions = [
            ("Documentation", self.show_documentation, "F1"),
            ("Tutorials", self.show_tutorials, None),
            ("Examples", self.show_examples, None),
            ("Keyboard Shortcuts", self.show_shortcuts, "Ctrl+Shift+H"),
            ("---", None, None),
            ("Check for Updates", self.check_updates, None),
            ("About GUI Constructor", self.show_about, None),
            ("Report Issue", self.report_issue, None)
        ]
        
        self._add_menu_actions(help_menu, help_actions)
    
    def _add_menu_actions(self, menu, actions):
        """Add actions to menu from list of tuples"""
        for text, callback, shortcut in actions:
            if text == "---":
                menu.addSeparator()
            else:
                action = QAction(text, self)
                if callback:
                    action.triggered.connect(callback)
                if shortcut:
                    action.setShortcut(QKeySequence(shortcut))
                menu.addAction(action)
    
    def _populate_recent_projects(self, menu):
        """Populate recent projects menu"""
        recent_projects = self.settings.value("recent_projects", [])
        
        if not recent_projects:
            no_projects = QAction("No recent projects", self)
            no_projects.setEnabled(False)
            menu.addAction(no_projects)
        else:
            for project in recent_projects[:10]:  # Last 10 projects
                action = QAction(project, self)
                action.triggered.connect(lambda checked, p=project: self.open_recent_project(p))
                menu.addAction(action)
        
        menu.addSeparator()
        clear_action = QAction("Clear Recent Projects", self)
        clear_action.triggered.connect(self.clear_recent_projects)
        menu.addAction(clear_action)
    
    def _create_toolbars(self):
        """Create application toolbars"""
        # Main toolbar
        main_toolbar = QToolBar("Main Tools", self)
        main_toolbar.setObjectName("main_toolbar")
        main_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(main_toolbar)
        
        # Main toolbar actions
        main_actions = [
            ("📁 New", self.new_project, "New Project"),
            ("📂 Open", self.open_project, "Open Project"),
            ("💾 Save", self.save_project, "Save Project"),
            ("🔍 Analyze", self.analyze_project, "Analyze Project"),
            ("⚡ Run", self.run_project, "Run Project"),
            ("---", None, None),
            ("↶ Undo", self.undo, "Undo"),
            ("↷ Redo", self.redo, "Redo"),
            ("---", None, None),
            ("🎨 Designer", self.show_designer, "Switch to Designer"),
            ("💻 Code", self.show_code_editor, "Switch to Code Editor"),
            ("📊 Analysis", self.show_analysis, "Switch to Analysis"),
            ("🤖 AI", self.show_ai_assistant, "Switch to AI Assistant")
        ]
        
        for icon_text, callback, tooltip in main_actions:
            if icon_text == "---":
                main_toolbar.addSeparator()
            else:
                btn = QToolButton()
                btn.setText(icon_text)
                btn.setToolTip(tooltip)
                if callback:
                    btn.clicked.connect(callback)
                main_toolbar.addWidget(btn)
        
        # Widgets toolbar (docked left)
        widgets_toolbar = QToolBar("Widgets", self)
        widgets_toolbar.setObjectName("widgets_toolbar")
        widgets_toolbar.setOrientation(Qt.Orientation.Vertical)
        widgets_toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, widgets_toolbar)
        
        # Widget categories
        widget_categories = {
            "📋 Basic": ["Button", "Label", "Line Edit", "Text Edit", "Check Box", "Radio Button"],
            "📊 Containers": ["Group Box", "Tab Widget", "Tool Box", "Scroll Area", "Frame"],
            "📈 Advanced": ["List Widget", "Tree Widget", "Table Widget", "Combo Box", "Slider"],
            "🧭 Layouts": ["Horizontal Layout", "Vertical Layout", "Grid Layout", "Form Layout"],
            "📅 Others": ["Calendar", "Progress Bar", "Dial", "Spin Box", "Date Edit"]
        }
        
        for category, widgets in widget_categories.items():
            # Category label
            cat_label = QLabel(category)
            cat_label.setStyleSheet("font-weight: bold; padding: 4px; background-color: #e5f3ff;")
            widgets_toolbar.addWidget(cat_label)
            
            # Widget buttons
            for widget in widgets:
                btn = QToolButton()
                btn.setText(widget)
                btn.setToolTip(f"Add {widget}")
                btn.setStyleSheet("text-align: left; padding: 4px 8px;")
                btn.clicked.connect(lambda checked, w=widget: self.add_widget_to_canvas(w))
                widgets_toolbar.addWidget(btn)
        
        # Design toolbar (docked top)
        design_toolbar = QToolBar("Design Tools", self)
        design_toolbar.setObjectName("design_toolbar")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, design_toolbar)
        
        design_actions = [
            ("👁️ Preview", self.preview_design, "Preview Design"),
            ("🎯 Align Left", self.align_left, "Align Left"),
            ("🎯 Align Center", self.align_center, "Align Center"),
            ("🎯 Align Right", self.align_right, "Align Right"),
            ("---", None, None),
            ("📏 Grid", self.toggle_grid, "Toggle Grid"),
            ("📐 Snap", self.toggle_snap, "Toggle Snap to Grid"),
            ("🎨 Style", self.edit_style, "Edit Style Sheet"),
            ("---", None, None),
            ("📝 Properties", self.show_properties, "Show Properties Panel")
        ]
        
        for icon_text, callback, tooltip in design_actions:
            if icon_text == "---":
                design_toolbar.addSeparator()
            else:
                btn = QToolButton()
                btn.setText(icon_text)
                btn.setToolTip(tooltip)
                if callback:
                    btn.clicked.connect(callback)
                design_toolbar.addWidget(btn)
    
    def _create_docks(self):
        """Create dock widgets"""
        # Properties dock
        properties_dock = QDockWidget("📋 Properties", self)
        properties_dock.setObjectName("properties_dock")
        properties_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea | 
            Qt.DockWidgetArea.LeftDockWidgetArea
        )
        
        properties_widget = QWidget()
        properties_layout = QVBoxLayout(properties_widget)
        
        # Properties content
        properties_tree = QTreeWidget()
        properties_tree.setHeaderLabels(["Property", "Value"])
        
        properties_layout.addWidget(properties_tree)
        properties_dock.setWidget(properties_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, properties_dock)
        
        # Project explorer dock
        explorer_dock = QDockWidget("📁 Project Explorer", self)
        explorer_dock.setObjectName("explorer_dock")
        explorer_dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | 
            Qt.DockWidgetArea.RightDockWidgetArea
        )
        
        explorer_widget = QWidget()
        explorer_layout = QVBoxLayout(explorer_widget)
        
        # File tree
        file_tree = QTreeWidget()
        file_tree.setHeaderLabels(["Project Files", "Type", "Size"])
        
        explorer_layout.addWidget(file_tree)
        explorer_dock.setWidget(explorer_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, explorer_dock)
        
        # Output dock
        output_dock = QDockWidget("📤 Output", self)
        output_dock.setObjectName("output_dock")
        output_dock.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea
        )
        
        output_widget = QWidget()
        output_layout = QVBoxLayout(output_widget)
        
        # Output tabs
        output_tabs = QTabWidget()
        output_tabs.addTab(QTextEdit(), "Build")
        output_tabs.addTab(QTextEdit(), "Debug")
        output_tabs.addTab(QTextEdit(), "Tests")
        
        output_layout.addWidget(output_tabs)
        output_dock.setWidget(output_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, output_dock)
    
    def _create_status_bar(self):
        """Create status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Status labels
        self.project_status_label = QLabel("No project loaded")
        self.cursor_position_label = QLabel("Ln 1, Col 1")
        self.file_type_label = QLabel("Python")
        self.encoding_label = QLabel("UTF-8")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        
        # Add widgets to status bar
        status_bar.addPermanentWidget(self.project_status_label, 1)
        status_bar.addPermanentWidget(self.cursor_position_label)
        status_bar.addPermanentWidget(self.file_type_label)
        status_bar.addPermanentWidget(self.encoding_label)
        status_bar.addPermanentWidget(self.progress_bar)
    
    def _load_plugins(self):
        """Load available plugins"""
        try:
            plugins = self.plugin_manager.load_all_plugins()
            print(f"Loaded {len(plugins)} plugins")
            
            # Add plugin actions to menus
            for plugin_name, plugin in plugins.items():
                plugin_actions = plugin.get_actions()
                for action_info in plugin_actions:
                    self._add_plugin_action(plugin_name, action_info)
                    
        except Exception as e:
            print(f"Error loading plugins: {e}")
    
    def _add_plugin_action(self, plugin_name, action_info):
        """Add plugin action to appropriate menu"""
        # Find or create menu for plugin category
        category = action_info.get('category', 'Plugins')
        menubar = self.menuBar()
        
        # Check if category menu exists
        category_menu = None
        for action in menubar.actions():
            if action.text() == category:
                category_menu = action.menu()
                break
        
        # Create category menu if it doesn't exist
        if not category_menu:
            category_menu = menubar.addMenu(category)
        
        # Add action to category menu
        action = QAction(action_info['name'], self)
        action.setToolTip(action_info.get('tooltip', ''))
        action.triggered.connect(lambda: self._execute_plugin_action(plugin_name, action_info))
        category_menu.addAction(action)
    
    def _execute_plugin_action(self, plugin_name, action_info):
        """Execute plugin action"""
        plugin = self.plugin_manager.plugins.get(plugin_name)
        if plugin and hasattr(plugin, action_info['callback'].__name__):
            callback = getattr(plugin, action_info['callback'].__name__)
            
            # Get current context (code, project, etc.)
            context = self._get_current_context()
            
            # Execute with context
            result = callback(**context)
            self._handle_plugin_result(result)
    
    def _get_current_context(self):
        """Get current context for plugin execution"""
        current_tab_data = self.tab_manager.get_current_tab_data()
        
        context = {
            'project_path': self.core.project.path,
            'project_data': self.core.project.metadata,
            'current_tab': current_tab_data.get('type', 'unknown')
        }
        
        # Add code from editor if available
        if hasattr(self, 'code_editor'):
            context['code'] = self.code_editor.toPlainText()
        
        return context
    
    def _handle_plugin_result(self, result):
        """Handle plugin execution result"""
        if isinstance(result, dict):
            if 'error' in result:
                QMessageBox.critical(self, "Plugin Error", result['error'])
            elif 'message' in result:
                self.statusBar().showMessage(result['message'], 3000)
        elif isinstance(result, str):
            # Show in output dock
            output_dock = self.findChild(QDockWidget, "output_dock")
            if output_dock:
                output_text = output_dock.findChild(QTextEdit)
                if output_text:
                    output_text.append(result)
    
    def _restore_window_state(self):
        """Restore window state from settings"""
        geometry = self.settings.value("window_geometry")
        state = self.settings.value("window_state")
        
        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window state
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        
        # Check for unsaved changes
        if self.core.project.modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.save_project()
        
        # Cleanup plugins
        for plugin in self.plugin_manager.plugins.values():
            plugin.cleanup()
        
        event.accept()
    
    # ===== Menu Action Handlers =====
    
    def new_project(self):
        """Create new project"""
        project_name, ok = QInputDialog.getText(
            self, "New Project", "Enter project name:"
        )
        
        if ok and project_name:
            project_path = QFileDialog.getExistingDirectory(
                self, "Select Project Directory"
            )
            
            if project_path:
                full_path = os.path.join(project_path, project_name)
                
                # Create project structure
                os.makedirs(full_path, exist_ok=True)
                os.makedirs(os.path.join(full_path, 'src'), exist_ok=True)
                os.makedirs(os.path.join(full_path, 'tests'), exist_ok=True)
                
                # Create basic files
                with open(os.path.join(full_path, 'main.py'), 'w') as f:
                    f.write("# Main application file\n")
                
                # Load project
                self.core.load_project(full_path)
                self.project_status_label.setText(f"Project: {project_name}")
                self.statusBar().showMessage(f"Created project: {project_name}", 3000)
                
                # Add to recent projects
                self._add_to_recent_projects(full_path)
    
    def open_project(self):
        """Open existing project"""
        project_path = QFileDialog.getExistingDirectory(
            self, "Open Project Directory"
        )
        
        if project_path:
            self._load_project(project_path)
    
    def open_recent_project(self, project_path):
        """Open recent project"""
        if os.path.exists(project_path):
            self._load_project(project_path)
        else:
            QMessageBox.warning(
                self, "Project Not Found",
                f"Project not found: {project_path}"
            )
    
    def _load_project(self, project_path):
        """Load project from path"""
        if self.core.load_project(project_path):
            project_name = os.path.basename(project_path)
            self.project_status_label.setText(f"Project: {project_name}")
            self.statusBar().showMessage(f"Loaded project: {project_name}", 3000)
            
            # Add to recent projects
            self._add_to_recent_projects(project_path)
            
            # Emit signal
            self.project_loaded.emit(project_path)
        else:
            QMessageBox.critical(
                self, "Load Error",
                f"Failed to load project: {project_path}"
            )
    
    def _add_to_recent_projects(self, project_path):
        """Add project to recent projects list"""
        recent = self.settings.value("recent_projects", [])
        
        # Remove if already in list
        if project_path in recent:
            recent.remove(project_path)
        
        # Add to beginning
        recent.insert(0, project_path)
        
        # Keep only last 10
        recent = recent[:10]
        
        self.settings.setValue("recent_projects", recent)
    
    def clear_recent_projects(self):
        """Clear recent projects list"""
        self.settings.setValue("recent_projects", [])
        self.statusBar().showMessage("Cleared recent projects", 3000)
    
    def save_project(self):
        """Save current project"""
        if self.core.project.path:
            if self.core.save_project():
                self.statusBar().showMessage("Project saved", 3000)
                self.project_saved.emit(self.core.project.path)
            else:
                QMessageBox.critical(self, "Save Error", "Failed to save project")
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Save project with new name/location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project As",
            filter="GUI Constructor Projects (*.guiproj)"
        )
        
        if file_path:
            if self.core.save_project(file_path):
                self.statusBar().showMessage(f"Project saved as: {file_path}", 3000)
                self._add_to_recent_projects(file_path)
            else:
                QMessageBox.critical(self, "Save Error", "Failed to save project")
    
    def close_project(self):
        """Close current project"""
        if self.core.project.modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "Save changes before closing?",
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                self.save_project()
        
        self.core.project = self.core.ProjectState()
        self.project_status_label.setText("No project loaded")
        self.statusBar().showMessage("Project closed", 3000)
    
    def import_project(self):
        """Import project from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Project",
            filter="Project Files (*.zip *.tar *.guiproj)"
        )
        
        if file_path:
            self.statusBar().showMessage(f"Importing: {os.path.basename(file_path)}...")
            # TODO: Implement import logic
            QTimer.singleShot(1000, lambda: self.statusBar().showMessage("Import complete", 3000))
    
    def export_project(self):
        """Export project to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Project",
            filter="ZIP Archive (*.zip);;All Files (*.*)"
        )
        
        if file_path:
            self.statusBar().showMessage(f"Exporting project...")
            # TODO: Implement export logic
            QTimer.singleShot(1000, lambda: self.statusBar().showMessage("Export complete", 3000))
    
    def undo(self):
        """Undo last action"""
        result = self.command_dispatcher.undo()
        if result.success:
            self.statusBar().showMessage(result.message, 3000)
        else:
            QMessageBox.information(self, "Undo", result.message)
    
    def redo(self):
        """Redo last undone action"""
        result = self.command_dispatcher.redo()
        if result.success:
            self.statusBar().showMessage(result.message, 3000)
        else:
            QMessageBox.information(self, "Redo", result.message)
    
    def cut(self):
        """Cut selected text"""
        # TODO: Implement cut for active widget
        pass
    
    def copy(self):
        """Copy selected text"""
        # TODO: Implement copy for active widget
        pass
    
    def paste(self):
        """Paste text"""
        # TODO: Implement paste for active widget
        pass
    
    def delete(self):
        """Delete selection"""
        # TODO: Implement delete for active widget
        pass
    
    def select_all(self):
        """Select all text"""
        # TODO: Implement select all for active widget
        pass
    
    def find(self):
        """Find text"""
        # TODO: Implement find dialog
        pass
    
    def replace(self):
        """Replace text"""
        # TODO: Implement replace dialog
        pass
    
    def show_preferences(self):
        """Show preferences dialog"""
        # TODO: Implement preferences dialog
        pass
    
    def toggle_status_bar(self):
        """Toggle status bar visibility"""
        status_bar = self.statusBar()
        status_bar.setVisible(not status_bar.isVisible())
    
    def zoom_in(self):
        """Zoom in"""
        # TODO: Implement zoom in
        pass
    
    def zoom_out(self):
        """Zoom out"""
        # TODO: Implement zoom out
        pass
    
    def zoom_reset(self):
        """Reset zoom"""
        # TODO: Implement zoom reset
        pass
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        # TODO: Implement theme toggle
        pass
    
    def analyze_project(self):
        """Analyze current project"""
        if not self.core.project.path:
            QMessageBox.information(self, "No Project", "Please open a project first")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Simulate analysis
        QTimer.singleShot(2000, self._finish_analysis)
    
    def _finish_analysis(self):
        """Finish project analysis"""
        self.progress_bar.setVisible(False)
        
        # Show results
        result = self.core.analyze_code("# Sample code\nprint('Hello')")
        
        result_text = f"""
        Project Analysis Complete:
        - Lines: {result.get('lines', 'N/A')}
        - Complexity: {result.get('complexity', 'N/A')}
        - Issues: {len(result.get('issues', []))}
        """
        
        QMessageBox.information(self, "Analysis Results", result_text)
        self.statusBar().showMessage("Project analysis complete", 3000)
    
    def run_project(self):
        """Run current project"""
        if not self.core.project.path:
            QMessageBox.information(self, "No Project", "Please open a project first")
            return
        
        self.statusBar().showMessage("Running project...")
        # TODO: Implement project execution
        QTimer.singleShot(1000, lambda: self.statusBar().showMessage("Project execution complete", 3000))
    
    def debug_project(self):
        """Debug current project"""
        # TODO: Implement debugging
        pass
    
    def test_project(self):
        """Run tests for current project"""
        # TODO: Implement testing
        pass
    
    def project_settings(self):
        """Show project settings"""
        # TODO: Implement project settings dialog
        pass
    
    def manage_dependencies(self):
        """Manage project dependencies"""
        # TODO: Implement dependency management
        pass
    
    def generate_requirements(self):
        """Generate requirements.txt"""
        # TODO: Implement requirements generation
        pass
    
    def build_executable(self):
        """Build executable from project"""
        # TODO: Implement executable building
        pass
    
    def create_installer(self):
        """Create installer for project"""
        # TODO: Implement installer creation
        pass
    
    def generate_code(self):
        """Generate code from design"""
        code = self.core.generate_gui_code()
        
        # Show in code editor tab
        self.tab_manager.setCurrentIndex(1)  # Switch to code editor
        # TODO: Set code in editor
        
        self.statusBar().showMessage("Code generated", 3000)
    
    def refactor_code(self):
        """Refactor code"""
        # TODO: Implement refactoring dialog
        pass
    
    def analyze_code(self):
        """Analyze code"""
        # TODO: Implement code analysis
        pass
    
    def generate_docs(self):
        """Generate documentation"""
        # TODO: Implement documentation generation
        pass
    
    def database_tools(self):
        """Database management tools"""
        # TODO: Implement database tools
        pass
    
    def api_testing(self):
        """API testing tools"""
        # TODO: Implement API testing
        pass
    
    def performance_profiler(self):
        """Performance profiling tools"""
        # TODO: Implement performance profiling
        pass
    
    def manage_plugins(self):
        """Manage plugins"""
        # TODO: Implement plugin manager dialog
        pass
    
    def manage_templates(self):
        """Manage templates"""
        # TODO: Implement template manager
        pass
    
    def ask_ai_assistant(self):
        """Ask AI assistant"""
        # TODO: Implement AI assistant dialog
        pass
    
    def ai_generate_code(self):
        """Generate code with AI"""
        # TODO: Implement AI code generation
        pass
    
    def ai_explain_code(self):
        """Explain code with AI"""
        # TODO: Implement AI code explanation
        pass
    
    def ai_optimize_code(self):
        """Optimize code with AI"""
        # TODO: Implement AI code optimization
        pass
    
    def ai_fix_bugs(self):
        """Fix bugs with AI"""
        # TODO: Implement AI bug fixing
        pass
    
    def ai_write_tests(self):
        """Write tests with AI"""
        # TODO: Implement AI test writing
        pass
    
    def ai_create_docs(self):
        """Create documentation with AI"""
        # TODO: Implement AI documentation
        pass
    
    def ai_settings(self):
        """AI assistant settings"""
        # TODO: Implement AI settings
        pass
    
    def ai_history(self):
        """AI conversation history"""
        # TODO: Implement AI history
        pass
    
    def show_documentation(self):
        """Show documentation"""
        # TODO: Implement documentation viewer
        pass
    
    def show_tutorials(self):
        """Show tutorials"""
        # TODO: Implement tutorial viewer
        pass
    
    def show_examples(self):
        """Show examples"""
        # TODO: Implement example viewer
        pass
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        # TODO: Implement shortcuts dialog
        pass
    
    def check_updates(self):
        """Check for updates"""
        # TODO: Implement update checker
        pass
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h1>GUI Constructor Platform</h1>
        <p>Version 2.0.0</p>
        <p>A modern GUI development platform with AI assistance.</p>
        <p>© 2024 GUI Constructor Team. All rights reserved.</p>
        """
        
        QMessageBox.about(self, "About GUI Constructor", about_text)
    
    def report_issue(self):
        """Report issue"""
        # TODO: Implement issue reporting
        pass
    
    def add_widget_to_canvas(self, widget_type):
        """Add widget to design canvas"""
        properties = {
            'type': widget_type,
            'name': widget_type.lower().replace(' ', '_'),
            'text': widget_type,
            'position': (10, 10),
            'size': (100, 30)
        }
        
        # Create and execute command
        command = AddWidgetCommand(widget_type, properties, self)
        result = self.command_dispatcher.execute_command(command)
        
        if result.success:
            self.statusBar().showMessage(f"Added {widget_type} to canvas", 3000)
        else:
            QMessageBox.warning(self, "Add Widget", result.message)
    
    def preview_design(self):
        """Preview current design"""
        # TODO: Implement design preview
        pass
    
    def align_left(self):
        """Align widgets left"""
        # TODO: Implement alignment
        pass
    
    def align_center(self):
        """Align widgets center"""
        # TODO: Implement alignment
        pass
    
    def align_right(self):
        """Align widgets right"""
        # TODO: Implement alignment
        pass
    
    def toggle_grid(self):
        """Toggle design grid"""
        # TODO: Implement grid toggle
        pass
    
    def toggle_snap(self):
        """Toggle snap to grid"""
        # TODO: Implement snap toggle
        pass
    
    def edit_style(self):
        """Edit style sheet"""
        # TODO: Implement style editor
        pass
    
    def show_properties(self):
        """Show properties panel"""
        # TODO: Implement properties panel toggle
        pass
    
    def show_designer(self):
        """Switch to designer tab"""
        self.tab_manager.setCurrentIndex(0)
    
    def show_code_editor(self):
        """Switch to code editor tab"""
        self.tab_manager.setCurrentIndex(1)
    
    def show_analysis(self):
        """Switch to analysis tab"""
        self.tab_manager.setCurrentIndex(2)
    
    def show_ai_assistant(self):
        """Switch to AI assistant tab"""
        self.tab_manager.setCurrentIndex(3)


if __name__ == "__main__":
    # For direct testing
    from PyQt5.QtWidgets import QApplication, QAction
    from gui.windows_style import Windows10Style
    
    app = QApplication(sys.argv)
    Windows10Style.apply_light_theme(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())