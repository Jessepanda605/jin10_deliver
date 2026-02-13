import requests
import os
import time
from datetime import datetime, timedelta

# --- 配置区 ---
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
SENT_LOG_FILE = "sent_news_ids.log"

def get_wscn_news():
    """抓取华尔街见闻快讯"""
    url = "https://api-prod.wallstreetcn.com/apiv1/content/lives"
    params = {
        "channel": "global-channel",
        "client": "pc",
        "limit": "20"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"DEBUG-WSCN状态码: {resp.status_code}")
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("items", [])
        return []
    except Exception as e:
        print(f"抓取华尔街见闻失败: {e}")
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
            "title": "财经快讯汇总",
            "text": f"### 财经重磅快讯\n\n{content}"
        }
    }
    requests.post(DINGTALK_WEBHOOK, json=payload)

def main():
    if not DINGTALK_WEBHOOK:
        print("错误: 钉钉 Webhook 未配置")
        return

    items = get_wscn_news()
    sent_ids = load_sent_ids()
    new_sent_list = []
    message_body = ""
    
    print(f"成功获取 {len(items)} 条快讯，开始筛选...")

    for item in items:
        news_id = str(item.get("id"))
        content_text = item.get("content_text", "")
        # 华尔街见闻的权重标识，通常大于 0 代表重要
        score = item.get("score", 0)
        
        # 筛选逻辑：重要性高，或者包含关键词
        is_important = score > 0
        is_hot = any(word in content_text for word in ["爆", "沸", "重磅", "特朗普", "美联储"])
        
        if (is_important or is_hot) and news_id not in sent_ids:
            # 简单清洗 HTML 标签
            clean_text = content_text.replace("<p>", "").replace("</p>", "\n\n")
            message_body += f"----- \n\n{clean_text}\n\n"
            new_sent_list.append(news_id)

    if message_body:
        send_to_dingtalk(message_body)
        save_sent_ids(new_sent_list)
        print(f"已向钉钉推送 {len(new_sent_list)} 条新快讯")
    else:
        print("暂时没有符合条件的重磅快讯")

if __name__ == "__main__":
    main()
