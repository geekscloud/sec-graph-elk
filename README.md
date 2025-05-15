# 安全事件图谱分析系统

> **重要提示**：在使用本系统前，请确保修改 `.env` 文件中的代理配置为您自己的配置，特别是 `LOGSTASH_HOST` 和 `LOGSTASH_TCP_PORT` 这两个参数。使用错误的配置可能导致系统无法正常构建和运行。

基于 ELK Stack 和 Neo4j 的安全事件分析与攻击路径追踪系统。

## 系统架构

系统由以下组件构成：

- **Elasticsearch**: 安全事件日志存储与分析
- **Logstash**: 数据收集、清洗与转换
- **Kibana**: 数据可视化
- **Neo4j**: 攻击路径图谱存储

## 功能特性

### 1. 数据收集与处理
- 多源数据收集（Beats、TCP、HTTP）
- 实时数据清洗与转换
- 地理位置信息解析
- 用户代理解析
- 事件类型标准化

### 2. 安全事件分析
- 攻击类型识别
- 严重程度分类
- 响应状态分析
- 地理位置分析

### 3. 攻击路径追踪
- 攻击源追踪
- 攻击路径可视化
- 多跳攻击分析
- 攻击链还原

## 快速开始

### 环境要求
- Docker
- Docker Compose
- Python 3.8+

### 安装步骤

1. 克隆仓库：
```bash
git clone <repository-url>
cd sec-graph-elk
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件设置必要的环境变量
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 运行测试数据生成器：
```bash
python scripts/generate_test_events.py
```

### 访问服务

- Kibana: http://localhost:5601
- Neo4j Browser: http://localhost:7474
- Logstash API: http://localhost:9600

### 端口配置

系统使用以下默认端口，可通过环境变量修改：

- **Logstash**:
  - Beats 输入: ${LOGSTASH_BEATS_PORT:-5044}
  - TCP 输入: ${LOGSTASH_TCP_PORT:-1514}
  - HTTP 输入: ${LOGSTASH_HTTP_PORT:-8080}

- **Elasticsearch**: 9200
- **Kibana**: 5601
- **Neo4j**: 7474 (HTTP), 7687 (Bolt)

## 数据流程说明

### 测试数据生成与处理流程

1. `generate_test_events.py` 生成测试数据后，通过 TCP 发送到 Logstash（端口 1514）
2. Logstash 接收到数据后，会进行以下处理：
   - 数据清洗和转换
   - 添加地理位置信息
   - 解析用户代理
   - 标准化事件类型
3. 然后 Logstash 会同时将数据输出到两个地方：
   - Elasticsearch：存储详细的事件日志
   - Neo4j：构建攻击关系图

数据流程图：
```
generate_test_events.py
        ↓ (TCP 端口 1514)
    Logstash
        ↓
    ┌─────┴─────┐
    ↓           ↓
Elasticsearch  Neo4j
(事件日志)    (攻击图谱)
```

### 验证数据写入

1. 查看 Elasticsearch 中的数据：
```bash
curl -X GET "http://localhost:9200/security-events-*/_search?pretty" -u elastic:elastic123456
```

2. 在 Neo4j 浏览器中查看攻击关系：
```cypher
MATCH (source:Server)-[r:ATTACKED]->(target:Server)
RETURN source, r, target
LIMIT 10
```

3. 在 Kibana 中查看可视化数据：
   - 访问 http://localhost:5601
   - 创建索引模式 `security-events-*`
   - 查看安全事件仪表板

### 自定义测试数据

如需修改数据生成的方式或内容，可以编辑 `generate_test_events.py` 中的 `generate_event()` 函数。

## 配置说明

### Logstash 配置

Logstash 提供三种数据输入方式：

1. **Beats 输入** (端口 ${LOGSTASH_BEATS_PORT:-5044})
   - 用于接收 Filebeat 等 Beats 系列工具发送的日志

2. **TCP 输入** (端口 ${LOGSTASH_TCP_PORT:-1514})
   - 用于接收其他安全设备通过 TCP 发送的 JSON 格式日志

3. **HTTP 输入** (端口 ${LOGSTASH_HTTP_PORT:-8080})
   - 用于接收通过 HTTP 接口发送的 JSON 格式日志

### 数据处理流程

1. **数据收集**
   - 接收来自不同来源的安全事件数据
   - 支持多种数据格式和协议

2. **数据清洗**
   - 时间戳标准化
   - 字段格式统一
   - 无效数据过滤

3. **数据丰富**
   - IP 地理位置解析
   - 用户代理解析
   - 事件类型标准化

4. **数据输出**
   - 写入 Elasticsearch 进行存储和分析
   - 写入 Neo4j 构建攻击关系图
   - 错误日志记录

## 开发指南

### 添加新的数据处理规则

1. 编辑 `config/logstash/pipeline/advanced_logstash.conf`
2. 在 filter 部分添加新的处理规则
3. 重启 Logstash 服务

### 测试数据生成

使用 `scripts/generate_test_events.py` 生成测试数据：

```bash
python scripts/generate_test_events.py
```

## 监控与维护

### 服务健康检查

```bash
docker-compose ps
```

### 日志查看

```bash
# Logstash 日志
docker-compose logs -f logstash

# Elasticsearch 日志
docker-compose logs -f elasticsearch

# Neo4j 日志
docker-compose logs -f neo4j
```

## 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 