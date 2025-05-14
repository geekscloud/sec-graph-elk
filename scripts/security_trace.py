# -*- coding: utf-8 -*-
"""
安全溯源与攻击路径追踪主脚本
- 依赖 Neo4j 作为知识图谱数据库
- 依赖 Elasticsearch 作为安全事件日志存储

主要功能：
1. 记录攻击事件到 Elasticsearch
2. 在 Neo4j 中建立攻击路径关系
3. 查询攻击路径
4. 查询相关安全事件
"""

from neo4j import GraphDatabase  # 导入 Neo4j 驱动
from elasticsearch import Elasticsearch  # 导入 Elasticsearch 驱动
import datetime
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Neo4j 连接配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")  # bolt 协议端口
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")  # 用户名
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j123456")  # 密码

# Elasticsearch 连接配置
ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")  # ES 服务地址
ES_USER = os.getenv("ES_USER", "elastic")  # 用户名
ES_PASSWORD = os.getenv("ES_PASSWORD", "elastic123456")  # 密码

class SecurityTracer:
    def __init__(self):
        # 初始化 Neo4j 连接
        # 通过 bolt 协议连接 Neo4j 图数据库
        self.neo4j_driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        # 初始化 Elasticsearch 连接
        # 通过 http_auth 认证连接 Elasticsearch
        self.es_client = Elasticsearch(
            ES_HOST,
            http_auth=(ES_USER, ES_PASSWORD),
            verify_certs=False  # 开发环境下关闭证书校验
        )

    def create_attack_path(self, source_ip, target_ip, attack_type, timestamp):
        """
        在 Neo4j 中创建攻击路径关系
        :param source_ip: 攻击源 IP
        :param target_ip: 受害者 IP
        :param attack_type: 攻击类型
        :param timestamp: 时间戳
        """
        with self.neo4j_driver.session() as session:
            query = """
            MERGE (source:Server {ip: $source_ip})
            MERGE (target:Server {ip: $target_ip})
            CREATE (source)-[r:ATTACKED {
                type: $attack_type,
                timestamp: $timestamp
            }]->(target)
            """
            session.run(query, {
                "source_ip": source_ip,
                "target_ip": target_ip,
                "attack_type": attack_type,
                "timestamp": timestamp
            })

    def log_security_event(self, event_data):
        """
        记录安全事件到 Elasticsearch
        :param event_data: 事件字典
        """
        try:
            index_name = f"security-events-{datetime.datetime.now().strftime('%Y.%m.%d')}"
            event_data["@timestamp"] = datetime.datetime.now().isoformat()
            response = self.es_client.index(
                index=index_name,
                document=event_data
            )
            print(f"事件已记录到 Elasticsearch: {response['result']}")
        except Exception as e:
            print(f"记录事件时出错: {str(e)}")

    def trace_attack_path(self, target_ip):
        """
        追踪某个目标 IP 的攻击路径
        :param target_ip: 目标 IP
        :return: 路径列表（节点和关系）
        """
        with self.neo4j_driver.session() as session:
            query = """
            MATCH path = (source:Server)-[r:ATTACKED*]->(target:Server {ip: $target_ip})
            RETURN path
            """
            result = session.run(query, {"target_ip": target_ip})
            # 将 Path 对象转换为可序列化结构
            paths = []
            for record in result:
                path = record["path"]
                nodes = [dict(node) for node in path.nodes]
                rels = [dict(rel) for rel in path.relationships]
                paths.append({"nodes": nodes, "relationships": rels})
            return paths

    def get_related_events(self, ip_address, time_range="1d"):
        """
        查询某 IP 在指定时间范围内的安全事件（Elasticsearch）
        :param ip_address: IP 地址
        :param time_range: 时间范围（如 '1d'）
        :return: 查询结果
        """
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"source_ip": ip_address}},
                        {"range": {
                            "@timestamp": {
                                "gte": f"now-{time_range}",
                                "lte": "now"
                            }
                        }}
                    ]
                }
            }
        }
        return self.es_client.search(
            index="security-events-*",
            body=query
        )

def main():
    tracer = SecurityTracer()
    
    # 示例：记录一个攻击事件
    attack_event = {
        "source_ip": "192.168.1.100",
        "target_ip": "192.168.1.200",
        "attack_type": "SQL_INJECTION",
        "severity": "HIGH",
        "details": "Attempted SQL injection attack detected"
    }
    
    try:
        # 1. 在 Neo4j 中创建攻击路径
        tracer.create_attack_path(
            attack_event["source_ip"],
            attack_event["target_ip"],
            attack_event["attack_type"],
            datetime.datetime.now().isoformat()
        )
        print("攻击路径已创建")
        
        # 2. 记录事件到 Elasticsearch
        tracer.log_security_event(attack_event)
        
        # 3. 追踪攻击路径
        attack_paths = tracer.trace_attack_path("192.168.1.200")
        print("攻击路径:", json.dumps(attack_paths, indent=2, ensure_ascii=False))
        
        # 4. 查询相关安全事件
        related_events = tracer.get_related_events("192.168.1.100")
        print("相关事件:", json.dumps(related_events, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"执行过程中出错: {str(e)}")

if __name__ == "__main__":
    main() 