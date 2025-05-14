# 安全事件图谱分析系统

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

2. 配置环境变量（可选）：
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

## 配置说明

### Logstash 配置

Logstash 提供三种数据输入方式：

1. **Beats 输入** (端口 5044)
   - 用于接收 Filebeat 等 Beats 系列工具发送的日志

2. **TCP 输入** (端口 5000)
   - 用于接收其他安全设备通过 TCP 发送的 JSON 格式日志

3. **HTTP 输入** (端口 8080)
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