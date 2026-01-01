"""Network Operations Utility Module"""
import subprocess
import time
import wmi
import pythoncom
import requests
# from constants import USAGE_API_URL, USAGE_SOFTWARE_NAME


def get_startupinfo():
    """Get subprocess startup information to hide console window"""
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return startupinfo


def get_ethernet_adapters(log_callback=None):
    """
    Get Ethernet adapter information
    
    Args:
        log_callback: Log callback function for outputting log information
    
    Returns:
        list: List of adapter information, each element contains 'name' and 'description'
    """
    if log_callback:
        log_callback("Getting Ethernet adapter information...")
    
    startupinfo = get_startupinfo()
    
    try:
        result = subprocess.run(
            ["ipconfig", "/all"], 
            capture_output=True, 
            text=True, 
            encoding='gb2312', 
            startupinfo=startupinfo
        )
        output = result.stdout
        
        adapters = []
        current_adapter = None
        adapter_info = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('以太网适配器') or line.startswith('无线局域网适配器'):
                if line.startswith('以太网适配器'):
                    adapter_name = line.replace('以太网适配器', '').replace(':', '').strip()
                else:
                    adapter_name = line.replace('无线局域网适配器', '').replace(':', '').strip()
                current_adapter = adapter_name
                adapter_info[current_adapter] = {'name': adapter_name}
            elif current_adapter and line.startswith('描述'):
                description = line.split(':', 1)[1].strip()
                adapter_info[current_adapter]['description'] = description
                if any(x in current_adapter for x in ['以太网', 'Eth', 'eth', 'WLAN', 'wlan']):
                    adapters.append(adapter_info[current_adapter])
        
        for adapter in adapters:
            if log_callback:
                log_callback(f"  📡 Found adapter: {adapter['name']} ({adapter['description']})")
        
        return adapters
        
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Failed to get adapter information: {str(e)}")
        return []


def configure_network(adapters, log_callback=None):
    """
    Configure network settings (set IP and DNS to DHCP)
    
    Args:
        adapters: List of adapter information
        log_callback: Log callback function
    """
    if log_callback:
        log_callback("Starting network configuration...")
    
    startupinfo = get_startupinfo()
    
    for adapter_info in adapters:
        if log_callback:
            log_callback(f"  🔧 Configuring adapter: {adapter_info['name']}")
        adapter_name = adapter_info['name']
        
        # Set DHCP
        try:
            # Set IP address to DHCP
            result = subprocess.run([
                "netsh", "interface", "ip", "set", "address",
                adapter_name, "source=dhcp"
            ], capture_output=True, text=True, startupinfo=startupinfo)
            
            if result.returncode == 0:
                if log_callback:
                    log_callback(f"    ✅ Set IP address to DHCP successfully")
            else:
                if result.stderr:
                    if log_callback:
                        log_callback(f"    ❌ Failed to set IP address: {result.stderr}")
                else:
                    if log_callback:
                        log_callback(f"    ✅ Set IP address to DHCP successfully")
            
            # Set DNS to DHCP
            result = subprocess.run([
                "netsh", "interface", "ip", "set", "dnsservers",
                adapter_name, "source=dhcp"
            ], capture_output=True, text=True, startupinfo=startupinfo)
            
            if result.returncode == 0:
                if log_callback:
                    log_callback(f"    ✅ Set DNS to DHCP successfully")
            else:
                if result.stderr:
                    if log_callback:
                        log_callback(f"    ❌ Failed to set DNS: {result.stderr}")
                else:
                    if log_callback:
                        log_callback(f"    ✅ Set DNS to DHCP successfully")
                        
        except Exception as e:
            if log_callback:
                log_callback(f"    ❌ Error configuring adapter: {str(e)}")


