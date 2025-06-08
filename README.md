# IPMI 管理面板

一个基于Web的IPMI管理工具，提供直观的图形界面来管理服务器的IPMI功能。

## 功能特性

- 🖥️ **电源管理**: 远程开机、关机、重启服务器
- ⏰ **定时任务**: 支持一次性、每日、每周的定时开关机任务
- 📊 **传感器监控**: 实时查看温度、电压、风扇等传感器数据
- 📋 **系统信息**: 获取服务器硬件信息
- 📝 **事件日志**: 查看和管理IPMI事件日志
- 🌐 **Web界面**: 现代化的响应式Web界面
- 📁 **任务持久化**: 任务配置保存在文件中，支持外部访问
- 🐳 **Docker部署**: 一键部署，无需复杂配置

## 快速开始

### 使用Docker运行

1. **构建镜像**:
   ```bash
   docker build -t ipmi-dashboard .
   ```

2. **运行容器**:
   ```bash
   docker run -d -p 8080:5000 --name ipmi-dashboard ipmi-dashboard
   ```

3. **访问界面**:
   打开浏览器访问 `http://localhost:8080`

### 使用Docker Compose

1. **启动服务**:
   ```bash
   docker-compose up -d
   ```

2. **停止服务**:
   ```bash
   docker-compose down
   ```

## 使用说明

1. **配置IPMI连接**:
   - 主机地址: 输入目标服务器的IPMI IP地址
   - 用户名: IPMI用户名
   - 密码: IPMI密码

2. **测试连接**:
   点击"测试连接"按钮验证IPMI连接是否正常

3. **电源管理**:
   - 开机: 远程启动服务器
   - 关机: 强制关闭服务器
   - 重启: 重启服务器
   - 软关机: 发送关机信号给操作系统

4. **监控功能**:
   - 传感器数据: 查看温度、电压、风扇转速等
   - 系统信息: 查看硬件配置信息
   - 事件日志: 查看系统事件和错误日志

5. **定时任务**:
   - 一次性任务: 指定具体时间执行
   - 每日任务: 每天在指定时间执行
   - 每周任务: 每周指定日期和时间执行
   - 任务管理: 启用/暂停/删除任务
   - 任务监控: 查看执行历史和结果

## 技术栈

- **后端**: Python Flask
- **前端**: Bootstrap 5 + JavaScript
- **IPMI工具**: ipmitool
- **容器化**: Docker

## 端口和目录说明

- **Web界面**: 8080端口 (映射到容器内5000端口)
- **任务文件目录**: ./tasks (映射到容器内/app/tasks)

## 安全注意事项

- 请确保IPMI网络的安全性
- 建议使用强密码
- 在生产环境中建议配置HTTPS
- 限制访问IP范围

## 故障排除

### 连接失败
- 检查IPMI IP地址是否正确
- 确认IPMI用户名和密码
- 验证网络连通性
- 检查IPMI服务是否启用

### 容器无法启动
```bash
# 查看容器日志
docker logs ipmi-dashboard

# 检查容器状态
docker ps -a
```

## 开发

### 本地开发环境

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **安装ipmitool**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ipmitool
   
   # CentOS/RHEL
   sudo yum install ipmitool
   
   # macOS
   brew install ipmitool
   ```

3. **运行应用**:
   ```bash
   python app.py
   ```

## 许可证

本项目采用MIT许可证。 