def get_system_status() -> str:
    """
    Check the computer's hardware status including CPU usage, RAM usage, and Battery level.
    """
    try:
        import psutil
        
        # Lấy thông số CPU (đo trong 1 giây để có độ chính xác)
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Lấy thông số RAM
        ram = psutil.virtual_memory()
        ram_total_gb = ram.total // (1024**3)
        ram_used_gb = ram.used // (1024**3)
        
        # Lấy thông số Pin (nếu là Laptop)
        battery = psutil.sensors_battery()
        
        status = f"System Diagnostics:\n"
        status += f"- CPU Usage: {cpu_usage}%\n"
        status += f"- RAM Usage: {ram.percent}% ({ram_used_gb}GB used out of {ram_total_gb}GB)\n"
        
        if battery:
            plugged = "Plugged In (Charging)" if battery.power_plugged else "On Battery (Discharging)"
            status += f"- Battery Level: {battery.percent}% ({plugged})"
        else:
            status += "- Battery Level: Desktop System (No battery detected)"
            
        return status
    except Exception as e:
        return f"Error retrieving system status: {str(e)}"