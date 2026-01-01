"""网络修复工具主入口"""
import sys
import customtkinter as ctk
from gui import NetworkRepairGUI
from admin_utils import is_admin, request_admin_privileges


def main():
    """主函数"""
    # 检查是否以管理员身份运行
    if not is_admin():
        # 请求管理员权限
        if request_admin_privileges():
            # 提权成功，退出当前进程
            sys.exit()
        else:
            # 提权失败，退出程序
            print("需要管理员权限才能运行此程序")
            sys.exit(1)
    
    # 替换 tk.Tk() 为 ctk.CTk() 以获得原生 WinUI3 风格支持
    root = ctk.CTk()
    app = NetworkRepairGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
