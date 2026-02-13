import requests
import os
import json
from datetime import datetime, timedelta

# --- 配置区 ---
# 从系统环境读取 Webhook 地址，保护隐私
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
SENT_LOG_FILE = "sent_news_ids.log"

def get_jin10_news():
    url = "https://flash-api.jin10.com/get_flash_list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-app-id": "R67yP4S8319Z7jS3",
        "x-version": "1.0.0"
    }
    params = {"channel": "-1", "vip": "1", "max_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        return resp.json().get("data", [])
    except:
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
        print("错误: 未配置 DINGTALK_WEBHOOK 环境变量")
        return

    news_list = get_jin10_news()
    sent_ids = load_sent_ids()
    new_sent_list = []
    message_body = ""
    
    for item in news_list:
        data = item.get("data", {})
        content = data.get("content", "")
        news_id = item.get("id")
        
        is_important = data.get("important") == 1
        is_hot = "【沸】" in content or "【爆】" in content
        
        if (is_important or is_hot) and str(news_id) not in sent_ids:
            clean_content = content.replace("<b>", "**").replace("</b>", "**").replace("<br/>", "\n\n")
            message_body += f"---\n\n{clean_content}\n\n"
            new_sent_list.append(str(news_id))

    if message_body:
        send_to_dingtalk(message_body)
        save_sent_ids(new_sent_list)
        print(f"成功推送 {len(new_sent_list)} 条新快讯")
    else:
        print("无符合条件的新快讯")

if __name__ == "__main__":
    main()
