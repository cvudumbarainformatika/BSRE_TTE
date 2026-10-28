from slowapi import Limiter
from slowapi.util import get_remote_address

# Rate limiting 60 requests/minute per IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    headers_enabled=True
)
