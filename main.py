import requests
import os
from datetime import datetime, timedelta

DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")

def get_jin10_news():
    url = "https://flash-api.jin10.com/get_flash_list"
    # 模拟更像真实浏览器的请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-app-id": "R67yP4S8319Z7jS3",
        "x-version": "1.0.0",
        "Origin": "https://www.jin10.com",
        "Referer": "https://www.jin10.com/"
    }
    
    beijing_now = datetime.utcnow() + timedelta(hours=8)
    params = {"channel": "-1", "vip": "1", "max_time": beijing_now.strftime("%Y-%m-%d %H:%M:%S")}
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        # 核心诊断逻辑：打印状态码和返回内容的前100个字符
        print(f"DEBUG: 状态码 = {resp.status_code}")
        if resp.status_code != 200:
            print(f"DEBUG: 错误原文 = {resp.text[:200]}")
        
        return resp.json().get("data", [])
    except Exception as e:
        print(f"解析失败原因: {e}")
        # 如果不是 JSON，尝试打印前100个字看看是不是 HTML
        try:
            print(f"DEBUG: 原始返回内容片段 = {resp.text[:100]}")
        except:
            pass
        return []

def main():
    if not DINGTALK_WEBHOOK:
        print("错误: 未配置 DINGTALK_WEBHOOK")
        return
    news_list = get_jin10_news()
    print(f"抓取到 {len(news_list)} 条原始快讯")

if __name__ == "__main__":
    main()
