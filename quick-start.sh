#!/bin/bash

# IPMI Dashboard 快速启动脚本 (使用Docker Hub镜像)

echo "🚀 IPMI 管理面板快速启动..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker"
    exit 1
fi

# 创建任务目录
mkdir -p tasks

# 停止已存在的容器
echo "🛑 停止已存在的容器..."
docker stop ipmi-dashboard > /dev/null 2>&1
docker rm ipmi-dashboard > /dev/null 2>&1

# 从Docker Hub拉取最新镜像并运行
echo "📥 拉取最新镜像并启动服务..."
docker run -d \
    --name ipmi-dashboard \
    -p 8080:5000 \
    -v $(pwd)/tasks:/app/tasks \
    -v /etc/localtime:/etc/localtime:ro \
    --restart unless-stopped \
    nemo470/ipmi-dashboard:latest

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if curl -s http://localhost:8080 > /dev/null; then
    echo "✅ IPMI 管理面板启动成功!"
    echo "🌐 访问地址: http://localhost:8080"
    echo ""
    echo "📋 使用说明:"
    echo "   1. 在浏览器中打开 http://localhost:8080"
    echo "   2. 填写IPMI连接信息（主机地址、用户名、密码）"
    echo "   3. 点击'测试连接'验证连接"
    echo "   4. 实时控制: 立即执行开关机操作"
    echo "   5. 定时任务: 设置自动化的定时开关机任务"
    echo "   6. 任务文件: ./tasks/scheduled_tasks.json 保存所有定时任务"
    echo ""
    echo "🛠️  管理命令:"
    echo "   停止服务: docker stop ipmi-dashboard"
    echo "   查看日志: docker logs -f ipmi-dashboard"
    echo "   重启服务: docker restart ipmi-dashboard"
    echo "   删除容器: docker rm -f ipmi-dashboard"
else
    echo "❌ 服务启动失败，请检查日志:"
    echo "   docker logs ipmi-dashboard"
fi 