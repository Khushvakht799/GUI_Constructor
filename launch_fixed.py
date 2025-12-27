"""
Fixed launch script with correct PyQt5 imports.
"""

import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

# Test PyQt5 imports
try:
    from PyQt5.QtWidgets import QApplication, QAction
    print("✓ PyQt5 imports successful")
    
    # Import after fixing paths
    from gui.gui_main import MainWindow
    from gui.windows_style import Windows10Style
    
    # Create and run app
    app = QApplication(sys.argv)
    Windows10Style.apply_light_theme(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nChecking imports...")
    
    # Try to identify the problem
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ QApplication imports OK")
    except ImportError as e2:
        print(f"✗ QApplication error: {e2}")
    
    try:
        from PyQt5.QtWidgets import QAction
        print("✓ QAction imports OK")
    except ImportError as e2:
        print(f"✗ QAction error: {e2}")
        print("\nIn PyQt5, QAction is in QtWidgets, not QtGui!")
    
    sys.exit(1)