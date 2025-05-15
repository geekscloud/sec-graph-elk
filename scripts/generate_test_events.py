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
from datetime import datetime, timedelta
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
    "BRUTE_FORCE",
    "RCE",
    "PHISHING",
    "RANSOMWARE",
    "DATA_EXFILTRATION",
    "LATERAL_MOVEMENT",
    "PRIVILEGE_ESCALATION",
    "SUPPLY_CHAIN",
    "ZERO_DAY_EXPLOIT"
]

SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# 定义受攻击的服务器范围
TARGET_SERVERS = {
    "web_servers": [f"192.168.1.{i}" for i in range(10, 15)],
    "db_servers": [f"192.168.2.{i}" for i in range(20, 23)],
    "auth_servers": [f"192.168.3.{i}" for i in range(30, 32)],
    "app_servers": [f"192.168.4.{i}" for i in range(40, 45)],
    "file_servers": [f"192.168.5.{i}" for i in range(50, 52)]
}

# 定义攻击源IP范围
ATTACK_SOURCES = [
    # 模拟内部攻击
    *[f"192.168.{random.randint(10, 50)}.{random.randint(100, 200)}" for _ in range(5)],
    # 模拟外部攻击
    *[f"{random.randint(1, 223)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(15)]
]

# 定义持续性攻击的状态
ongoing_attacks = []

def generate_ip():
    """生成随机 IP 地址"""
    return random.choice(ATTACK_SOURCES)

def get_target_ip():
    """获取目标IP，控制在特定范围内"""
    server_type = random.choice(list(TARGET_SERVERS.keys()))
    return random.choice(TARGET_SERVERS[server_type])

def start_new_attack():
    """开始一个新的持续性攻击"""
    attack_type = random.choice(ATTACK_TYPES)
    severity = random.choice(SEVERITY_LEVELS)
    # 更严重的攻击持续时间更长
    if severity == "CRITICAL":
        duration = random.randint(10, 30)  # 分钟
    elif severity == "HIGH":
        duration = random.randint(5, 15)
    else:
        duration = random.randint(1, 10)
        
    source_ip = generate_ip()
    
    # 确定攻击目标范围
    if attack_type in ["DDoS", "BRUTE_FORCE"]:
        # 这些攻击类型通常针对单一目标
        target_type = random.choice(["web_servers", "auth_servers"])
        targets = [random.choice(TARGET_SERVERS[target_type])]
    elif attack_type in ["LATERAL_MOVEMENT", "RANSOMWARE"]:
        # 这些攻击类型通常跨多个服务器
        targets = []
        for server_type in random.sample(list(TARGET_SERVERS.keys()), random.randint(2, 3)):
            targets.extend(random.sample(TARGET_SERVERS[server_type], 
                                         min(random.randint(1, 3), len(TARGET_SERVERS[server_type]))))
    else:
        # 其他攻击类型随机选择1-2个目标
        target_type = random.choice(list(TARGET_SERVERS.keys()))
        targets = random.sample(TARGET_SERVERS[target_type], 
                               min(random.randint(1, 2), len(TARGET_SERVERS[target_type])))
    
    # 事件频率 - 严重程度越高，事件越频繁
    if severity == "CRITICAL":
        frequency = random.uniform(0.5, 1.5)  # 每0.5-1.5秒一个事件
    elif severity == "HIGH":
        frequency = random.uniform(1, 3)
    else:
        frequency = random.uniform(2, 5)
    
    attack = {
        "type": attack_type,
        "severity": severity,
        "source_ip": source_ip,
        "targets": targets,
        "started_at": datetime.now(),
        "end_at": datetime.now() + timedelta(minutes=duration),
        "frequency": frequency,
        "last_event": datetime.now() - timedelta(seconds=frequency)  # 确保第一次检查时立即生成事件
    }
    
    ongoing_attacks.append(attack)
    logger.info(f"开始新的攻击: {attack_type} 从 {source_ip} 到 {len(targets)} 个目标，持续 {duration} 分钟")
    return attack

def update_attacks():
    """更新持续性攻击状态，移除过期的攻击"""
    global ongoing_attacks
    current_time = datetime.now()
    
    # 移除过期的攻击
    ongoing_attacks = [attack for attack in ongoing_attacks if attack["end_at"] > current_time]
    
    # 随机决定是否开始新的攻击
    if len(ongoing_attacks) < 3 and random.random() < 0.2:  # 20%概率开始新攻击
        start_new_attack()

def generate_event():
    """生成单个安全事件"""
    update_attacks()
    current_time = datetime.now()
    
    # 如果有持续性攻击，90%的概率从中生成事件
    if ongoing_attacks and random.random() < 0.9:
        # 检查哪些攻击需要生成新事件
        for attack in ongoing_attacks:
            time_since_last = (current_time - attack["last_event"]).total_seconds()
            if time_since_last >= attack["frequency"]:
                attack["last_event"] = current_time
                target_ip = random.choice(attack["targets"])
                
                # 根据攻击类型生成详细信息
                if attack["type"] == "SQL_INJECTION":
                    details = f"检测到SQL注入尝试: 'OR 1=1--'"
                    method = "POST"
                    response = random.choice([200, 400, 500])
                elif attack["type"] == "XSS":
                    details = f"检测到跨站脚本攻击: '<script>alert(document.cookie)</script>'"
                    method = "GET"
                    response = random.choice([200, 400])
                elif attack["type"] == "DDoS":
                    details = f"DDoS攻击检测: SYN洪水，每秒{random.randint(1000, 10000)}个请求"
                    method = "GET"
                    response = random.choice([503, 504, 429])
                elif attack["type"] == "BRUTE_FORCE":
                    details = f"检测到暴力破解尝试: 用户'{random.choice(['admin', 'root', 'administrator'])}'，尝试次数: {random.randint(5, 50)}"
                    method = "POST"
                    response = 401
                elif attack["type"] == "RANSOMWARE":
                    details = f"检测到勒索软件活动: 尝试加密文件，受影响路径: /var/data/{random.choice(['uploads', 'backups', 'customer'])}"
                    method = "PUT"
                    response = random.choice([200, 403])
                elif attack["type"] == "LATERAL_MOVEMENT":
                    details = f"检测到横向移动: 未授权SSH连接尝试"
                    method = "CONNECT"
                    response = random.choice([403, 200])
                else:
                    details = f"模拟{attack['type']}攻击事件: 可疑活动"
                    method = random.choice(["GET", "POST", "PUT"])
                    response = random.choice([200, 400, 401, 403, 500])
                
                event = {
                    "@timestamp": current_time.isoformat(),
                    "event_type": attack["type"],
                    "source_ip": attack["source_ip"],
                    "target_ip": target_ip,
                    "severity": attack["severity"],
                    "details": details,
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "request_method": method,
                    "response_code": response,
                    "attack_id": id(attack),  # 用于关联同一次攻击的多个事件
                    "attack_duration": f"{(current_time - attack['started_at']).total_seconds():.0f}秒"
                }
                return event
    
    # 如果没有生成持续性攻击的事件，则生成随机的单次事件
    event = {
        "@timestamp": datetime.now().isoformat(),
        "event_type": random.choice(ATTACK_TYPES),
        "source_ip": generate_ip(),
        "target_ip": get_target_ip(),
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
                logger.info(f"已发送事件: {event['event_type']} 严重程度: {event['severity']}")
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
        # 开始几个初始攻击
        for _ in range(2):
            start_new_attack()
            
        while True:
            # 生成并发送事件
            event = generate_event()
            if event and not send_to_logstash(event):
                logger.error("发送事件失败，等待 5 秒后重试...")
                time.sleep(5)
                continue
            
            # 随机等待
            time.sleep(random.uniform(0.5, 2))
            
    except KeyboardInterrupt:
        logger.info("停止生成测试事件")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main() 