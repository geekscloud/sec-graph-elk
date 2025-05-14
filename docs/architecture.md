# 安全事件图谱系统架构文档

## 系统架构

本系统采用分布式架构，主要包含以下组件：

### 1. 数据存储层

#### Elasticsearch 集群
- 采用3节点集群部署
- 节点配置：
  - 每个节点分配1GB内存
  - 启用安全认证
  - 启用内存锁定
  - 使用持久化存储
- 集群特性：
  - 自动发现机制
  - 主节点选举
  - 数据分片和复制

#### Neo4j 图数据库
- 支持集群部署（企业版）
- 社区版支持单节点+只读副本
- 内存配置：
  - 页面缓存：2GB
  - 堆内存：2GB
- 安全特性：
  - 启用认证
  - 支持APOC和GDS插件

### 2. 数据处理层

#### Logstash
- 负责数据采集和转换
- 支持多种输入源
- 可配置的数据处理管道
- 与Elasticsearch集群集成

### 3. 可视化层

#### Kibana
- 提供数据可视化界面
- 支持安全事件分析
- 与Elasticsearch集群集成
- 支持用户认证

## 网络架构

- 所有服务通过Docker网络互联
- 使用bridge网络模式
- 服务间通过服务名进行通信

## 生产环境配置

### 环境变量
- ES_PASSWORD: Elasticsearch密码
- ES_USER: Elasticsearch用户名
- NEO4J_USER: Neo4j用户名
- NEO4J_PASSWORD: Neo4j密码

### 持久化存储
- Elasticsearch数据卷：esdata01, esdata02, esdata03
- Neo4j数据卷：neo4j_data

### 高可用性
- 所有服务配置自动重启
- Elasticsearch集群提供数据冗余
- 服务间依赖关系管理

### 安全配置
- Elasticsearch启用X-Pack安全特性
- Neo4j启用认证
- 所有服务使用环境变量管理敏感信息

## 部署说明

1. 准备环境变量文件(.env)：
```bash
ES_PASSWORD=your_secure_password
ES_USER=elastic
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password
```

2. 启动服务：
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. 验证服务：
- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Neo4j: http://localhost:7474

## 注意事项

1. 生产环境部署前请修改默认密码
2. 确保服务器有足够的内存和存储空间
3. 建议配置监控和告警机制
4. 定期备份重要数据
5. 根据实际需求调整内存配置 