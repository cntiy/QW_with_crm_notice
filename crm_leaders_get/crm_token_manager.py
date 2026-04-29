import time
import threading
import logging
from get_token import get_token

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


class CRMTokenManager:
    def __init__(self, refresh_interval: int = 6600):
        self.refresh_interval = refresh_interval
        self._token_data = None
        self._fetched_at = 0.0
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._refresh_thread = None

    def _fetch(self) -> dict:
        data = get_token()
        if not data or "accessToken" not in data:
            raise ValueError(f"CRM token fetch failed: {data}")
        logging.info("CRM token refreshed")
        return data

    def get_token_data(self) -> dict:
        if self._token_data and time.time() < self._fetched_at + self.refresh_interval:
            return self._token_data
        with self._lock:
            if self._token_data and time.time() < self._fetched_at + self.refresh_interval:
                return self._token_data
            self._token_data = self._fetch()
            self._fetched_at = time.time()
            return self._token_data

    def start_auto_refresh(self):
        self._stop_event.clear()
        self._refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._refresh_thread.start()
        logging.info("CRM token auto-refresh started")

    def stop_auto_refresh(self):
        self._stop_event.set()
        if self._refresh_thread:
            self._refresh_thread.join(timeout=5)

    def _refresh_loop(self):
        while not self._stop_event.is_set():
            self._stop_event.wait(self.refresh_interval)
            if self._stop_event.is_set():
                break
            try:
                with self._lock:
                    self._token_data = self._fetch()
                    self._fetched_at = time.time()
            except Exception as e:
                logging.warning(f"CRM token refresh failed, retry in 60s: {e}")
                self._stop_event.wait(60)


crm_token_mgr = CRMTokenManager(refresh_interval=6600)
