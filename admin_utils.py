"""Administrator Privileges Utility Module"""
import ctypes
import sys


def is_admin():
    """Check if currently running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def request_admin_privileges():
    """Request administrator privileges (re-run program as administrator)"""
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join([sys.argv[0]] + sys.argv[1:]), None, 1
        )
        return True
    except Exception as e:
        return False

