import sys
import os

# Redirect stdout and stderr to null to prevent console output
if hasattr(sys, '_MEIPASS'):  # Only when running from PyInstaller
    # Redirect stdout to null
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    # Also suppress print statements
    def _suppress_print(*args, **kwargs):
        pass
    
    # Replace built-in print function
    __builtins__['print'] = _suppress_print
