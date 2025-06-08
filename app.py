#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, flash
import subprocess
import json
import re
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
import uuid
import threading

app = Flask(__name__)
app.secret_key = 'ipmi_dashboard_secret_key'

# 确保任务目录存在
TASKS_DIR = '/app/tasks'
TASKS_FILE = os.path.join(TASKS_DIR, 'scheduled_tasks.json')
os.makedirs(TASKS_DIR, exist_ok=True)

class TaskManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.tasks = {}
        self.load_tasks()
        
    def load_tasks(self):
        """从文件加载任务"""
        try:
            if os.path.exists(TASKS_FILE):
                with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', {})
                    # 重新添加任务到调度器
                    for task_id, task_info in self.tasks.items():
                        if task_info['status'] == 'active':
                            self._schedule_task(task_id, task_info)
        except Exception as e:
            print(f"加载任务失败: {e}")
            self.tasks = {}
    
    def save_tasks(self):
        """保存任务到文件"""
        try:
            data = {
                'tasks': self.tasks,
                'last_updated': datetime.now().isoformat()
            }
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存任务失败: {e}")
    
    def add_task(self, host, user, password, action, schedule_type, schedule_config, name=""):
        """添加定时任务"""
        task_id = str(uuid.uuid4())
        task_info = {
            'id': task_id,
            'name': name or f"{action} 任务",
            'host': host,
            'user': user,
            'password': password,
            'action': action,
            'schedule_type': schedule_type,
            'schedule_config': schedule_config,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_run': None,
            'run_count': 0
        }
        
        self.tasks[task_id] = task_info
        self._schedule_task(task_id, task_info)
        self.save_tasks()
        return task_id
    
    def _schedule_task(self, task_id, task_info):
        """安排任务执行"""
        try:
            if task_info['schedule_type'] == 'once':
                # 一次性任务
                run_date = datetime.fromisoformat(task_info['schedule_config']['datetime'])
                trigger = DateTrigger(run_date=run_date)
            elif task_info['schedule_type'] == 'daily':
                # 每日任务
                time_str = task_info['schedule_config']['time']
                hour, minute = map(int, time_str.split(':'))
                trigger = CronTrigger(hour=hour, minute=minute)
            elif task_info['schedule_type'] == 'weekly':
                # 每周任务
                time_str = task_info['schedule_config']['time']
                hour, minute = map(int, time_str.split(':'))
                day_of_week = task_info['schedule_config']['day_of_week']
                trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
            else:
                return False
            
            self.scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                args=[task_id],
                id=task_id,
                replace_existing=True
            )
            return True
        except Exception as e:
            print(f"安排任务失败: {e}")
            return False
    
    def _execute_task(self, task_id):
        """执行任务"""
        if task_id not in self.tasks:
            return
        
        task_info = self.tasks[task_id]
        try:
            # 执行IPMI命令
            result = ipmi_manager.power_control(
                task_info['host'],
                task_info['user'], 
                task_info['password'],
                task_info['action']
            )
            
            # 更新任务信息
            task_info['last_run'] = datetime.now().isoformat()
            task_info['run_count'] += 1
            task_info['last_result'] = result
            
            # 如果是一次性任务，执行后设为完成
            if task_info['schedule_type'] == 'once':
                task_info['status'] = 'completed'
            
            self.save_tasks()
            print(f"任务 {task_id} 执行完成: {result}")
            
        except Exception as e:
            task_info['last_run'] = datetime.now().isoformat()
            task_info['last_result'] = {"success": False, "error": str(e)}
            self.save_tasks()
            print(f"任务 {task_id} 执行失败: {e}")
    
    def remove_task(self, task_id):
        """删除任务"""
        if task_id in self.tasks:
            try:
                self.scheduler.remove_job(task_id)
            except:
                pass
            del self.tasks[task_id]
            self.save_tasks()
            return True
        return False
    
    def toggle_task(self, task_id):
        """启用/禁用任务"""
        if task_id in self.tasks:
            task_info = self.tasks[task_id]
            if task_info['status'] == 'active':
                task_info['status'] = 'paused'
                try:
                    self.scheduler.remove_job(task_id)
                except:
                    pass
            else:
                task_info['status'] = 'active'
                self._schedule_task(task_id, task_info)
            self.save_tasks()
            return True
        return False
    
    def get_tasks(self):
        """获取所有任务"""
        return dict(self.tasks)

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
task_manager = TaskManager()

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

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """获取所有定时任务"""
    tasks = task_manager.get_tasks()
    return jsonify({"success": True, "tasks": tasks})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """添加定时任务"""
    data = request.get_json()
    
    # 验证必需字段
    required_fields = ['host', 'user', 'password', 'action', 'schedule_type', 'schedule_config']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"success": False, "error": f"缺少必需字段: {field}"})
    
    try:
        task_id = task_manager.add_task(
            host=data['host'],
            user=data['user'], 
            password=data['password'],
            action=data['action'],
            schedule_type=data['schedule_type'],
            schedule_config=data['schedule_config'],
            name=data.get('name', '')
        )
        return jsonify({"success": True, "task_id": task_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def remove_task(task_id):
    """删除定时任务"""
    if task_manager.remove_task(task_id):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "任务不存在"})

@app.route('/api/tasks/<task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """启用/禁用定时任务"""
    if task_manager.toggle_task(task_id):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "任务不存在"})

@app.route('/api/tasks/file', methods=['GET'])
def get_tasks_file():
    """获取任务文件内容"""
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({"success": True, "content": content})
        else:
            return jsonify({"success": True, "content": "{}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 