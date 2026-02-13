import requests
import os
from datetime import datetime, timedelta
import time

# --- 配置区 ---
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
SENT_LOG_FILE = "sent_news_ids.log"

def get_jin10_news():
    url = "https://flash-api.jin10.com/get_flash_list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-app-id": "R67yP4S8319Z7jS3",
        "x-version": "1.0.0"
    }
    
    # 【修复时区】强制使用北京时间 (UTC+8)
    beijing_now = datetime.utcnow() + timedelta(hours=8)
    max_time_str = beijing_now.strftime("%Y-%m-%d %H:%M:%S")
    
    params = {
        "channel": "-1", 
        "vip": "1", 
        "max_time": max_time_str
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        data = resp.json().get("data", [])
        return data
    except Exception as e:
        print(f"请求失败: {e}")
        return []

def load_sent_ids():
    if os.path.exists(SENT_LOG_FILE):
        with open(SENT_LOG_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_sent_ids(new_ids):
    with open(SENT_LOG_FILE, "a") as f:
        for nid in new_ids:
            f.write(f"{nid}\n")

def send_to_dingtalk(content):
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "金十财经汇总",
            "text": f"### 金十财经汇总\n\n{content}"
        }
    }
    requests.post(DINGTALK_WEBHOOK, json=payload)

def main():
    if not DINGTALK_WEBHOOK:
        print("错误: 未配置 DINGTALK_WEBHOOK")
        return

    news_list = get_jin10_news()
    sent_ids = load_sent_ids()
    new_sent_list = []
    message_body = ""
    
    print(f"抓取到 {len(news_list)} 条原始快讯，开始筛选...")

    for item in news_list:
        news_id = str(item.get("id"))
        data = item.get("data", {})
        content = data.get("content", "")
        
        # --- 优化筛选逻辑 ---
        # 1. 重要性标识
        is_important = data.get("important") == 1
        # 2. 关键词匹配（去掉括号增加兼容性）
        is_hot = any(word in content for word in ["爆", "沸", "重磅", "紧急"])
        
        if (is_important or is_hot) and news_id not in sent_ids:
            # 格式化内容
            clean_content = content.replace("<b>", "**").replace("</b>", "**").replace("<br/>", "\n\n")
            message_body += f"---\n\n{clean_content}\n\n"
            new_sent_list.append(news_id)

    if message_body:
        send_to_dingtalk(message_body)
        save_sent_ids(new_sent_list)
        print(f"成功推送 {len(new_sent_list)} 条新快讯")
    else:
        print("无符合条件的新快讯（已过滤重复或无重磅消息）")

if __name__ == "__main__":
    main()
