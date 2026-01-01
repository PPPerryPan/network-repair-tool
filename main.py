"""Network Repair Tool Main Entry"""
import sys
import customtkinter as ctk
from gui import NetworkRepairGUI
from admin_utils import is_admin, request_admin_privileges


def main():
    """Main function"""
    # Check if running with administrator privileges
    if not is_admin():
        # Request administrator privileges
        if request_admin_privileges():
            # Privilege escalation successful, exit current process
            sys.exit()
        else:
            # Privilege escalation failed, exit program
            print("Administrator privileges are required to run this program")
            sys.exit(1)
    
    root = ctk.CTk()
    app = NetworkRepairGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
