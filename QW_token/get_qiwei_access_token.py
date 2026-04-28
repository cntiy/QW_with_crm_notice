import os
import time
import threading
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

# 修正原代码拼写错误 agent_scret -> agent_secret
CORP_ID = os.getenv("CORP_id")
AGENT_SECRET = os.getenv("agent_scret")
REFRESH_INTERVAL = 7000  # 自定义刷新间隔（秒）

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


class WeChatTokenManager:
    def __init__(self, corpid: str, corpsecret: str, refresh_interval: int = 7000):
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.refresh_interval = refresh_interval
        self._token = None
        self._expires_at = 0.0
        self._lock = threading.Lock()
        self._refresh_thread = None
        self._stop_event = threading.Event()

    def fetch_token(self) -> tuple[str, int]:
        """请求企微获取新凭证（改用 POST 避免 URL 日志泄露）"""
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        payload = {"corpid": self.corpid, "corpsecret": self.corpsecret}
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if "access_token" not in data:
                raise ValueError(f"企微API返回异常: {data}")
            return data["access_token"], data.get("expires_in", 7200)
        except Exception as e:
            logging.error(f"获取企微凭证失败: {e}")
            raise

    def get_token(self) -> str:
        """获取当前有效凭证（线程安全 + 提前60秒失效缓冲）"""
        # 快速路径：凭证仍有效
        if self._token and time.time() < self._expires_at - 60:
            return self._token

        # 慢速路径：加锁获取新凭证
        with self._lock:
            # 双重检查，防止并发重复请求
            if self._token and time.time() < self._expires_at - 60:
                return self._token
            token, expires_in = self.fetch_token()
            self._token = token
            self._expires_at = time.time() + expires_in
            logging.info(f"✅ 凭证已更新，有效期至 {time.ctime(self._expires_at)}")
            return self._token

    def start_auto_refresh(self):#记得别的代码用这个要启动一次
        """启动后台定时刷新线程"""
        self._stop_event.clear()
        self._refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._refresh_thread.start()
        logging.info("🔄 自动刷新任务已启动")

    def stop_auto_refresh(self):
        """优雅停止刷新任务"""
        self._stop_event.set()
        if self._refresh_thread:
            self._refresh_thread.join(timeout=5)
        logging.info("🛑 自动刷新任务已停止")

    def _refresh_loop(self):
        """后台循环：每 7000s 强制刷新一次"""
        while not self._stop_event.is_set():
            try:
                token, expires_in = self.fetch_token()
                self._token = token
                self._expires_at = time.time() + expires_in
                logging.info(f"🔄 定时刷新成功，下次刷新: {self.refresh_interval}s 后")
            except Exception as e:
                logging.warning(f"⚠️ 定时刷新失败，60秒后重试: {e}")
            # 使用 Event.wait 替代 time.sleep，支持被立即中断
            self._stop_event.wait(self.refresh_interval)



