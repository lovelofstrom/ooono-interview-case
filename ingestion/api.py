import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PAGE_SIZE = 1000  # API maximum
TIMEOUT = (
    30  # First call can take ~20 seconds. 30 seconds so it contains extra padding.
)


class ApiClient:
    def __init__(self, base_url: str, client_id: str, client_secret: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.token: str | None = None
        self.token_expires_at = 0.0

        # Retry rate limits (429) and temporary server errors (5xx), waiting longer each time.
        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def _get_token(self) -> str:
        # Tokens expire after 15 minutes. Fetch a new one a minute before that.
        if self.token is None or time.time() > self.token_expires_at - 60:
            response = self.session.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            body = response.json()
            self.token = body["access_token"]
            self.token_expires_at = time.time() + body["expires_in"]
        return self.token

    def fetch_all(self, path: str, params: dict | None = None) -> list[dict]:
        """Fetch every record from an endpoint, following next_cursor page by page."""
        params = dict(
            params or {}
        )
        params["limit"] = PAGE_SIZE
        records = []
        while True:
            response = self.session.get(
                f"{self.base_url}{path}",
                params=params,
                headers={"Authorization": f"Bearer {self._get_token()}"},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            page = response.json()
            records.extend(page["data"])
            if not page["data"] or not page.get("next_cursor"):
                return records
            params["cursor"] = page["next_cursor"]
