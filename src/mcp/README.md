# MCP (Multi-service Content Provider) Module

MCP模块为虚拟女友项目提供多服务内容提供者功能，用于增强虚拟女友的知识库。

The MCP module provides multi-service content provider functionality to enhance the virtual girlfriend's knowledge base.

## 功能特性 / Features

- **多服务支持** - 支持多个外部服务同时配置
- **智能路由** - 根据域（domain）自动路由到合适的服务
- **优先级管理** - 支持服务优先级和自动故障转移
- **认证支持** - 支持多种认证方式（API Key, Bearer Token, Basic Auth）
- **重试机制** - 内置指数退避重试策略
- **响应标准化** - 统一的响应格式（content, confidence, metadata）
- **启用/禁用** - 全局和单服务级别的启用/禁用控制
- **审计日志** - 完整的请求日志记录
- **协议支持** - REST和gRPC协议支持（gRPC为占位符实现）

## 快速开始 / Quick Start

### 1. 配置服务

编辑 `enhance_config.yaml` 文件配置MCP服务：

```yaml
mcp:
  enabled: true  # 全局启用/禁用
  default_timeout: 5
  default_retries: 3
  
  services:
    - name: weather_service
      enabled: true
      endpoint: https://api.weather.example.com/v1/query
      protocol: rest
      authentication:
        type: api_key
        key: WEATHER_API_KEY  # 环境变量或实际密钥
        header: X-API-Key
      domains:
        - weather
        - forecast
        - temperature
      timeout: 5
      retries: 3
      priority: 1  # 优先级（数字越小优先级越高）
```

### 2. 使用客户端

```python
from mcp import MCPClient

# 初始化客户端
client = MCPClient()

# 查询天气信息
response = client.fetch("weather", "北京的天气怎么样？")

if response.success:
    print(f"内容: {response.content}")
    print(f"置信度: {response.confidence}")
    print(f"服务: {response.service_name}")
    print(f"元数据: {response.metadata}")
else:
    print(f"错误: {response.error}")

# 获取可用域
domains = client.get_available_domains()
print(f"可用域: {domains}")

# 获取服务状态
status = client.get_service_status()
print(f"MCP启用: {status['mcp_enabled']}")
print(f"启用的服务: {status['enabled_services']}/{status['total_services']}")
```

## 配置说明 / Configuration

### 全局配置

- `enabled`: 全局启用/禁用MCP（默认：true）
- `default_timeout`: 默认超时时间（秒，默认：5）
- `default_retries`: 默认重试次数（默认：3）

### 服务配置

每个服务需要配置以下字段：

- `name` (必需): 服务名称，唯一标识符
- `enabled` (必需): 是否启用此服务
- `endpoint` (必需): 服务端点URL
- `protocol` (必需): 协议类型（rest 或 grpc）
- `authentication` (必需): 认证配置
  - `type`: 认证类型（none, api_key, bearer, basic）
  - `key`: 认证密钥（支持环境变量）
  - `header`: 认证头名称（默认：Authorization）
- `domains` (必需): 服务处理的域列表
- `timeout` (可选): 超时时间（继承全局配置）
- `retries` (可选): 重试次数（继承全局配置）
- `priority` (可选): 优先级（数字越小优先级越高，默认：999）

### 认证类型

1. **none** - 无认证
   ```yaml
   authentication:
     type: none
   ```

2. **api_key** - API密钥认证
   ```yaml
   authentication:
     type: api_key
     key: YOUR_API_KEY
     header: X-API-Key
   ```

3. **bearer** - Bearer令牌认证
   ```yaml
   authentication:
     type: bearer
     key: YOUR_TOKEN
     header: Authorization  # 将生成 "Bearer YOUR_TOKEN"
   ```

4. **basic** - Basic认证
   ```yaml
   authentication:
     type: basic
     key: YOUR_BASIC_AUTH
     header: Authorization  # 将生成 "Basic YOUR_BASIC_AUTH"
   ```

## API文档 / API Documentation

### MCPClient

主要客户端类，提供与MCP服务交互的接口。

#### `__init__(config_path: Optional[str] = None)`

初始化MCP客户端。

**参数:**
- `config_path`: 配置文件路径（默认：项目根目录的 enhance_config.yaml）

#### `fetch(domain: str, query: str, **kwargs) -> MCPResponse`

获取指定域的信息。

**参数:**
- `domain`: 查询域（如 'weather', 'news'）
- `query`: 查询内容
- `**kwargs`: 额外参数

**返回:**
- `MCPResponse`: 标准化响应对象

