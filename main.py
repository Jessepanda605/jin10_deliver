import requests
import os
from datetime import datetime, timedelta

# --- 配置区 ---
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")
SENT_LOG_FILE = "sent_news_ids.log"

def get_jin10_news():
    # 方案 C：使用金十核心接口，并大幅度增强模拟伪装
    url = "https://flash-api.jin10.com/get_flash_list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Origin": "https://www.jin10.com",
        "Referer": "https://www.jin10.com/",
        "x-app-id": "R67yP4S8319Z7jS3",
        "x-version": "1.0.0"
    }
    
    # 获取北京时间（UTC+8）
    beijing_now = datetime.utcnow() + timedelta(hours=8)
    params = {
        "channel": "-1",
        "vip": "1",
        "max_time": beijing_now.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        # 注意：这里我们换回了 flash-api，但增加了极强的伪装头
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"DEBUG-最新状态码: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"接口返回异常内容片段: {resp.text[:200]}")
            return []
            
        return resp.json().get("data", [])
    except Exception as e:
        print(f"抓取过程出错: {e}")
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
        print("错误: 请确认 GitHub Secrets 已配置 DINGTALK_WEBHOOK")
        return

    news_list = get_jin10_news()
    sent_ids = load_sent_ids()
    new_sent_list = []
    message_body = ""
    
    print(f"成功获取 {len(news_list)} 条快讯数据，准备筛选...")

    for item in news_list:
        data = item.get("data", {})
        content = data.get("content", "")
        news_id = str(item.get("id"))
        
        # 兼容性匹配：重要消息或包含关键词
        is_important = data.get("important") == 1
        is_hot = any(word in content for word in ["爆", "沸", "重磅", "紧急", "特朗普"])
        
        if (is_important or is_hot) and news_id not in sent_ids:
            clean_content = content.replace("<b>", "**").replace("</b>", "**").replace("<br/>", "\n\n")
            message_body += f"---\n\n{clean_content}\n\n"
            new_sent_list.append(news_id)

    if message_body:
        send_to_dingtalk(message_body)
        save_sent_ids(new_sent_list)
        print(f"已发送 {len(new_sent_list)} 条新快讯至钉钉")
    else:
        print("未发现新的热点快讯")

if __name__ == "__main__":
    main()
