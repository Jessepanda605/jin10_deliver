import requests
import os
import json
from datetime import datetime, timedelta

# --- 配置区 ---
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
SENT_LOG_FILE = "sent_news_ids.log"

def get_jin10_news():
    # 方案 B：使用金十的公共静态数据接口，更不容易被屏蔽
    url = "https://cdn.jin10.com/data/flash/all.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.jin10.com/"
    }
    
    try:
        # 这个接口返回的是一个大列表
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"DEBUG-状态码: {resp.status_code}")
        
        if resp.status_code != 200:
            return []
            
        return resp.json()
    except Exception as e:
        print(f"DEBUG-抓取异常: {e}")
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
        print("错误: 请检查 GitHub Secrets 里的 DINGTALK_WEBHOOK")
        return

    news_list = get_jin10_news()
    sent_ids = load_sent_ids()
    new_sent_list = []
    message_body = ""
    
    print(f"成功获取 {len(news_list)} 条快讯，开始扫描热点...")

    # 这个接口的数据结构稍有不同
    for item in news_list:
        news_id = str(item.get("id"))
        data = item.get("data", {})
        content = data.get("content", "")
        
        # 筛选逻辑：由于这个接口没有 important 标识，我们全力匹配关键词
        is_hot = any(word in content for word in ["【爆】", "【沸】", "重磅", "紧急", "特朗普"])
        
        if is_hot and news_id not in sent_ids:
            clean_content = content.replace("<b>", "**").replace("</b>", "**").replace("<br/>", "\n\n")
            message_body += f"---\n\n{clean_content}\n\n"
            new_sent_list.append(news_id)

    if message_body:
        send_to_dingtalk(message_body)
        save_sent_ids(new_sent_list)
        print(f"成功推送 {len(new_sent_list)} 条快讯到钉钉")
    else:
        print("当前暂无新的热点快讯")

if __name__ == "__main__":
    main()
