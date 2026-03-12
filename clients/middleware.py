import time
from collections import defaultdict, deque

from django.http import JsonResponse


class SimpleRateLimitMiddleware:
    """
    Very small in-memory rate limit for public POST endpoints.
    Not suitable for multi-instance production without shared storage.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.window_seconds = 60
        self.max_requests = 20
        self.bucket = defaultdict(deque)

    def __call__(self, request):
        if request.method == "POST" and request.path in {"/apply/"}:
            now = time.time()
            key = request.META.get("REMOTE_ADDR", "unknown")
            q = self.bucket[key]
            while q and now - q[0] > self.window_seconds:
                q.popleft()
            if len(q) >= self.max_requests:
                return JsonResponse(
                    {"detail": "Too many requests. Try later."},
                    status=429,
                )
            q.append(now)
        return self.get_response(request)
