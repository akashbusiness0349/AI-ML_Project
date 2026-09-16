from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence


@dataclass
class RequestMeasurement:
    request_id: str
    latency_ms: float
    status_code: int
    success: bool
    error: str | None
    response: Dict[str, Any] | None


def post_json(
    url: str,
    payload: Dict[str, Any],
    timeout_seconds: float,
) -> RequestMeasurement:

    request_id = str(payload.get("request_id", "unknown"))

    body = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    started = time.perf_counter()

    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout_seconds,
        ) as response:

            raw = response.read().decode("utf-8")
            status_code = response.getcode()

        latency_ms = (time.perf_counter() - started) * 1000

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None

        return RequestMeasurement(
            request_id=request_id,
            latency_ms=latency_ms,
            status_code=status_code,
            success=200 <= status_code < 300,
            error=None if 200 <= status_code < 300 else raw[:500],
            response=parsed,
        )

    except urllib.error.HTTPError as exc:
        latency_ms = (time.perf_counter() - started) * 1000

        try:
            error_body = exc.read().decode("utf-8")
        except Exception:
            error_body = str(exc)

        return RequestMeasurement(
            request_id=request_id,
            latency_ms=latency_ms,
            status_code=exc.code,
            success=False,
            error=error_body[:500],
            response=None,
        )

    except Exception as exc:
        latency_ms = (time.perf_counter() - started) * 1000

        return RequestMeasurement(
            request_id=request_id,
            latency_ms=latency_ms,
            status_code=0,
            success=False,
            error=str(exc),
            response=None,
        )


def run_concurrent_requests(
    url: str,
    records: Sequence[Dict[str, Any]],
    concurrency: int,
    total_requests: int,
    timeout_seconds: float,
) -> List[RequestMeasurement]:

    if concurrency < 1:
        raise ValueError("concurrency must be >= 1")

    if not records:
        raise ValueError("No request records supplied.")

    selected_records = [
        records[index % len(records)]
        for index in range(total_requests)
    ]

    measurements: List[RequestMeasurement] = []

    started = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=concurrency,
        thread_name_prefix="task04-load",
    ) as executor:

        futures: List[Future] = [
            executor.submit(
                post_json,
                url,
                record,
                timeout_seconds,
            )
            for record in selected_records
        ]

        for future in as_completed(futures):
            measurements.append(future.result())

    elapsed_seconds = time.perf_counter() - started

    if elapsed_seconds <= 0:
        elapsed_seconds = 0.000001

    return measurements


def warmup(
    url: str,
    records: Sequence[Dict[str, Any]],
    timeout_seconds: float,
    count: int = 10,
) -> None:

    if not records:
        return

    for index in range(count):
        record = records[index % len(records)]
        post_json(
            url=url,
            payload=record,
            timeout_seconds=timeout_seconds,
        )