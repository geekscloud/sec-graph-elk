# Neo4j 与 ELK 集成指南

## 一、架构总览

本项目采用 Docker Compose 一键部署 Neo4j、Elasticsearch、Kibana、Logstash 四大核心组件，结合 Python 脚本实现安全事件的采集、存储、分析与可视化。

### 架构图（文本版）

```
+-------------------+         +-------------------+
|                   |         |                   |
|   攻击事件采集脚本|  <----> |    Neo4j 图数据库  |
| (security_trace.py)|         |   (攻击路径建模)   |
+-------------------+         +-------------------+
         |                                 ^
         v                                 |
+-------------------+         +-------------------+
|                   |         |                   |
|   Elasticsearch   | <-----> |      Logstash     |
| (安全事件日志存储) |         | (日志收集/转发)    |
+-------------------+         +-------------------+
         |
         v
+-------------------+
|      Kibana       |
| (安全事件可视化)  |
+-------------------+
```

## 二、数据链路说明

1. **攻击事件采集脚本**（security_trace.py）
   - 记录攻击事件到 Elasticsearch
   - 在 Neo4j 中建立攻击路径
   - 支持攻击路径追踪与事件检索

2. **Logstash**
   - 可接收外部日志（如 Filebeat、系统日志），转发到 Elasticsearch

3. **Kibana**
   - 通过 Web 页面可视化安全事件、攻击链路

## 三、可能出现的问题及解决方案

### 1. Neo4j 连接问题

- **问题**：无法连接到 Neo4j 数据库。
- **解决方案**：
  - 检查 Neo4j 服务是否正常运行（`docker-compose ps`）。
  - 确认 Neo4j 的连接配置（URI、用户名、密码）是否正确。
  - 检查防火墙设置，确保 Neo4j 端口（7474、7687）可访问。

### 2. Elasticsearch 连接问题

- **问题**：无法连接到 Elasticsearch。
- **解决方案**：
  - 检查 Elasticsearch 服务是否正常运行（`docker-compose ps`）。
  - 确认 Elasticsearch 的连接配置（地址、用户名、密码）是否正确。
  - 检查防火墙设置，确保 Elasticsearch 端口（9200）可访问。

### 3. Logstash 配置问题

- **问题**：Logstash 无法将日志转发到 Elasticsearch。
- **解决方案**：
  - 检查 Logstash 配置文件（`config/logstash/pipeline/logstash.conf`），确保输出配置正确。
  - 确认 Logstash 服务是否正常运行（`docker-compose ps`）。
  - 查看 Logstash 日志，排查错误信息。

### 4. Kibana 可视化问题

- **问题**：Kibana 无法显示安全事件。
- **解决方案**：
  - 确认 Elasticsearch 中是否有数据（通过 `curl -X GET "http://localhost:9200/security-events-*/_search"`）。
  - 检查 Kibana 索引模式配置，确保已添加 `security-events-*` 索引。
  - 确认 Kibana 服务是否正常运行（`docker-compose ps`）。

## 四、正确的调用链路图示

1. **攻击事件采集脚本**（security_trace.py）：
   - 连接 Neo4j 和 Elasticsearch。
   - 记录攻击事件到 Elasticsearch。
   - 在 Neo4j 中建立攻击路径。

2. **Logstash**：
   - 监听 5044 端口，接收外部日志。
   - 将日志转发到 Elasticsearch。

3. **Kibana**：
   - 通过 Web 页面（http://localhost:5601）访问。
   - 添加索引模式 `security-events-*`。
   - 在"发现（Discover）"页面检索和分析安全事件。

## 五、快速开始

1. 启动所有服务：
```bash
docker-compose up -d
```

2. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

3. 运行安全溯源示例脚本：
```bash
python scripts/security_trace.py
```

## 六、注意事项

- 所有服务均为开发环境配置，生产环境请修改默认密码。
- Neo4j/ES 数据均持久化到本地 volume。
- 如需自定义配置，请修改 config/ 目录下相关文件。 