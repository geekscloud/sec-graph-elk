#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全事件测试数据生成器
- 生成模拟的安全事件数据
- 通过 TCP 发送到 Logstash
"""

import socket
import json
import random
import time
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logstash 配置
LOGSTASH_HOST = "localhost"
LOGSTASH_PORT = 5000

# 模拟数据配置
ATTACK_TYPES = [
    "SQL_INJECTION",
    "XSS",
    "DDoS",
    "RCE",
    "PHISHING",
    "LATERAL_MOVEMENT"
]

SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def generate_ip():
    """生成随机 IP 地址"""
    return f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"

def generate_event():
    """生成单个安全事件"""
    event = {
        "@timestamp": datetime.now().isoformat(),
        "event_type": random.choice(ATTACK_TYPES),
        "source_ip": generate_ip(),
        "target_ip": generate_ip(),
        "severity": random.choice(SEVERITY_LEVELS),
        "details": f"模拟{random.choice(ATTACK_TYPES)}攻击事件",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "request_method": random.choice(["GET", "POST", "PUT", "DELETE"]),
        "response_code": random.choice([200, 301, 400, 401, 403, 404, 500])
    }
    return event

def send_to_logstash(event):
    """发送事件到 Logstash"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((LOGSTASH_HOST, LOGSTASH_PORT))
            s.sendall(json.dumps(event).encode() + b'\n')
            logger.info(f"已发送事件: {event['event_type']}")
    except Exception as e:
        logger.error(f"发送事件失败: {str(e)}")

def main():
    """主函数：持续生成和发送事件"""
    logger.info("开始生成测试事件...")
    
    try:
        while True:
            # 生成并发送事件
            event = generate_event()
            send_to_logstash(event)
            
            # 随机等待 1-5 秒
            time.sleep(random.uniform(1, 5))
            
    except KeyboardInterrupt:
        logger.info("停止生成测试事件")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main() 