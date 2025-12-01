# MCP 架构说明

## 你的两个MCP配置文件的用途

### 1. `mcp.json` - 外部MCP工具注册
**用途**: 给 Claude Desktop 或其他 MCP 客户端注册 MCP 服务器

```json
{
  "mcpServers": {
    "mcp_tool": {
      "type": "streamable_http",
      "url": "https://mcp.api-inference.modelscope.net/564add6c6f6040/mcp"
    }
  }
}
```

**使用场景**: 当你在 Claude Desktop 中启用这个 MCP 工具后，Claude 可以直接调用这个远程服务器提供的工具。

### 2. `enhance_config.yaml` - 推理管道内部配置
**用途**: 定义你的虚拟女友推理管道如何调用外部服务

```yaml
mcp:
  enabled: true
  services:
    - name: weather_service
      endpoint: https://mcp.api-inference.modelscope.net/564add6c6f6040/mcp
      protocol: rest
      ...
```

**使用场景**: 当推理管道运行时，用来调用 MCP 服务器或其他外部服务获取实时数据。

## 当前的修复（已完成）

### 问题
1. 推理管道的 MCP 客户端 (`src/mcp/mcp_client.py`) 默认只读 JSON 格式的配置
2. 你的实际配置在 `enhance_config.yaml` (YAML 格式)
3. 最小查询长度 threshold 过高 (10字符)，导致短查询未能触发增强

### 修复
1. ✅ 更新 `src/mcp/mcp_config.py` 支持 YAML 和 JSON 格式
2. ✅ 优先加载 `enhance_config.yaml`（如果不存在再加载 `mcp.json`）
3. ✅ 降低 `ENHANCEMENT_MIN_QUERY_LENGTH` 从 10 到 5

## 工作流程

### 用户询问天气时:
```
用户: "北京的天气怎么样?"
  ↓
[推理管道 - _decide_enhancement()]
  - 检查查询长度 (9 ≥ 5) ✓
  - 检查关键词或问号 ✓
  - 决定: 需要增强
  ↓
[推理管道 - _perform_enhancement()]
  - 调用网络搜索 (可选)
  - 调用 MCP 客户端
    ↓
    [MCP 客户端 - fetch()]
      - 加载 enhance_config.yaml
      - 检测 "weather" 域
      - 选择 weather_service
      - 调用 https://mcp.api-inference.modelscope.net/564add6c6f6040/mcp
      - 返回天气数据
    ↓
  - 合并搜索结果和 MCP 结果
  - 生成摘要
  ↓
[模型 - generate_reply()]
  - 使用增强上下文生成回复
  ↓
女友回复: "北京今天天气很好呢! ☀️ ..."
```

## 两个配置文件的关系

```
┌─────────────────────────────────────────┐
│  Claude Desktop (如果配置了 mcp.json)   │
│  可以看到 mcp_tool 工具可用              │
└──────────────┬──────────────────────────┘
               │
               ↓ (Claude Desktop 调用)
┌─────────────────────────────────────────┐
│  MCP 服务器                              │
│  https://mcp.api-inference.modelscope... │
└──────────────┬──────────────────────────┘
               │
               ↑ (推理管道调用)
┌─────────────────────────────────────────┐
│  虚拟女友推理管道                        │
│  使用 enhance_config.yaml 配置          │
│  通过 src/mcp/mcp_client.py 调用        │
└─────────────────────────────────────────┘
```

## 总结

**您的正确用法是：**
- ✅ `mcp.json` - 保留用于 Claude Desktop MCP 工具注册
- ✅ `enhance_config.yaml` - 推理管道使用的实际服务配置
- ✅ `src/mcp/mcp_client.py` - 连接到 MCP 服务器的本地客户端

这样设计的好处：
1. 推理管道独立工作，不依赖外部 MCP 注册
2. Claude Desktop 也可以独立使用相同的 MCP 服务器
3. 两个系统可以各自发展，互不影响
