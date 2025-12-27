"""
Windows 10 style definitions for GUI Constructor.
PyQt5 compatible version.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont


class Windows10Style:
    """Windows 10 style configuration for PyQt5"""
    
    @staticmethod
    def apply_dark_theme(app):
        """Apply Windows 10 dark theme for PyQt5"""
        app.setStyle("Fusion")
        
        dark_palette = QPalette()
        
        # Base colors
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        
        # Link colors
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
        
        # Disabled colors
        dark_palette.setColor(QPalette.Disabled, QPalette.WindowText,
                             QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.Text,
                             QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText,
                             QColor(127, 127, 127))
        
        app.setPalette(dark_palette)
        app.setStyleSheet(Windows10Style.get_dark_stylesheet())
    
    @staticmethod
    def apply_light_theme(app):
        """Apply Windows 10 light theme for PyQt5"""
        app.setStyle("Fusion")
        
        light_palette = QPalette()
        
        # Base colors
        light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
        light_palette.setColor(QPalette.WindowText, Qt.black)
        light_palette.setColor(QPalette.Base, Qt.white)
        light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipBase, Qt.white)
        light_palette.setColor(QPalette.ToolTipText, Qt.black)
        light_palette.setColor(QPalette.Text, Qt.black)
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ButtonText, Qt.black)
        light_palette.setColor(QPalette.BrightText, Qt.red)
        
        # Link colors
        light_palette.setColor(QPalette.Link, QColor(0, 102, 204))
        light_palette.setColor(QPalette.Highlight, QColor(0, 102, 204))
        light_palette.setColor(QPalette.HighlightedText, Qt.white)
        
        app.setPalette(light_palette)
        app.setStyleSheet(Windows10Style.get_light_stylesheet())
    
    @staticmethod
    def get_dark_stylesheet():
        """Get dark theme stylesheet for PyQt5"""
        return """
            QToolTip {
                color: #ffffff;
                background-color: #2a82da;
                border: 1px solid white;
            }
            
            QMenuBar {
                background-color: #353535;
                color: white;
            }
            
            QMenuBar::item:selected {
                background-color: #2a82da;
            }
            
            QStatusBar {
                background-color: #353535;
                color: white;
            }
            
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #353535;
            }
            
            QTabBar::tab {
                background-color: #454545;
                color: white;
                padding: 8px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #2a82da;
            }
            
            QTabBar::tab:hover {
                background-color: #555555;
            }
        """
    
    @staticmethod
    def get_light_stylesheet():
        """Get light theme stylesheet for PyQt5"""
        return """
            QToolTip {
                border: 1px solid #767676;
                background-color: white;
            }
            
            QMenuBar {
                background-color: #f0f0f0;
            }
            
            QMenuBar::item:selected {
                background-color: #e5f3ff;
            }
            
            QStatusBar {
                background-color: #f0f0f0;
            }
            
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px;
                margin-right: 2px;
                border: 1px solid #cccccc;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            
            QTabBar::tab:hover {
                background-color: #e5f3ff;
            }
            
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 6px 12px;
                border-radius: 4px;
            }
            
            QPushButton:hover {
                background-color: #e5f3ff;
                border-color: #0078d4;
            }
            
            QPushButton:pressed {
                background-color: #cce4ff;
            }
        """
    
    @staticmethod
    def get_font_settings():
        """Get Windows 10 recommended font settings for PyQt5"""
        font = QFont("Segoe UI", 10)
        font.setStyleStrategy(QFont.PreferAntialias)
        return font


class ModernButtonStyle:
    """Modern button styling for Windows 10 - PyQt5 version"""
    
    @staticmethod
    def get_button_style(button_type="default"):
        """Get CSS style for different button types"""
        styles = {
            "default": """
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
            """,
            "secondary": """
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e5f3ff;
                    border-color: #0078d4;
                }
            """,
            "danger": """
                QPushButton {
                    background-color: #d13438;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #c12a2e;
                }
            """,
            "success": """
                QPushButton {
                    background-color: #107c10;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #0e6b0e;
                }
            """
        }
        return styles.get(button_type, styles["default"])