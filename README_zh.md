# 网络修复工具

[English Version](README.md)

一个基于Python和CustomTkinter开发的网络修复工具，能够自动检测并修复常见的网络连接问题。

## 功能特点

- 📡 **自动检测适配器**：同时支持以太网和无线局域网(WLAN)适配器
- 🔧 **一键修复**：自动执行完整的网络修复流程
- 📊 **实时进度显示**：清晰展示修复步骤和进度
- 📋 **详细日志**：记录完整的修复过程和结果

## 修复流程

1. **获取适配器**：检测并获取所有可用的网络适配器
2. **重置网卡**：设置IP地址和DNS为DHCP
3. **重置DNS**：清除DNS缓存并重置Winsock
4. **重新联网**：释放并重新获取IP地址
5. **完成**：显示修复结果和当前网络配置

## 安装和使用

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **运行程序**：
   ```bash
   python main.py
   ```
   或直接双击运行编译后的可执行文件

3. **程序会自动**：
   - 请求管理员权限
   - 启动修复流程
   - 显示修复进度和结果

## 开发说明

### 项目结构

```
network_repair/
├── main.py              # 主入口文件
├── gui.py               # GUI界面模块
├── network_utils.py     # 网络操作工具模块
├── admin_utils.py       # 管理员权限工具模块
├── constants.py         # 常量定义模块
├── requirements.txt     # 依赖列表
├── icon.ico             # 应用图标
├── network_repair.spec  # PyInstaller配置文件
├── README.md            # 项目说明文档（英文）
└── README_zh.md         # 项目说明文档（中文）
```

### 主要模块功能

- **main.py**：程序主入口，处理管理员权限请求和启动GUI
- **gui.py**：实现现代化的GUI界面和修复流程控制
- **network_utils.py**：提供网络修复的核心功能
- **admin_utils.py**：检查和请求管理员权限
- **constants.py**：定义修复步骤、主题颜色和状态配置

## 统计功能（可选）

如果需要统计程序的运行次数，可以按照以下步骤开启：

1. 在 `network_utils.py` 中取消注释：
   ```python
   from constants import USAGE_API_URL, USAGE_SOFTWARE_NAME
   # upload_usage(log_callback=self.log_message)
   ```

2. 在 `gui.py` 中取消注释：
   ```python
   # upload_usage(log_callback=self.log_message)
   ```

3. 在 `constants.py` 中取消注释并配置API地址：
   ```python
   USAGE_API_URL = 'http://your-api-url.com/api/usage'
   USAGE_SOFTWARE_NAME = 'network_repair'
   ```

## 注意事项

- 程序必须以管理员权限运行，否则无法执行网络修复操作
- 修复过程中可能需要重启网络连接，请耐心等待
- 部分复杂网络环境可能需要更长的修复时间
- 如果修复失败，可能是由于TUN网卡、网络代理或其他非本机网络问题导致