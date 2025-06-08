#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, flash
import subprocess
import json
import re
import os

app = Flask(__name__)
app.secret_key = 'ipmi_dashboard_secret_key'

class IPMIManager:
    def __init__(self):
        self.default_host = ""
        self.default_user = ""
        self.default_password = ""
    
    def execute_ipmi_command(self, host, user, password, command_args):
        """执行IPMI命令"""
        try:
            if not host or not user or not password:
                return {"success": False, "error": "请填写完整的IPMI连接信息"}
            
            cmd = [
                "ipmitool", "-I", "lanplus", "-H", host, 
                "-U", user, "-P", password
            ] + command_args
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                return {"success": True, "output": result.stdout.strip()}
            else:
                return {"success": False, "error": result.stderr.strip()}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "命令执行超时"}
        except Exception as e:
            return {"success": False, "error": f"执行错误: {str(e)}"}
    
    def get_power_status(self, host, user, password):
        """获取电源状态"""
        return self.execute_ipmi_command(host, user, password, ["power", "status"])
    
    def power_control(self, host, user, password, action):
        """电源控制"""
        valid_actions = ["on", "off", "cycle", "reset", "soft"]
        if action not in valid_actions:
            return {"success": False, "error": f"无效的电源操作: {action}"}
        return self.execute_ipmi_command(host, user, password, ["power", action])
    
    def get_sensor_data(self, host, user, password):
        """获取传感器数据"""
        return self.execute_ipmi_command(host, user, password, ["sensor", "list"])
    
    def get_system_info(self, host, user, password):
        """获取系统信息"""
        return self.execute_ipmi_command(host, user, password, ["fru", "print"])
    
    def get_event_log(self, host, user, password):
        """获取事件日志"""
        return self.execute_ipmi_command(host, user, password, ["sel", "list"])
    
    def clear_event_log(self, host, user, password):
        """清除事件日志"""
        return self.execute_ipmi_command(host, user, password, ["sel", "clear"])

ipmi_manager = IPMIManager()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/power/status', methods=['POST'])
def get_power_status():
    """获取电源状态API"""
    data = request.get_json()
    result = ipmi_manager.get_power_status(
        data.get('host'), 
        data.get('user'), 
        data.get('password')
    )
    return jsonify(result)

@app.route('/api/power/control', methods=['POST'])
def power_control():
    """电源控制API"""
    data = request.get_json()
    result = ipmi_manager.power_control(
        data.get('host'), 
        data.get('user'), 
        data.get('password'),
        data.get('action')
    )
    return jsonify(result)

@app.route('/api/sensors', methods=['POST'])
def get_sensors():
    """获取传感器数据API"""
    data = request.get_json()
    result = ipmi_manager.get_sensor_data(
        data.get('host'), 
        data.get('user'), 
        data.get('password')
    )
    return jsonify(result)

@app.route('/api/system-info', methods=['POST'])
def get_system_info():
    """获取系统信息API"""
    data = request.get_json()
    result = ipmi_manager.get_system_info(
        data.get('host'), 
        data.get('user'), 
        data.get('password')
    )
    return jsonify(result)

@app.route('/api/events', methods=['POST'])
def get_events():
    """获取事件日志API"""
    data = request.get_json()
    result = ipmi_manager.get_event_log(
        data.get('host'), 
        data.get('user'), 
        data.get('password')
    )
    return jsonify(result)

@app.route('/api/events/clear', methods=['POST'])
def clear_events():
    """清除事件日志API"""
    data = request.get_json()
    result = ipmi_manager.clear_event_log(
        data.get('host'), 
        data.get('user'), 
        data.get('password')
    )
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 