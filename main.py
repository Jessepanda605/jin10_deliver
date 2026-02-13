import requests
import os
from datetime import datetime, timedelta

DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK")

def get_jin10_news():
    url = "https://flash-api.jin10.com/get_flash_list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-app-id": "R67yP4S8319Z7jS3",
        "x-version": "1.0.0"
    }
    
    beijing_now = datetime.utcnow() + timedelta(hours=8)
    params = {"channel": "-1", "vip": "1", "max_time": beijing_now.strftime("%Y-%m-%d %H:%M:%S")}
    
    print("--- 诊断开始 ---")
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        # 强制打印状态码
        print(f"诊断-HTTP状态码: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"诊断-错误网页内容: {resp.text[:300]}")
            return []
            
        return resp.json().get("data", [])
    except Exception as e:
        print(f"诊断-系统级错误: {e}")
        return []

def main():
    if not DINGTALK_WEBHOOK:
        print("错误: GitHub Secrets 里的 DINGTALK_WEBHOOK 没配置好")
        return
    news_list = get_jin10_news()
    print(f"结果: 抓取到 {len(news_list)} 条快讯")
    print("--- 诊断结束 ---")

if __name__ == "__main__":
    main()
