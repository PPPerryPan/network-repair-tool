"""常量定义模块"""

# 修复步骤列表
REPAIR_STEPS = [
    "获取适配器",
    "重置网卡",
    "重置 DNS",
    "重新联网",
    "完成"
]

# 现代化主题颜色配置 - 支持深色/浅色模式
THEME_COLORS = {
    'light': {
        'primary': '#2563eb',      # 蓝色
        'success': '#16a34a',      # 绿色
        'warning': '#ea580c',      # 橙色
        'error': '#dc2626',        # 红色
        'background': '#f8fafc',   # 浅灰背景
        'surface': '#ffffff',      # 白色表面
        'text': '#1e293b',         # 深灰文字
        'text_secondary': '#64748b' # 次要文字
    },
    'dark': {
        'primary': '#3b82f6',      # 亮蓝色
        'success': '#22c55e',      # 亮绿色
        'warning': '#f97316',      # 亮橙色
        'error': '#ef4444',        # 亮红色
        'background': '#0f172a',   # 深蓝背景
        'surface': '#1e293b',      # 深灰表面
        'text': '#f1f5f9',         # 浅灰文字
        'text_secondary': '#94a3b8' # 次要文字
    }
}

# 步骤状态配置 - 移除直接THEME_COLORS引用
STEP_STATUS_CONFIG = {
    "waiting": ("⏳", "text_secondary"),
    "running": ("⏳", "primary"),
    "completed": ("✅", "success"),
    "error": ("❌", "error")
}

# 使用统计 API 配置
# USAGE_API_URL = 'http://localhost:10001/api/usage'
# USAGE_SOFTWARE_NAME = 'network_repair'

