# AI 航班搜索测试提效系统

基于 AI 对话的航班搜索与测试辅助工具。通过自然语言交互（如“明天上海到香港的微信H5渠道”），即可快速解析意图、查询多方接口、并支持在无实飞数据时自动生成结构化的 Mock 航班数据供业务测试使用。

本项目深度集成了 **AI Agent 研发协同架构**，从零开始由大模型主导设计、拆解、编码与自我验证迭代。

## 🌟 主要特性 (Key Features)

### 1. 语义化航班解析
系统内置了基于 Anthropic/DeepSeek 模型驱动的意图解析层，支持复杂的自然语言解析：
- **日期智能推算**：理解“明天”、“下周五”、“2月15号”等时间口语。
- **多维度查询支持**：支持单程/往返/中转、指定航司、指定航班号。
- **多乘客与多舱位**：提取不同乘客结构（成人/儿童/婴儿），识别不同舱位（经济舱、头等舱等）。
- **渠道控制**：通过配置字典(`flatType.json`)精确支持各种渠道出票平台（如微信、同程小程序、APP等）查询映射。

### 2. 自适应澄清与容错
- 针对用户提问缺失关键参数时（如没给日期或未指定具体机场），自动抛出携带选项的澄清卡片。
- 支持与用户多回合进行状态记忆 (Session History) 及意图补全。

### 3. 真实数据与 Mock 智能降级
- **实时引擎**：调用直飞、中转二方业务搜索引擎，展示详尽的航段和票价组成。
- **断路 Mock callback**：当查询特定生僻条件或不存在的航班时（或出于特意指定），后端智能拦截并组合构造一份以假乱真的底层航班 Mock 数据返回给前端。

### 4. Agentic 研发协同规范
项目内嵌了专用的 `/orchestrator` 规范库，用以驾驭 AI Coding Agent 的状态：
- 分为 `ALWAYS/`（核心环境常量、加载流、规范）与 `PROGRAMS/`（一个个微型需求闭环）。
- 使得每一次功能迭代（如 `P-2026-007` 渠道映射更新）都具有完整的立项、分析、执行、移交流，杜绝大模型上下文遗忘。

## 📁 项目结构 (Project Structure)

```
flightsearch/
├── AGENTS.md                  # AI 专属提示与运行协议
├── orchestrator/              # AI Agent 研发协作生命周期管理
│   ├── ALWAYS/                # 上下文引导、开发流程预设与常量配置
│   │   ├── BOOT.md            
│   │   ├── CORE.md            
│   │   ├── DEV-FLOW.md        
│   ├── PROGRAMS/              # 单一特性的需求迭代跟踪记录 
│
├── backend/                   # 后端服务 (Python FastAPI)
│   ├── app/
│   │   ├── api/chat.py        # 对话及流式通信核心控制层
│   │   ├── schemas/           # Pydantic 进出参协议模型
│   │   ├── services/          # LLM 意图服务、航班查询、Mock 打底服务
│   │   └── data/              # 城市映射、航司、渠道(flatType)字典
│   ├── main.py                
│   ├── pyproject.toml         
│   └── .env                   
│
├── frontend/                  # 前端层 (Vue 3 + TypeScript)
│   ├── src/
│   │   ├── api/               # Axios 实例模块
│   │   ├── components/        # ChatBox, TripCard, ClarifyCard 等组件积木
│   │   └── stores/            # 基于 Pinia 的聊天流管理
│   └── package.json           
│
└── README.md
```

## 🛠️ 技术栈 (Tech Stack)

**后端 (Backend)**: 
- `Python 3.10+` + `FastAPI` 
- `Anthropic/OpenAI SDK` 
- `httpx` / `Poetry`

**前端 (Frontend)**:
- `Vue 3` + `TypeScript` + `Vite`
- `Pinia` 状态管理
- `Element Plus` 基础组件交互

## 🚀 快速开始 (Getting Started)

### 1. 配置并启动后端

```bash
# cd /Users/qiumiaomiao/Documents/AI/flightsearch/backend
cd backend

# 安装依赖
poetry install

# 配置环境变量（编辑 .env 文件，如果需要调整 LLM 网络可以运行 `.agents/skills` 中的切换脚本）
# 启动后端服务 (热更新模式)
poetry run python main.py
```
> 后端服务运行在 `http://localhost:8000`

### 2. 配置并启动前端

```bash
# cd /Users/qiumiaomiao/Documents/AI/flightsearch/frontend
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```
> 前端服务运行在 `http://localhost:5173`

## ⚙️ 环境配置说明

配置支持同时对接**公网 (DeepSeek)**和**内网 (Authropic Sonnet)** 环境：

**后端配置: `backend/.env`**
```bash
# 二方搜索及Mock网关
SEARCH_API_URL=http://...
MOCK_API_URL=http://...

# LLM 密钥与路由 (支持通过 python scripts 自动切换)
ANTHROPIC_API_KEY=sk-...
ANTHROPIC_API_URL=https://api.deepseek.com
ANTHROPIC_MODEL=deepseek-chat
LLM_PROTOCOL=openai  # 或 anthropic
```

**前端配置: `frontend/.env`**
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

## 📝 系统核心流程 (Architecture Flow)

```mermaid
graph TD
    A[用户输入文本，如: "明晚赴港"] --> B[LLM 意图解析服务]
    B --> C{必填基础信息是否完整？}
    C -- 否 --> D[抛出 Clarify 意图，下发表单选项询问用户]
    D --> E[用户响应补充内容]
    E --> B
    
    C -- 是 --> F[提取 `TripInfo`: 出发、到达、日期、指定渠道等]
    F --> G[调用真实二方航班搜索引擎]
    G --> H{引擎是否返回对应要求航段?}
    H -- 是 --> I[实时渲染 TripCard 真实航班列表]
    
    H -- 否 --> J[触发 Mock Flight 服务级联降级]
    J --> K[基于请求参数自动造出合理的行程图与运价 `flatType`]
    K --> L[渲染带有 Mock 打底标识的航班列表页供测试使用]
```

## 🔧 常见维护操作

- **新增测试渠道**：修改 `backend/app/data/flatType.json` 中的选项，系统热更新后即刻生效，AI 便能自动提取该渠道意图。
- **调整机场数据**：修改 `backend/app/data/city_mapping.json`。
- **测试局域网联调**：修改 `frontend/.env` 的基建 IP 并更新 `backend/app/core/config.py` 中的 `CORS_ORIGINS`。
