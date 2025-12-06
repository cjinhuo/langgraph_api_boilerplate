# PHONY 的作用：让 make 命令忽略这些目标，直接执行命令，比如本地有个 dev 文件，有 PHONY 声明后，执行 make dev 会直接执行 dev 命令，而不是执行 dev 文件
.PHONY: dev web stop restart clean api

# 停止所有 langgraph 进程
stop:
	@echo "正在停止 langgraph 服务..."
	@pkill -f "langgraph dev" || true
	@echo "✅ 服务已停止"

web:
	@echo "正在启动 web 开发服务器..."
	cd web && pnpm dev
	
# 启动开发服务器
dev:stop
	@sleep 1
	@echo "正在启动 langgraph 开发服务器..."
	uv run langgraph dev --no-browser --allow-blocking


no_watch_dev: stop
	@sleep 1
	@echo "正在启动 langgraph 开发服务器..."
	uv run langgraph dev --no-browser --allow-blocking --no-reload

# 重启服务
restart: stop
	@sleep 1
	@echo "正在重启 langgraph 开发服务器..."
	uv run langgraph dev --no-browser --allow-blocking

# 启动 api 服务
api:
	@echo "正在启动 api 服务..."
	uv run uvicorn api.main:app --reload