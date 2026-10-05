"""HTTP-клиент ML-сервиса. Если он недоступен — возвращаем None и не ломаем ИС."""
import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()
ML_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000")


class MlClient:
    def __init__(self, base_url: str = ML_URL, timeout: float = 3.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def predict(self, text: str) -> Optional[dict]:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.post(f"{self.base_url}/predict", json={"text": text})
                r.raise_for_status()
                return r.json()
        except Exception as e:
            print(f"[ml_client] ML-сервис недоступен: {e}")
            return None

    def health(self) -> dict:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                r = client.get(f"{self.base_url}/health")
                r.raise_for_status()
                return {"ok": True, "ml": r.json()}
        except Exception as e:
            return {"ok": False, "error": str(e)}