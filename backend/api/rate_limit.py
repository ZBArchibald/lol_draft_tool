import math
import time
from collections import deque

from fastapi import Request
from fastapi.responses import JSONResponse

from backend.core.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS

# Sliding-window limiter, kept in memory: client IP -> timestamps of its recent requests.
#
# In-memory state is only accurate because Cloud Run runs with --max-instances 1 (see
# deploy.yml). With more than one instance each would keep its own counts and the real limit
# would be N times higher; at that point move this to Redis or a Cloud Armor rule. State also
# resets when the instance scales to zero, which is fine for an abuse guard.
#
# No lock is needed: the middleware below has no `await` between reading and writing these
# structures, so the event loop can't interleave two requests in the middle of a check.
_recent_requests: dict[str, deque] = {}

# Idle IPs would otherwise stay in the dict forever; sweep them out this often.
_SWEEP_INTERVAL_SECONDS = 300
_last_sweep = time.monotonic()


def _client_ip(request: Request) -> str:
    # Cloud Run's front end appends the real client IP to the END of X-Forwarded-For. Anything
    # a caller puts earlier in the header is spoofable, so take the last entry, not the first.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"


def _sweep_idle_clients(now: float) -> None:
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    idle = []
    for ip, timestamps in _recent_requests.items():
        if not timestamps or timestamps[-1] <= cutoff:
            idle.append(ip)
    for ip in idle:
        del _recent_requests[ip]


async def rate_limit_middleware(request: Request, call_next):
    global _last_sweep

    # Only guard the API itself. OPTIONS is the browser's CORS preflight, which carries no
    # real work and shouldn't eat into someone's budget.
    if not request.url.path.startswith("/api/") or request.method == "OPTIONS":
        return await call_next(request)

    now = time.monotonic()

    if now - _last_sweep > _SWEEP_INTERVAL_SECONDS:
        _sweep_idle_clients(now)
        _last_sweep = now

    ip = _client_ip(request)
    if ip not in _recent_requests:
        _recent_requests[ip] = deque()
    timestamps = _recent_requests[ip]

    # Drop timestamps that have aged out of the window (oldest are on the left).
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    while timestamps and timestamps[0] <= cutoff:
        timestamps.popleft()

    if len(timestamps) >= RATE_LIMIT_REQUESTS:
        # The oldest request leaving the window is what frees up a slot.
        retry_after = max(1, math.ceil(timestamps[0] + RATE_LIMIT_WINDOW_SECONDS - now))
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please slow down and try again shortly."},
            headers={"Retry-After": str(retry_after)},
        )

    timestamps.append(now)
    return await call_next(request)
