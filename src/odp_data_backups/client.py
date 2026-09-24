from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class CartoError(RuntimeError):
    """Raised when Carto rejects a query or returns an invalid response."""


class CartoClient:
    def __init__(
        self,
        endpoint: str = "https://phl.carto.com/api/v2/sql",
        *,
        timeout: float = 120,
        retries: int = 4,
        session: requests.Session | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self.session = session or requests.Session()
        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=1,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"POST"}),
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def query(self, sql: str) -> dict[str, Any]:
        try:
            response = self.session.post(
                self.endpoint,
                data={"q": sql},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise CartoError(f"Carto request failed for query:\n{sql}\n\n{exc}") from exc

        if "error" in payload or "rows" not in payload:
            detail = payload.get("error", payload)
            raise CartoError(f"Carto rejected query:\n{sql}\n\n{detail}")
        return payload

    def iter_query(self, sql: str, *, page_size: int = 25_000) -> Iterator[list[dict[str, Any]]]:
        if page_size < 1:
            raise ValueError("page_size must be at least 1")

        offset = 0
        while True:
            payload = self.query(f"{sql} LIMIT {page_size} OFFSET {offset}")
            rows = payload["rows"]
            if not rows:
                return
            yield rows
            if len(rows) < page_size:
                return
            offset += len(rows)
