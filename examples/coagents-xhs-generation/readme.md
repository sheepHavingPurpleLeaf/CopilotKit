# CoAgents 小红书内容生成示例

这个示例展示了一个智能的小红书内容生成应用，使用 CopilotKit 和 LangGraph 构建。

## 功能特性

- 🤖 **智能博主人设生成**：根据产品信息自动生成专属博主人设
- 📝 **小红书笔记创作**：生成符合平台特色的高质量笔记内容
- 🏷️ **热门标签生成**：自动生成提升曝光度的话题标签
- 🔍 **竞品分析搜索**：搜索参考资料和竞品内容
- 🎨 **实时画板展示**：左侧画板实时显示生成内容
- 💬 **智能对话交互**：支持自然语言交互和功能建议

## 项目结构

```
coagents-xhs-generation/
├── agent/                 # Python后端Agent
│   ├── research_canvas/    # 核心逻辑
│   │   ├── langgraph/     # LangGraph工作流
│   │   └── demo.py        # 启动文件
│   ├── pyproject.toml     # Python依赖
│   └── .env              # 环境变量
├── ui/                   # Next.js前端
│   ├── src/app/          # 应用页面
│   ├── src/components/   # React组件
│   ├── package.json      # Node.js依赖
│   └── .env.local        # 前端环境变量
└── readme.md            # 本文档
```

## 快速开始

### 1. 安装后端依赖

**在 `agent/` 目录下：**

```bash
cd agent
poetry install
```

### 2. 配置环境变量

在 `agent/` 目录下创建 `.env` 文件：

```env
# DeepSeek API配置（推荐）
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# 或使用其他兼容API
# OPENAI_API_KEY=your_openai_api_key
# OPENAI_BASE_URL=https://api.openai.com/v1

# 搜索功能（可选）
TAVILY_API_KEY=your_tavily_api_key

# 服务端口
PORT=8000
```

### 3. 启动后端服务

```bash
cd agent
poetry run demo
```

服务将在 `http://localhost:8000` 启动。

### 4. 安装前端依赖

**在 `ui/` 目录下：**

```bash
cd ui
pnpm install
```

### 5. 配置前端环境

在 `ui/` 目录下创建 `.env.local` 文件：

```env
# API配置（与后端保持一致）
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# 后端服务地址
REMOTE_ACTION_URL=http://localhost:8000
```

### 6. 启动前端服务

```bash
cd ui
pnpm run dev
```

前端将在 `http://localhost:3001` 启动（如果3000端口被占用）。

## 使用指南

### 基本工作流程

1. **产品信息录入**
   - 告诉AI你的产品信息："我的产品是火山推理引擎，一款高性能AI推理工具..."

2. **博主人设生成**
   - 系统会自动建议生成博主人设
   - 或手动说："生成博主人设"

3. **笔记内容创作**
   - 说："帮我写笔记"或"创作小红书内容"
   - 系统会同时生成笔记内容和热门标签

4. **查看和优化**
   - 在左侧画板查看完整内容
   - 可以要求修改或生成新的标签

### 支持的功能指令

- **产品信息**："我的产品叫..."、"产品特点是..."
- **人设生成**："生成博主人设"、"创建人设"
- **内容创作**："帮我写笔记"、"创作小红书内容"
- **标签生成**："生成标签"、"添加话题标签"
- **搜索参考**："搜索竞品"、"找些参考资料"

## 技术架构

### 后端技术栈
- **LangGraph**: 工作流编排
- **CopilotKit**: Agent集成框架
- **FastAPI**: Web服务框架
- **DeepSeek/OpenAI**: 大语言模型

### 前端技术栈
- **Next.js 15.4.4**: React框架
- **CopilotKit React**: AI聊天组件
- **Tailwind CSS**: 样式框架
- **TypeScript**: 类型安全

### 核心组件

1. **Router Node**: 意图识别和消息路由
2. **Note Creation Node**: 笔记创作和产品信息处理
3. **Search Node**: 搜索和参考资料获取
4. **Conversation Node**: 普通对话处理

## 开发环境

### 系统要求
- Node.js 18+
- Python 3.12+
- Poetry (Python包管理)
- pnpm (Node.js包管理)

### 版本信息
- Next.js: 15.4.4
- React: 19.0.0
- CopilotKit: 1.9.3
- LangGraph: 0.4.8

## 故障排除

### 常见问题

1. **端口占用**
   - 后端默认使用8000端口
   - 前端会自动寻找可用端口（通常是3001）

2. **API密钥错误**
   - 检查 `.env` 文件中的API密钥配置
   - 确保DeepSeek API密钥有效且有足够额度

3. **依赖安装问题**
   - 使用 `poetry install` 安装Python依赖
   - 使用 `pnpm install` 安装Node.js依赖

4. **工具调用错误**
   - 确保后端服务正常运行
   - 检查网络连接和API调用

### 调试技巧

1. **查看后端日志**
   ```bash
   cd agent
   poetry run demo
   ```

2. **查看前端控制台**
   - 打开浏览器开发者工具
   - 查看Console和Network面板

3. **重启服务**
   ```bash
   # 重启后端
   cd agent && poetry run demo
   
   # 重启前端
   cd ui && pnpm run dev
   ```

## 自定义配置

### 修改模型配置

在 `agent/research_canvas/langgraph/model.py` 中修改模型设置：

```python
def get_model(state: AgentState):
    model_name = state.get("model", "deepseek-chat")
    # 添加你的自定义模型配置
```

### 自定义UI样式

在 `ui/src/app/Main.tsx` 中修改界面样式：

```typescript
style={{
  "--copilot-kit-background-color": "#E0E9FD",
  "--copilot-kit-secondary-color": "#6766FC",
  // 自定义你的颜色主题
}}
```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License