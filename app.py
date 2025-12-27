"""
GUI Constructor - Main Application Entry Point.
Modern GUI platform for Python GUI development with AI assistance.
PyQt5 compatible version.
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def main():
    """Main application entry point"""
    try:
        # Test PyQt5 import first
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QFont
        print("✓ PyQt5 imports successful")
        
        # Import application modules
        from gui.gui_main import MainWindow
        from gui.windows_style import Windows10Style
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("GUI Constructor")
        app.setOrganizationName("GUI Constructor Team")
        
        # Apply Windows 10 style
        Windows10Style.apply_light_theme(app)
        app.setFont(Windows10Style.get_font_settings())
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        # Start application event loop
        return app.exec_()
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("\nPlease install required dependencies:")
        print("  pip install PyQt5")
        return 1
    except Exception as e:
        print(f"✗ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())