from collections.abc import Mapping
from urllib.parse import urljoin

import httpx
from fastapi import HTTPException, Request, Response, status


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
}


class UpstreamProxy:
    def __init__(self, *, upstreams: Mapping[str, str], timeout_seconds: float):
        self.upstreams = dict(upstreams)
        self.timeout = httpx.Timeout(timeout_seconds)

    async def forward(self, request: Request, *, service_key: str, path: str = "") -> Response:
        base_url = self.upstreams[service_key].rstrip("/") + "/"
        upstream_path = f"{service_key}/{path}".rstrip("/")
        url = urljoin(base_url, upstream_path)

        headers = {
            name: value
            for name, value in request.headers.items()
            if name.lower() not in HOP_BY_HOP_HEADERS
        }
        body = await request.body()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                upstream_response = await client.request(
                    request.method,
                    url,
                    params=request.query_params,
                    content=body,
                    headers=headers,
                )
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"{service_key} service is unavailable",
            ) from exc

        response_headers = {
            name: value
            for name, value in upstream_response.headers.items()
            if name.lower() not in HOP_BY_HOP_HEADERS
        }
        return Response(
            content=upstream_response.content,
            status_code=upstream_response.status_code,
            headers=response_headers,
            media_type=upstream_response.headers.get("content-type"),
        )
