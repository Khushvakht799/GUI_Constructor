"""
Tab Manager - handles tabbed interface for GUI Constructor.
"""

from PyQt5.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,, QAction
                             QPushButton, QLabel, QTextEdit, QTreeWidget,
                             QTreeWidgetItem, QListWidget, QSplitter,
                             QToolBar, QStatusBar, QDockWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon


class TabManager(QTabWidget):
    """Manages application tabs with Windows 10 style"""
    
    tab_changed = pyqtSignal(int)  # Signal when tab changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tabs_data = {}  # Store tab-specific data
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup tab widget appearance"""
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setDocumentMode(True)
        self.tabCloseRequested.connect(self.close_tab)
        
        # Customize appearance
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #000000;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #cccccc;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #e5f3ff;
            }
        """)
    
    def create_designer_tab(self) -> QWidget:
        """Create designer/canvas tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Toolbar for designer
        designer_toolbar = QToolBar("Designer Tools")
        designer_toolbar.setMovable(False)
        
        # Widget palette buttons
        widget_types = [
            ("Button", "🟦", "QPushButton"),
            ("Label", "🏷️", "QLabel"),
            ("Text Edit", "📝", "QTextEdit"),
            ("Line Edit", "📄", "QLineEdit"),
            ("Combo Box", "📋", "QComboBox"),
            ("List Widget", "📃", "QListWidget"),
            ("Tree Widget", "🌳", "QTreeWidget"),
            ("Table Widget", "📊", "QTableWidget"),
            ("Group Box", "📦", "QGroupBox"),
            ("Tab Widget", "📑", "QTabWidget"),
            ("Scroll Area", "📜", "QScrollArea"),
            ("Tool Box", "🧰", "QToolBox")
        ]
        
        for name, icon, widget_class in widget_types:
            action = QAction(f"{icon} {name}", self)
            action.setToolTip(f"Add {widget_class}")
            action.setData(widget_class)
            designer_toolbar.addAction(action)
        
        # Canvas area (placeholder)
        canvas_label = QLabel("🖌️ Design Canvas Area\n\n"
                            "Drag and drop widgets here to design your GUI")
        canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 2px dashed #cccccc;
                border-radius: 8px;
                padding: 40px;
                font-size: 14px;
                color: #666666;
            }
        """)
        
        # Properties panel
        properties_panel = self._create_properties_panel()
        
        # Split layout
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(canvas_label)
        splitter.addWidget(properties_panel)
        splitter.setSizes([400, 200])
        
        layout.addWidget(designer_toolbar)
        layout.addWidget(splitter)
        
        self.tabs_data[id(tab)] = {
            'type': 'designer',
            'widgets': [],
            'layout': 'vertical'
        }
        
        return tab
    
    def _create_properties_panel(self) -> QWidget:
        """Create properties panel for widget editing"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Panel title
        title = QLabel("📋 Widget Properties")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
        layout.addWidget(title)
        
        # Property tree
        properties_tree = QTreeWidget()
        properties_tree.setHeaderLabels(["Property", "Value"])
        properties_tree.setColumnWidth(0, 150)
        
        # Sample properties
        sample_properties = [
            ("General", [
                ("Name", "pushButton"),
                ("Type", "QPushButton"),
                ("Enabled", "True")
            ]),
            ("Geometry", [
                ("X Position", "10"),
                ("Y Position", "10"),
                ("Width", "100"),
                ("Height", "32")
            ]),
            ("Text", [
                ("Label", "Click Me"),
                ("Font", "Segoe UI, 9pt"),
                ("Alignment", "Center")
            ]),
            ("Style", [
                ("Background", "#0078d4"),
                ("Text Color", "#ffffff"),
                ("Border", "None")
            ])
        ]
        
        for category, props in sample_properties:
            category_item = QTreeWidgetItem(properties_tree, [category])
            for prop_name, prop_value in props:
                prop_item = QTreeWidgetItem(category_item, [prop_name, prop_value])
                category_item.addChild(prop_item)
            properties_tree.addTopLevelItem(category_item)
            category_item.setExpanded(True)
        
        layout.addWidget(properties_tree)
        
        # Apply button
        apply_btn = QPushButton("💾 Apply Changes")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(apply_btn)
        
        panel.setMaximumWidth(250)
        return panel
    
    def create_code_editor_tab(self) -> QWidget:
        """Create code editor tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Code editor toolbar
        code_toolbar = QToolBar("Code Tools")
        
        code_actions = [
            ("💾 Save", "Ctrl+S"),
            ("📄 New File", "Ctrl+N"),
            ("📂 Open", "Ctrl+O"),
            ("🔍 Find", "Ctrl+F"),
            ("🔄 Replace", "Ctrl+H"),
            ("▶️ Run", "F5"),
            ("🐛 Debug", "F9"),
            ("📋 Format", "Ctrl+Shift+F")
        ]
        
        for text, shortcut in code_actions:
            action = QAction(text, self)
            action.setShortcut(shortcut)
            code_toolbar.addAction(action)
        
        # Code editor area
        code_edit = QTextEdit()
        code_edit.setPlaceholderText("Python code will appear here...\n\n"
                                   "Generated code from designer or\n"
                                   "write your own code here.")
        code_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #264f78;
                border: none;
            }
        """)
        
        # Output panel
        output_label = QLabel("📤 Output")
        output_edit = QTextEdit()
        output_edit.setMaximumHeight(150)
        output_edit.setReadOnly(True)
        output_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', monospace;
                font-size: 11px;
                background-color: #0c0c0c;
                color: #cccccc;
            }
        """)
        
        layout.addWidget(code_toolbar)
        layout.addWidget(code_edit)
        layout.addWidget(output_label)
        layout.addWidget(output_edit)
        
        self.tabs_data[id(tab)] = {
            'type': 'code_editor',
            'file_path': None,
            'modified': False
        }
        
        return tab
    
    def create_analysis_tab(self) -> QWidget:
        """Create project analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Analysis toolbar
        analysis_toolbar = QToolBar("Analysis Tools")
        
        analysis_actions = [
            ("📊 Analyze Project", "Analyze project structure"),
            ("🔍 Code Metrics", "Calculate code metrics"),
            ("📈 Dependencies", "Show dependency graph"),
            ("⚠️ Issues", "Find code issues"),
            ("✅ Lint", "Run code linter"),
            ("📋 Report", "Generate analysis report")
        ]
        
        for text, tooltip in analysis_actions:
            action = QAction(text, self)
            action.setToolTip(tooltip)
            analysis_toolbar.addAction(action)
        
        # Analysis results area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tree view for project structure
        project_tree = QTreeWidget()
        project_tree.setHeaderLabels(["Project Structure", "Type", "Size"])
        project_tree.setColumnWidth(0, 250)
        
        # Sample project structure
        root = QTreeWidgetItem(project_tree, ["MyProject", "Project", ""])
        items = [
            (["src", "Folder", ""], [
                (["main.py", "Python", "2.4 KB"], []),
                (["config.py", "Python", "1.1 KB"], []),
                (["utils", "Folder", ""], [
                    (["helpers.py", "Python", "3.2 KB"], []),
                    (["validators.py", "Python", "2.8 KB"], [])
                ])
            ]),
            (["tests", "Folder", ""], [
                (["test_main.py", "Python", "4.1 KB"], []),
                (["test_utils.py", "Python", "3.7 KB"], [])
            ]),
            (["requirements.txt", "Text", "0.2 KB"], []),
            (["README.md", "Markdown", "1.5 KB"], [])
        ]
        
        def add_items(parent, items_list):
            for item_data, children in items_list:
                item = QTreeWidgetItem(parent, item_data)
                if children:
                    add_items(item, children)
        
        add_items(root, items)
        root.setExpanded(True)
        
        # Analysis results panel
        results_panel = QWidget()
        results_layout = QVBoxLayout(results_panel)
        
        # Metrics display
        metrics_label = QLabel("📐 Project Metrics")
        metrics_label.setStyleSheet("font-weight: bold; padding: 8px;")
        results_layout.addWidget(metrics_label)
        
        metrics_text = QTextEdit()
        metrics_text.setReadOnly(True)
        metrics_text.setHtml("""
            <h3>Project Analysis Results</h3>
            <table border="1" cellpadding="5">
            <tr><td><b>Total Files:</b></td><td>24</td></tr>
            <tr><td><b>Python Files:</b></td><td>18</td></tr>
            <tr><td><b>Total Lines:</b></td><td>1,842</td></tr>
            <tr><td><b>Code Lines:</b></td><td>1,254</td></tr>
            <tr><td><b>Comment Lines:</b></td><td>312</td></tr>
            <tr><td><b>Blank Lines:</b></td><td>276</td></tr>
            <tr><td><b>Cyclomatic Complexity:</b></td><td>Low (Average: 3.2)</td></tr>
            <tr><td><b>Code Issues:</b></td><td>12 (Minor)</td></tr>
            <tr><td><b>Dependencies:</b></td><td>8 packages</td></tr>
            </table>
            
            <h3>Recommendations:</h3>
            <ul>
            <li>✅ Code structure is good</li>
            <li>⚠️ Add docstrings to 3 functions</li>
            <li>⚠️ Consider splitting large files</li>
            <li>✅ Dependencies are up-to-date</li>
            </ul>
        """)
        results_layout.addWidget(metrics_text)
        
        splitter.addWidget(project_tree)
        splitter.addWidget(results_panel)
        splitter.setSizes([300, 500])
        
        layout.addWidget(analysis_toolbar)
        layout.addWidget(splitter)
        
        self.tabs_data[id(tab)] = {
            'type': 'analysis',
            'project_path': None,
            'analysis_data': {}
        }
        
        return tab
    
    def create_ai_assistant_tab(self) -> QWidget:
        """Create AI assistant tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # AI Assistant header
        header = QLabel("🤖 AI Assistant")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #0078d4;
                padding: 12px;
                background-color: #f0f8ff;
                border-bottom: 2px solid #0078d4;
            }
        """)
        layout.addWidget(header)
        
        # Chat area
        chat_display = QTextEdit()
        chat_display.setReadOnly(True)
        chat_display.setHtml("""
            <div style='padding: 10px;'>
                <div style='background-color: #e5f3ff; padding: 8px; border-radius: 8px; margin: 5px;'>
                    <b>AI Assistant:</b> Hello! I'm your AI assistant. How can I help you with GUI development today?
                </div>
                <div style='text-align: right;'>
                    <div style='background-color: #d4edda; padding: 8px; border-radius: 8px; margin: 5px; display: inline-block;'>
                        <b>You:</b> Help me create a login form
                    </div>
                </div>
                <div style='background-color: #e5f3ff; padding: 8px; border-radius: 8px; margin: 5px;'>
                    <b>AI Assistant:</b> I can help with that! A login form typically needs:<br>
                    1. Username field<br>
                    2. Password field<br>
                    3. Login button<br>
                    4. Optional: Remember me checkbox<br>
                    Would you like me to generate the code for this?
                </div>
            </div>
        """)
        layout.addWidget(chat_display)
        
        # Input area
        input_panel = QWidget()
        input_layout = QHBoxLayout(input_panel)
        
        ai_input = QTextEdit()
        ai_input.setMaximumHeight(80)
        ai_input.setPlaceholderText("Type your question or request here...")
        input_layout.addWidget(ai_input)
        
        # AI action buttons
        buttons_panel = QWidget()
        buttons_layout = QVBoxLayout(buttons_panel)
        
        ai_buttons = [
            ("💡 Generate Code", "primary"),
            ("🔍 Analyze", "secondary"),
            ("🔄 Refactor", "secondary"),
            ("📝 Document", "secondary"),
            ("🐛 Debug", "secondary")
        ]
        
        for text, btn_type in ai_buttons:
            btn = QPushButton(text)
            if btn_type == "primary":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        font-weight: bold;
                        padding: 8px;
                        margin: 2px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        padding: 6px;
                        margin: 2px;
                    }
                """)
            buttons_layout.addWidget(btn)
        
        input_layout.addWidget(buttons_panel)
        layout.addWidget(input_panel)
        
        # Quick prompts
        prompts_label = QLabel("💭 Quick Prompts:")
        layout.addWidget(prompts_label)
        
        prompts_widget = QWidget()
        prompts_layout = QHBoxLayout(prompts_widget)
        
        quick_prompts = [
            "Create login form",
            "Add data table",
            "Fix layout issues",
            "Optimize performance",
            "Add dark theme"
        ]
        
        for prompt in quick_prompts:
            prompt_btn = QPushButton(prompt)
            prompt_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e5f3ff;
                    border: 1px solid #0078d4;
                    padding: 6px 12px;
                    margin: 2px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #cce4ff;
                }
            """)
            prompts_layout.addWidget(prompt_btn)
        
        layout.addWidget(prompts_widget)
        
        self.tabs_data[id(tab)] = {
            'type': 'ai_assistant',
            'conversation': [],
            'model': 'gpt-3.5-turbo'
        }
        
        return tab
    
    def create_settings_tab(self) -> QWidget:
        """Create settings/configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Settings header
        header = QLabel("⚙️ Settings")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 12px;
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
        """)
        layout.addWidget(header)
        
        # Settings categories
        categories = QListWidget()
        categories.addItems([
            "General",
            "Editor",
            "Designer",
            "AI Assistant", 
            "Plugins",
            "Appearance",
            "Keyboard",
            "Updates"
        ])
        categories.setMaximumWidth(200)
        
        # Settings content area
        settings_content = QTextEdit()
        settings_content.setReadOnly(True)
        settings_content.setHtml("""
            <h2>General Settings</h2>
            <p>Configure general application behavior and preferences.</p>
            
            <h3>Application</h3>
            <ul>
            <li><b>Language:</b> English</li>
            <li><b>Theme:</b> Windows 10 Light</li>
            <li><b>Auto-save:</b> Enabled (every 5 minutes)</li>
            <li><b>Check for updates:</b> Weekly</li>
            </ul>
            
            <h3>Projects</h3>
            <ul>
            <li><b>Default project location:</b> C:\\Projects</li>
            <li><b>Recent projects to show:</b> 10</li>
            <li><b>Auto-open last project:</b> Enabled</li>
            </ul>
            
            <h3>File Handling</h3>
            <ul>
            <li><b>Default file encoding:</b> UTF-8</li>
            <li><b>Line endings:</b> System default (CRLF)</li>
            <li><b>Backup files:</b> Enabled (.bak)</li>
            </ul>
        """)
        
        # Layout for categories and content
        settings_splitter = QSplitter(Qt.Orientation.Horizontal)
        settings_splitter.addWidget(categories)
        settings_splitter.addWidget(settings_content)
        
        layout.addWidget(settings_splitter)
        
        # Save/Cancel buttons
        button_panel = QWidget()
        button_layout = QHBoxLayout(button_panel)
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                padding: 8px 16px;
            }
        """)
        
        reset_btn = QPushButton("Reset to Defaults")
        
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addWidget(button_panel)
        
        self.tabs_data[id(tab)] = {
            'type': 'settings',
            'settings': {}
        }
        
        return tab
    
    def add_default_tabs(self):
        """Add default tabs to the application"""
        self.addTab(self.create_designer_tab(), "🎨 Designer")
        self.addTab(self.create_code_editor_tab(), "💻 Code Editor")
        self.addTab(self.create_analysis_tab(), "📊 Analysis")
        self.addTab(self.create_ai_assistant_tab(), "🤖 AI Assistant")
        self.addTab(self.create_settings_tab(), "⚙️ Settings")
    
    def close_tab(self, index):
        """Close tab at specified index"""
        if index >= 0 and index < self.count():
            widget = self.widget(index)
            tab_id = id(widget)
            
            # Clean up tab data
            if tab_id in self.tabs_data:
                del self.tabs_data[tab_id]
            
            # Remove tab
            self.removeTab(index)
            
            # If no tabs left, add default tabs
            if self.count() == 0:
                self.add_default_tabs()
    
    def get_current_tab_data(self):
        """Get data for current tab"""
        current_widget = self.currentWidget()
        if current_widget:
            tab_id = id(current_widget)
            return self.tabs_data.get(tab_id, {})
        return {}
    
    def set_current_tab_data(self, key, value):
        """Set data for current tab"""
        current_widget = self.currentWidget()
        if current_widget:
            tab_id = id(current_widget)
            if tab_id not in self.tabs_data:
                self.tabs_data[tab_id] = {}
            self.tabs_data[tab_id][key] = value