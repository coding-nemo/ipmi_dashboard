# 更新日志

## [1.0.0] - 2025-06-08

### 新增功能
- 🖥️ **实时IPMI控制**: 电源开关、重启、软关机
- ⏰ **定时任务系统**: 支持一次性、每日、每周的自动化任务
- 📊 **系统监控**: 传感器数据、系统信息、事件日志查看
- 🌐 **现代化Web界面**: 响应式设计，Bootstrap 5 UI
- 📁 **数据持久化**: 任务配置保存在外部文件中
- 🐳 **Docker支持**: 完整的容器化部署方案
- 🔧 **API接口**: RESTful API设计
- 🛡️ **错误处理**: 完善的异常处理和用户反馈

### 技术特性
- Python Flask 后端
- ipmitool 集成
- APScheduler 任务调度
- Bootstrap 5 前端
- Docker 容器化
- 数据卷持久化

### Docker Hub
- 镜像地址: `nemo470/ipmi-dashboard:latest`
- 版本标签: `nemo470/ipmi-dashboard:v1.0` 