#### `get_available_domains() -> List[str]`

获取所有可用的域。

**返回:**
- 域名列表（已排序）

#### `get_service_status() -> Dict[str, Any]`

获取所有服务的状态。

**返回:**
- 服务状态信息字典

#### `reload_config(config_path: Optional[str] = None)`

重新加载配置文件。

**参数:**
- `config_path`: 配置文件路径

### MCPResponse

标准化响应对象。

**属性:**
- `content` (str): 响应内容
- `confidence` (float): 置信度（0.0 - 1.0）
- `metadata` (Dict): 元数据
- `service_name` (str): 服务名称
- `success` (bool): 是否成功
- `error` (Optional[str]): 错误信息（如果失败）

**方法:**
- `to_dict()`: 转换为字典

## 工作原理 / How It Works

### 1. 服务选择

当调用 `fetch(domain, query)` 时：

1. 检查MCP是否全局启用
2. 查找处理该域的所有已启用服务
3. 按优先级排序（priority字段）
4. 依次尝试每个服务

### 2. 重试机制

- 使用指数退避策略：2^n秒（最多10秒）
- 配置的重试次数后放弃
- 失败后尝试下一个服务

### 3. 故障转移

- 如果优先级高的服务失败，自动尝试优先级低的服务
- 所有服务都失败才返回错误

### 4. 响应标准化

所有服务响应都会被标准化为统一格式：

```python
{
    "content": "响应内容",
    "confidence": 0.85,  # 0.0 - 1.0
    "metadata": {
        "timestamp": "2024-11-23T12:00:00",
        "service": "service_name",
        "data": {...}  # 额外数据
    },
    "service_name": "service_name",
    "success": true,
    "error": null
}
```

## 测试 / Testing

运行MCP测试：

```bash
# 测试配置解析器
.venv/bin/python tests/test_mcp_config.py

# 测试MCP客户端
.venv/bin/python tests/test_mcp_client.py

# 使用pytest运行所有测试
.venv/bin/pytest tests/test_mcp*.py -v
```

测试覆盖：
- ✅ 配置加载和验证
- ✅ 服务选择和路由
- ✅ 认证头构建
- ✅ 优先级和故障转移
- ✅ 重试逻辑
- ✅ 错误处理
- ✅ 响应标准化
- ✅ 全局和单服务启用/禁用
- ✅ 域匹配（大小写不敏感）

## 示例场景 / Example Scenarios

### 场景1: 天气查询

```python
client = MCPClient()
response = client.fetch("weather", "明天北京的天气")

if response.success:
    # 使用响应内容构建女友回复
    girlfriend_reply = f"亲爱的，{response.content} 要记得带伞哦~ 😊"
```

### 场景2: 新闻查询

```python
response = client.fetch("news", "最新科技新闻")

if response.success:
    girlfriend_reply = f"我帮你查了一下，{response.content} 感兴趣吗？💕"
```

### 场景3: 服务离线处理

```python
response = client.fetch("weather", "天气查询")

if not response.success:
    # 优雅降级
    girlfriend_reply = "抱歉呀，现在查不到实时信息呢~ 不过我会一直陪着你的！💕"
```

## 注意事项 / Notes

1. **环境变量**: 配置中以大写字母和下划线命名的key会被视为环境变量
2. **占位符实现**: 当前REST和gRPC调用为占位符实现，返回模拟数据
3. **生产环境**: 在生产环境中需要实现真实的HTTP/gRPC调用
4. **安全性**: 敏感信息（API密钥）应使用环境变量而非硬编码
5. **日志**: 所有请求都会记录到日志，便于审计和调试

## 扩展开发 / Extension Development

### 添加真实HTTP调用

在 `mcp_client.py` 的 `_query_rest_service` 中：

```python
import requests

def _query_rest_service(self, service, query, request_id, **kwargs):
    payload = self._build_rest_payload(query, **kwargs)
    headers = service.authentication.get_auth_header() or {}
    headers['Content-Type'] = 'application/json'
    
    response = requests.post(
        service.endpoint,
        json=payload,
        headers=headers,
        timeout=service.timeout
    )
    response.raise_for_status()
    
    return self._normalize_response(response.json(), service.name)
```

### 添加真实gRPC调用

在 `mcp_client.py` 的 `_query_grpc_service` 中使用 grpcio 库实现真实的gRPC调用。

## 版本历史 / Version History

- **v1.0** (2024-11): 初始实现
  - 多服务支持
  - 智能路由
  - 重试和故障转移
  - 响应标准化
  - 完整测试覆盖

## 许可证 / License

与主项目相同
