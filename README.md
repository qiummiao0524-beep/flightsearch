# AI 航班搜索测试提效系统

基于 AI 对话的航班搜索工具，通过自然语言交互快速获取航班数据，支持 Mock 数据生成。

## 项目结构

```
flightsearch/
├── backend/                 # 后端 (Python FastAPI)
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── schemas/        # 数据模型
│   │   ├── services/       # 业务服务
│   │   └── data/           # 静态数据
│   ├── main.py             # 入口文件
│   ├── pyproject.toml      # Poetry 依赖
│   └── .env                # 环境配置
│
├── frontend/               # 前端 (Vue 3 + TypeScript)
│   ├── src/
│   │   ├── api/           # API 调用
│   │   ├── components/    # 组件
│   │   ├── stores/        # 状态管理
│   │   └── types/         # 类型定义
│   ├── package.json
│   └── .env               # 环境配置
│
└── README.md
```

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- Claude API (通过公司内部代理)
- httpx (异步 HTTP 客户端)
- Poetry (依赖管理)

### 前端
- Vue 3 + TypeScript
- Vite
- Pinia (状态管理)
- Element Plus (UI 组件库)
- Axios

## 快速开始

### 1. 配置后端

```bash
cd backend

# 安装依赖
poetry install

# 配置环境变量（编辑 .env 文件）
# 启动后端服务
poetry run python main.py
```

后端服务运行在 http://localhost:8000

### 2. 配置前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务运行在 http://localhost:5173

## 配置说明

### 后端配置 (backend/.env)

```bash
# 二方搜索接口配置
SEARCH_API_URL=http://servicegw.qa.ly.com/gateway/iflight.java.searchfrontapi.uat/v1/search/simplifysearch/
SEARCH_API_TOKEN=696d839f-672e-4476-88db-78234d905c0a

# 二方 Mock 接口配置
MOCK_API_URL=http://dispatchmng.uat.ie.17usoft.com/service/wiki

# Claude API 配置（使用公司内部代理）
ANTHROPIC_API_KEY=sk-xxx
ANTHROPIC_API_URL=https://oneai.17usoft.com/anthropic
ANTHROPIC_MODEL=claude-3-7-sonnet

# 调试模式
DEBUG=true
```

### 前端配置 (frontend/.env)

```bash
# 后端 API 地址
VITE_API_BASE_URL=http://localhost:8000/api
```

## 使用方式

1. 在对话框中输入您的出行需求，例如：
   - "帮我查明天上海到香港的机票"
   - "2月15日北京飞东京，两个大人一个小孩"
   - "查一下 MU5101 航班"

2. AI 助手会解析您的需求，如果信息不完整会询问澄清（如选择出发机场）

3. 信息完整后，系统会调用搜索接口获取航班数据

4. 如果搜索无结果，系统会自动 Mock 数据并重新搜索

## 系统流程

```
用户输入 → LLM 意图解析 → 信息完整？
                              ↓ 否
                         返回澄清问题
                              ↓ 是
                         调用搜索接口（轮询直到 finished=true）
                              ↓
                         有结果？ → 是 → 返回航班列表
                              ↓ 否
                         调用 Mock 接口生成数据
                              ↓
                         再次调用搜索接口
                              ↓
                         返回结果
```

## API 接口

### POST /api/chat
对话接口

请求：
```json
{
  "session_id": "可选，首次对话为空",
  "message": "用户消息",
  "selected_option": "可选，用户选择的澄清选项"
}
```

响应：
```json
{
  "session_id": "会话ID",
  "type": "clarify|result|error",
  "message": "响应消息",
  "trip_info": {
    "travel_type": "OW",
    "departure": {"city": "上海", "code": "PVG"},
    "arrival": {"city": "香港", "code": "HKG"},
    "dep_date": "2026-02-11",
    "passengers": [{"type": "ADT", "count": 1}],
    "cabin_class": "Y"
  },
  "clarify": {
    "field": "departure_code",
    "question": "上海有多个机场，请选择：",
    "options": [
      {"label": "上海虹桥 (SHA)", "value": "SHA"},
      {"label": "上海浦东 (PVG)", "value": "PVG"}
    ]
  },
  "flights": [...],
  "is_mocked": false
}
```

### GET /api/session/{session_id}
获取会话信息

### POST /api/session/new
创建新会话

### GET /health
健康检查

## 开发说明

### 添加新的城市/机场
编辑 `backend/app/data/city_mapping.json`

### 修改 LLM Prompt
编辑 `backend/app/services/llm_service.py` 中的 `SYSTEM_PROMPT`

### 调整搜索请求格式
编辑 `backend/app/services/flight_search.py` 中的 `build_search_request`

搜索接口采用轮询机制：
- 首次请求生成 traceId
- 根据响应中的 sleepTime 等待后再次请求
- 使用相同的 traceId 直到 finished=true

### 调整 Mock 请求格式
编辑 `backend/app/services/flight_mock.py` 中的 `build_mock_request`

Mock 接口请求格式：
```json
{
  "requestBody": "航班数据 JSON 字符串",
  "wikiUrl": "/callBack/entity",
  "version": "1.0.0",
  "serviceName": "callBack"
}
```

## 局域网访问

如需让其他人通过局域网访问测试：

1. 修改 `frontend/.env` 中的 API 地址为局域网 IP
2. 修改 `backend/app/core/config.py` 中的 CORS_ORIGINS 添加局域网地址
3. 前端已配置 `host: '0.0.0.0'`，会自动监听所有网卡

访问地址示例：
- 前端: http://10.181.22.2:5173
- 后端: http://10.181.22.2:8000
