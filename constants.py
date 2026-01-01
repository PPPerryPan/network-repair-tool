"""Constants Definition Module"""

# Repair steps list
REPAIR_STEPS = [
    "Get Adapters",
    "Reset Network Adapter",
    "Reset DNS",
    "Reconnect Network",
    "Complete"
]

# Modern theme color configuration - supports dark/light modes
THEME_COLORS = {
    'light': {
        'primary': '#2563eb',      # Blue
        'success': '#16a34a',      # Green
        'warning': '#ea580c',      # Orange
        'error': '#dc2626',        # Red
        'background': '#f8fafc',   # Light gray background
        'surface': '#ffffff',      # White surface
        'text': '#1e293b',         # Dark gray text
        'text_secondary': '#64748b' # Secondary text
    },
    'dark': {
        'primary': '#3b82f6',      # Bright blue
        'success': '#22c55e',      # Bright green
        'warning': '#f97316',      # Bright orange
        'error': '#ef4444',        # Bright red
        'background': '#0f172a',   # Dark blue background
        'surface': '#1e293b',      # Dark gray surface
        'text': '#f1f5f9',         # Light gray text
        'text_secondary': '#94a3b8' # Secondary text
    }
}

# Step status configuration - removed direct THEME_COLORS reference
STEP_STATUS_CONFIG = {
    "waiting": ("⏳", "text_secondary"),
    "running": ("⏳", "primary"),
    "completed": ("✅", "success"),
    "error": ("❌", "error")
}

# Usage statistics API configuration
# USAGE_API_URL = 'http://localhost:10001/api/usage'
# USAGE_SOFTWARE_NAME = 'network_repair'