def set_dns_to_dhcp(adapters, log_callback=None):
    """
    Set DNS to DHCP using WMI
    
    Args:
        adapters: List of adapter information
        log_callback: Log callback function
    """
    if log_callback:
        log_callback("Setting DNS to DHCP...")
    
    try:
        # Initialize COM in child thread
        pythoncom.CoInitialize()
        
        c = wmi.WMI()
        
        for adapter_info in adapters:
            if log_callback:
                log_callback(f"  🌐 Setting DNS for adapter: {adapter_info['name']}")
            for adapter in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                if adapter.Description == adapter_info['description']:
                    result = adapter.SetDNSServerSearchOrder()
                    if result[0] == 0:
                        if log_callback:
                            log_callback(f"    ✅ Successfully set DNS to automatic acquisition")
                    else:
                        if log_callback:
                            log_callback(f"    ❌ Failed to set DNS to automatic acquisition, error code: {result[0]}")
                    break
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Error setting DNS: {str(e)}")
    finally:
        # Clean up COM
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def refresh_network_config(log_callback=None):
    """
    Refresh network configuration
    
    Args:
        log_callback: Log callback function
    """
    startupinfo = get_startupinfo()
    
    if log_callback:
        log_callback("Refreshing DNS cache...")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, startupinfo=startupinfo)
    
    if log_callback:
        log_callback("Releasing IP address...")
    subprocess.run(["ipconfig", "/release"], capture_output=True, startupinfo=startupinfo)
    subprocess.run(["ipconfig", "/release"], capture_output=True, startupinfo=startupinfo)
    subprocess.run(["ipconfig", "/release"], capture_output=True, startupinfo=startupinfo)
    
    time.sleep(5)
    
    if log_callback:
        log_callback("Renewing IP address...")
        log_callback("Running, please wait patiently...")
        log_callback("Computers with complex network environments may take several minutes to load, please wait patiently...")
        log_callback("This is a Windows feature, not a bug, please wait patiently")
    subprocess.run(["ipconfig", "/renew"], capture_output=True, startupinfo=startupinfo)
    
    if log_callback:
        log_callback("Refreshing DNS cache again...")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, startupinfo=startupinfo)
    
    if log_callback:
        log_callback("Resetting Winsock...")
    subprocess.run(["netsh", "winsock", "reset"], capture_output=True, startupinfo=startupinfo)
    
    # Update registry settings to disable proxy
    if log_callback:
        log_callback("Disabling proxy settings...")
    try:
        subprocess.run([
            "reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            "/v", "AutoConfigURL", "/t", "REG_SZ", "/d", "", "/f"
        ], capture_output=True, startupinfo=startupinfo)
        subprocess.run([
            "reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            "/v", "UseAutoDetect", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, startupinfo=startupinfo)
        subprocess.run([
            "reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            "/v", "ProxyEnable", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, startupinfo=startupinfo)
        subprocess.run([
            "reg", "add", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings",
            "/v", "ProxyServer", "/d", "", "/f"
        ], capture_output=True, startupinfo=startupinfo)
        if log_callback:
            log_callback("✅ Proxy settings disabled")
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Failed to disable proxy settings: {str(e)}")
    
    # Additional DNS refresh
    if log_callback:
        log_callback("Repeating DNS refresh...")
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, startupinfo=startupinfo)
    subprocess.run(["netsh", "winsock", "reset"], capture_output=True, startupinfo=startupinfo)


def display_network_info(log_callback=None):
    """
    Display network configuration information
    
    Args:
        log_callback: Log callback function
    """
    if log_callback:
        log_callback("——————Current Network Configuration——————")
    
    startupinfo = get_startupinfo()
    
    try:
        result = subprocess.run(
            ["ipconfig", "/all"], 
            capture_output=True, 
            text=True, 
            encoding='gb2312', 
            startupinfo=startupinfo
        )
        if result.returncode == 0:
            if log_callback:
                log_callback(result.stdout)
        else:
            if log_callback:
                log_callback("❌ Failed to get network configuration information")
    except Exception as e:
        if log_callback:
            log_callback(f"❌ Error displaying network information: {str(e)}")
    
    if log_callback:
        log_callback("————————————")


# def upload_usage(log_callback=None):
#     """
#     Upload usage statistics
#     
#     Args:
#         log_callback: Log callback function
#     """
#     try:
#         data = {'software': USAGE_SOFTWARE_NAME}
#         response = requests.post(USAGE_API_URL, json=data)
#         if log_callback:
#             log_callback(f"Internal network test result: {response.status_code}")
#     except Exception as e:
#         if log_callback:
#             log_callback(f"Failed to upload usage statistics: {str(e)}")

