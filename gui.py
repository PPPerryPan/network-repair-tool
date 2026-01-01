"""GUI 界面模块"""
import sys
import os
import tkinter as tk
from tkinter import ttk
import threading
import queue
import customtkinter as ctk

from constants import REPAIR_STEPS, THEME_COLORS, STEP_STATUS_CONFIG
from network_utils import (
    get_ethernet_adapters,
    configure_network,
    set_dns_to_dhcp,
    refresh_network_config,
    display_network_info,
    # upload_usage
)


class NetworkRepairGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("网络修复工具")
        self.root.geometry("800x850")
        
        # 设置 CustomTkinter 主题
        self.appearance_mode = "System"
        ctk.set_appearance_mode(self.appearance_mode)  # 跟随系统
        ctk.set_default_color_theme("blue")
        
        # 设置窗口图标
        self.setup_icon()
        
        # 颜色配置 - 根据外观模式选择颜色
        current_mode = ctk.get_appearance_mode().lower()
        self.colors = THEME_COLORS.get(current_mode, THEME_COLORS['light'])
        
        # 创建消息队列用于线程间通信
        self.message_queue = queue.Queue()
        
        # 状态变量
        self.current_step = 0
        self.is_repairing = False
        
        self.setup_ui()
        self.start_repair_automatically()
        
    def setup_icon(self):
        """设置窗口图标和任务栏图标"""
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(__file__)
            
            possible_paths = [
                os.path.join(base_path, 'icon.ico'),
                os.path.join(base_path, '..', 'icon.ico'),
                os.path.join(os.path.dirname(base_path), 'icon.ico'),
            ]
            
            icon_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    icon_path = path
                    break
            
            if icon_path and os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"未找到图标文件，尝试的路径: {possible_paths}")
        except Exception as e:
            print(f"设置窗口图标失败: {e}")
        
    def setup_ui(self):
        """设置用户界面"""
        # 配置 Grid 权重
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # 主背景容器
        main_container = ctk.CTkFrame(self.root, corner_radius=0, fg_color=self.colors['background'])
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(2, weight=1) # 日志区域自适应高度
        
        # 1. 标题卡片区域
        header_frame = ctk.CTkFrame(
            main_container, 
            fg_color=self.colors['surface'], 
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb" if ctk.get_appearance_mode().lower() == "light" else "#334155",
            height=100
        )
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 15), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🔧 网络修复工具", 
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=28, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="自动检测并修复本地网络连接问题", 
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=15),
            text_color=self.colors['text_secondary']
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        
        # 2. 步骤进度卡片
        steps_frame = ctk.CTkFrame(
            main_container, 
            fg_color=self.colors['surface'], 
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb" if ctk.get_appearance_mode().lower() == "light" else "#334155"
        )
        steps_frame.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        
        self.steps = REPAIR_STEPS
        self.step_icons = []
        self.step_labels = []
        
        # 配置列权重
        for i in range(len(self.steps)):
            steps_frame.grid_columnconfigure(i, weight=1)
            
        for i, step in enumerate(self.steps):
            # 单个步骤容器
            step_container = ctk.CTkFrame(steps_frame, fg_color="transparent")
            step_container.grid(row=0, column=i, padx=5, pady=20, sticky="ew")
            
            # 添加悬停效果
            step_container.bind("<Enter>", lambda e, container=step_container: container.configure(fg_color="#f1f5f9" if ctk.get_appearance_mode().lower() == "light" else "#334155"))
            step_container.bind("<Leave>", lambda e, container=step_container: container.configure(fg_color="transparent"))
            
            # 图标
            icon_label = ctk.CTkLabel(
                step_container, 
                text="⏳", 
                font=ctk.CTkFont(family="Segoe UI Emoji", size=24)
            )
            icon_label.pack(side="top", pady=(0, 8))
            self.step_icons.append(icon_label)
            
            # 文字
            step_label = ctk.CTkLabel(
                step_container, 
                text=step, 
                font=ctk.CTkFont(family="Microsoft YaHei UI", size=12),
                text_color=self.colors['text_secondary']
            )
            step_label.pack(side="top")
            self.step_labels.append(step_label)
            
        # 3. 执行日志卡片
        log_frame = ctk.CTkFrame(
            main_container, 
            fg_color=self.colors['surface'], 
            corner_radius=12,
            border_width=1,
            border_color="#e5e7eb" if ctk.get_appearance_mode().lower() == "light" else "#334155"
        )
        log_frame.grid(row=2, column=0, padx=20, pady=(15, 20), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        log_title = ctk.CTkLabel(
            log_frame, 
            text="📋 执行日志", 
            font=ctk.CTkFont(family="Microsoft YaHei UI", size=16, weight="bold"),
            text_color=self.colors['text']
        )
        log_title.grid(row=0, column=0, padx=20, pady=(20, 15), sticky="w")
        
        # 文本框
        self.output_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color=self.colors['text'],
            fg_color="#f8f9fa" if ctk.get_appearance_mode().lower() == "light" else "#1e293b",
            border_width=1,
            border_color="#e2e8f0" if ctk.get_appearance_mode().lower() == "light" else "#334155",
            corner_radius=8
        )
        self.output_text.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # 为日志文本框添加右键菜单
        self.setup_textbox_context_menu()
        
        # 开始处理消息队列
        self.process_queue()
        
    def update_step_progress(self, step_index, status="waiting"):
        """更新步骤进度"""
        if 0 <= step_index < len(self.steps):
            icon, color_key = STEP_STATUS_CONFIG.get(status, STEP_STATUS_CONFIG["waiting"])
            color = self.colors[color_key]
            
            # 添加步骤状态变化的动画效果
            self.animate_step_change(step_index, icon, color, status)
            
            self.root.update_idletasks()
    
    def start_repair_automatically(self):
        """自动开始修复网络"""
        self.is_repairing = True
        self.log_message("https://github.com/PPPerryPan/network_repair")
        self.log_message("已获取管理员权限，开始自动修复网络...")
        
        repair_thread = threading.Thread(target=self.perform_repair)
        repair_thread.daemon = True
        repair_thread.start()
    
    def log_message(self, message):
        """添加消息到输出框"""
        self.message_queue.put(message)
    
    def process_queue(self):
        """处理消息队列"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                self.output_text.insert(tk.END, message + "\n")
                self.output_text.see(tk.END)
                # CustomTkinter 的 Textbox 更新可能需要 update
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_queue)
    
    def perform_repair(self):
        """执行网络修复操作"""
        try:
            self.log_message("🚀 开始网络修复...")
            
            # 获取以太网适配器
            self.log_message("📡 正在获取网络适配器信息...")
            self.update_step_progress(0, "running")
            self.current_step_index = 0
            adapters = get_ethernet_adapters(log_callback=self.log_message)
            if not adapters:
                self.log_message("❌ 未找到任何以太网适配器")
                self.update_step_progress(0, "error")
                return
            
            self.log_message(f"✅ 找到 {len(adapters)} 个以太网适配器")
            self.update_step_progress(0, "completed")
            
            # 配置网络
            self.log_message("⚙️ 正在配置网络设置...")
            self.update_step_progress(1, "running")
            self.current_step_index = 1
            configure_network(adapters, log_callback=self.log_message)
            self.update_step_progress(1, "completed")
            
            # 设置DNS
            self.log_message("🌐 正在设置DNS为DHCP...")
            self.update_step_progress(2, "running")
            self.current_step_index = 2
            set_dns_to_dhcp(adapters, log_callback=self.log_message)
            self.update_step_progress(2, "completed")
            
            # 刷新网络配置
            self.log_message("🔄 正在刷新网络配置...")
            self.update_step_progress(3, "running")
            self.current_step_index = 3
            refresh_network_config(log_callback=self.log_message)
            self.update_step_progress(3, "completed")
            
            # 显示网络信息
            self.log_message("📊 正在获取网络配置信息...")
            # try:
            #     upload_usage(log_callback=self.log_message)
            # except Exception as e:
            #     self.log_message(f"跳过")
            self.update_step_progress(4, "running")
            self.current_step_index = 4
            display_network_info(log_callback=self.log_message)
            self.update_step_progress(4, "completed")
            
            self.log_message("\n🎉 已完成处理，网络应该恢复正常了 []~(￣▽￣)~*")
            self.log_message("💡 若还是不行，可能使用了 TUN 网卡，或非本机网络问题，请检查网络代理工具配置或联系您的网络管理员。 (＠_＠;)")
            
        except Exception as e:
            self.log_message(f"❌ 修复过程中出现错误: {str(e)}")
            if hasattr(self, 'current_step_index'):
                self.update_step_progress(self.current_step_index, "error")
        finally:
            self.is_repairing = False
            self.root.after(0, self.repair_completed)
    
    def repair_completed(self):
        """修复完成后的UI更新"""
        self.update_step_progress(0, "completed")
        self.update_step_progress(1, "completed")
        self.update_step_progress(2, "completed")
        self.update_step_progress(3, "completed")
        self.update_step_progress(4, "completed")
        
        # 添加庆祝动画
        self.animate_completion()
        
        self.log_message("\n✅ 修复完成，程序将在60秒后自动关闭...")
        self.root.after(60000, self.root.destroy)
    
    def animate_step_change(self, step_index, icon, color, status):
        """为步骤变化添加动画效果"""
        # 更新图标和颜色
        self.step_icons[step_index].configure(text=icon, text_color=color)
        
        # 更新文字颜色
        if status == "running":
            self.step_labels[step_index].configure(text_color=self.colors['primary'], font=ctk.CTkFont(family="Microsoft YaHei UI", size=12, weight="bold"))
        elif status == "completed":
            self.step_labels[step_index].configure(text_color=self.colors['success'])
        elif status == "error":
            self.step_labels[step_index].configure(text_color=self.colors['error'])
        else:
            self.step_labels[step_index].configure(text_color=self.colors['text_secondary'], font=ctk.CTkFont(family="Microsoft YaHei UI", size=12))
        
        # 添加缩放动画
        self.animate_icon_scale(self.step_icons[step_index])
    
    def animate_icon_scale(self, icon_label):
        """图标缩放动画"""
        # 保存原始字体大小
        original_font = icon_label.cget("font")
        
        # 放大动画
        def scale_up():
            icon_label.configure(font=ctk.CTkFont(family="Segoe UI Emoji", size=28))
            self.root.after(100, scale_down)
        
        # 缩小回原始大小
        def scale_down():
            icon_label.configure(font=original_font)
        
        scale_up()
    
    def animate_completion(self):
        """修复完成的庆祝动画"""
        # 让所有完成的步骤图标跳动
        def animate_step_icons():
            for i in range(5):
                for icon in self.step_icons:
                    if icon.cget("text") == "✅":
                        # 保存原始字体
                        original_font = icon.cget("font")
                        # 放大
                        icon.configure(font=ctk.CTkFont(family="Segoe UI Emoji", size=28))
                        self.root.after(100, lambda icon=icon, original_font=original_font: icon.configure(font=original_font))
                self.root.after(200, lambda: None)  # 等待下一帧
        
        # 执行动画
        animate_step_icons()
    
    def setup_textbox_context_menu(self):
        """设置文本框的右键菜单"""
        # 创建右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.colors['surface'], fg=self.colors['text'])
        
        # 添加菜单项
        self.context_menu.add_command(label="复制", command=self.copy_text)
        self.context_menu.add_command(label="粘贴", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="全选", command=self.select_all_text)
        
        # 绑定右键事件
        self.output_text.bind("<Button-3>", self.show_context_menu)
        # 绑定键盘快捷键
        self.output_text.bind("<Control-c>", self.copy_text)
        self.output_text.bind("<Control-v>", self.paste_text)
        self.output_text.bind("<Control-a>", self.select_all_text)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.context_menu.grab_release()
    
    def copy_text(self, event=None):
        """复制选中的文本"""
        try:
            selected_text = self.output_text.get("sel.first", "sel.last")
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            # 没有选中的文本
            pass
    
    def paste_text(self, event=None):
        """粘贴文本"""
        try:
            clipboard_text = self.root.clipboard_get()
            # 在当前光标位置插入文本
            self.output_text.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            # 剪贴板为空
            pass
    
    def select_all_text(self, event=None):
        """全选文本"""
        self.output_text.tag_add(tk.SEL, "1.0", tk.END)
        self.output_text.mark_set(tk.INSERT, "1.0")
        self.output_text.see(tk.INSERT)
        return 'break'
