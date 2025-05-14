# Neo4j-ELK 集成环境

这是一个集成了 Neo4j 和 ELK Stack 的开发环境，适用于服务器安全溯源和攻击路径追踪的知识图谱课题。

---

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

---

## 二、各组件说明

### 1. Neo4j
- 作用：存储服务器、攻击者、攻击路径等知识图谱结构化数据。
- 端口：7474 (HTTP), 7687 (Bolt)
- 连接方式：Python 通过 `neo4j` 驱动，使用 Bolt 协议连接。
- 典型用法：
  - 创建攻击路径：MERGE (source:Server)-[ATTACKED]->(target:Server)
  - 查询攻击链路：MATCH path = (source)-[ATTACKED*]->(target) RETURN path

### 2. Elasticsearch
- 作用：存储安全事件日志，支持全文检索和复杂查询。
- 端口：9200
- 连接方式：Python 通过 `elasticsearch` 驱动，使用 HTTP 认证连接。
- 典型用法：
  - 写入事件：client.index(index=..., document=...)
  - 查询事件：client.search(index=..., body=...)

### 3. Logstash
- 作用：日志收集、格式化、转发到 Elasticsearch。
- 端口：5044
- 典型用法：监听 5044 端口，接收日志并写入 ES。

### 4. Kibana
- 作用：安全事件的可视化分析。
- 端口：5601
- 典型用法：通过 Web UI 查询、展示 Elasticsearch 中的安全事件。

---

## 三、数据流说明

1. **攻击事件采集脚本**（security_trace.py）
   - 记录攻击事件到 Elasticsearch
   - 在 Neo4j 中建立攻击路径
   - 支持攻击路径追踪与事件检索

2. **Logstash**
   - 可接收外部日志（如 Filebeat、系统日志），转发到 Elasticsearch

3. **Kibana**
   - 通过 Web 页面可视化安全事件、攻击链路

---

## 四、快速开始

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

---

## 五、主要脚本说明

### scripts/security_trace.py
- 连接 Neo4j 和 Elasticsearch
- 记录攻击事件到 ES
- 在 Neo4j 中建立攻击路径
- 查询攻击路径和相关事件
- 详细注释见脚本内部

---

## 六、默认账号密码

- Neo4j: 用户名 neo4j / 密码 neo4j123456
- Elasticsearch/Kibana: 用户名 elastic / 密码 elastic123456

---

## 七、注意事项
- 所有服务均为开发环境配置，生产环境请修改默认密码。
- Neo4j/ES 数据均持久化到本地 volume。
- 如需自定义配置，请修改 config/ 目录下相关文件。

---

## 八、环境变量配置

为了方便项目复制和复现，本项目使用环境变量配置连接信息。你可以通过以下方式配置：

1. 在项目根目录创建 `.env` 文件，内容如下：
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123456
ES_HOST=http://localhost:9200
ES_USER=elastic
ES_PASSWORD=elastic123456
```

2. 修改 `docker-compose.yml` 中的服务配置，确保服务地址与 `.env` 文件一致。

3. 运行脚本时，环境变量会自动加载，无需硬编码 IP 地址。 