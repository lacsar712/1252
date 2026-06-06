FROM python:3.11-slim

WORKDIR /app

# 安装 curl 供健康检查使用
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令 - 使用 main:app 而不是 backend.main:app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
