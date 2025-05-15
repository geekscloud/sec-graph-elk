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
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Logstash 配置
LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "localhost")
LOGSTASH_PORT = int(os.getenv("LOGSTASH_TCP_PORT", "1514"))

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

def send_to_logstash(event, max_retries=3, retry_delay=5):
    """发送事件到 Logstash，带重试机制"""
    for attempt in range(max_retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)  # 设置超时时间
                s.connect((LOGSTASH_HOST, LOGSTASH_PORT))
                s.sendall(json.dumps(event).encode() + b'\n')
                logger.info(f"已发送事件: {event['event_type']}")
                return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"发送事件失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
            else:
                logger.error(f"发送事件失败，已达到最大重试次数: {str(e)}")
                return False

def wait_for_logstash(max_attempts=30, delay=2):
    """等待 Logstash 服务就绪"""
    logger.info(f"等待 Logstash 服务就绪 ({LOGSTASH_HOST}:{LOGSTASH_PORT})...")
    for attempt in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((LOGSTASH_HOST, LOGSTASH_PORT))
                logger.info("Logstash 服务已就绪")
                return True
        except Exception:
            if attempt < max_attempts - 1:
                logger.info(f"等待 Logstash 服务... ({attempt + 1}/{max_attempts})")
                time.sleep(delay)
            else:
                logger.error("Logstash 服务未就绪，请检查服务状态")
                return False

def main():
    """主函数：持续生成和发送事件"""
    logger.info(f"开始生成测试事件... (Logstash: {LOGSTASH_HOST}:{LOGSTASH_PORT})")
    
    # 等待 Logstash 服务就绪
    if not wait_for_logstash():
        return
    
    try:
        while True:
            # 生成并发送事件
            event = generate_event()
            if not send_to_logstash(event):
                logger.error("发送事件失败，等待 5 秒后重试...")
                time.sleep(5)
                continue
            
            # 随机等待 1-5 秒
            time.sleep(random.uniform(1, 5))
            
    except KeyboardInterrupt:
        logger.info("停止生成测试事件")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main() 