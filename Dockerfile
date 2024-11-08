# 使用官方的 Python 基礎映像
FROM python:3.13-slim

# 設定工作目錄
WORKDIR /app

# 複製 pyproject.toml 和 poetry.lock 文件到工作目錄
COPY pyproject.toml poetry.lock* /app/

# 安裝 Poetry
RUN pip install poetry

# 使用 Poetry 安裝依賴項
RUN poetry install --no-root

# 複製應用程式代碼到工作目錄
COPY . /app

# 暴露應用程式運行的端口
EXPOSE 5000

# 設定環境變數
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 運行應用程式
CMD [ "poetry", "run","flask", "run"]