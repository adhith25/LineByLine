"""
LineByLine Authentication Layer
Phase 7B — Secure Supabase JWT verification for the Flask backend.

Design principles:
  1. NEVER trust a user ID that comes from the request body.
  2. The ONLY source of truth for user identity is a verified Supabase JWT.
  3. Token verification is centralized here — never duplicated in route handlers.
  4. Decorators provide a clean, reusable API for endpoint protection.

Token flow:
  Frontend  ->  Authorization: Bearer <access_token>
               v
  _extract_bearer_token()
               v
  supabase.auth.get_user(token)   # server-side verification via Supabase
               v
  g.current_user = { id, email, display_name }
               v
  Endpoint uses g.current_user.id  ← 100% trusted, not spoofable
"""

import os
import functools
from typing import Optional, Dict, Any

from flask import request, jsonify, g
from supabase import create_client, Client

_SUPABASE_URL: Optional[str] = os.environ.get("SUPABASE_URL")
_SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase_client: Optional[Client] = None
if _SUPABASE_URL and _SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase_client = create_client(_SUPABASE_URL, _SUPABASE_SERVICE_ROLE_KEY)
    except Exception as _e:
        print(f"[auth] WARNING: Failed to initialise Supabase client: {_e}")
        supabase_client = None
else:
    print(
        "[auth] WARNING: SUPABASE_URL and/or SUPABASE_SERVICE_ROLE_KEY not set. "
        "Protected endpoints will return 503 until configured."
    )


def _extract_bearer_token() -> Optional[str]:
    """Extract and validate the Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    return token or None


def _build_user_info(user_obj: Any) -> Dict[str, Any]:
    """Normalise a Supabase user object into a lean trusted dictionary."""
    user_meta = getattr(user_obj, "user_metadata", None) or {}
    if isinstance(user_meta, dict):
        display_name = user_meta.get("display_name")
    else:
        display_name = None

    return {
        "id": str(user_obj.id),
        "email": getattr(user_obj, "email", None),
        "display_name": display_name,
        "role": getattr(user_obj, "role", None),
    }


def require_auth(view_func):
    """
    Decorator — endpoint requires a valid Supabase Bearer token.

    Returns 401 if:
      - Authorization header missing or malformed
      - Token is expired, revoked, or invalid

    On success, attaches `g.current_user` with the verified user identity.
    """

    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        if not supabase_client:
            return (
                jsonify(
                    {
                        "error": "Server authentication layer is not configured. "
                        "Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
                    }
                ),
                503,
            )

        token = _extract_bearer_token()
        if not token:
            return (
                jsonify(
                    {
                        "error": "Authentication required. Please sign in.",
                        "code": "MISSING_TOKEN",
                    }
                ),
                401,
            )

        try:
            response = supabase_client.auth.get_user(token)
            user = getattr(response, "user", None)
            if not user:
                raise ValueError("No user returned for token")
        except Exception as exc:
            print(f"[auth] Token verification failed: {exc}")
            return (
                jsonify(
                    {
                        "error": "Invalid or expired session. Please sign in again.",
                        "code": "INVALID_TOKEN",
                    }
                ),
                401,
            )

        g.current_user = _build_user_info(user)
        return view_func(*args, **kwargs)

    return wrapper


def optional_auth(view_func):
    """
    Decorator — endpoint ACCEPTS a valid Supabase Bearer token but doesn't require it.

    If a valid token is present:  g.current_user is set
    If no token or invalid token: g.current_user is None  (public mode)

    This lets explain/teach/followup endpoints work for unauthenticated guests
    while still providing verified identity once the user signs in.
    """

    @functools.wraps(view_func)
    def wrapper(*args, **kwargs):
        g.current_user = None
        if not supabase_client:
            return view_func(*args, **kwargs)

        token = _extract_bearer_token()
        if token:
            try:
                response = supabase_client.auth.get_user(token)
                user = getattr(response, "user", None)
                if user:
                    g.current_user = _build_user_info(user)
            except Exception as exc:
                print(f"[auth] Optional token verification skipped: {exc}")
                g.current_user = None

        return view_func(*args, **kwargs)

    return wrapper


def get_current_user_id() -> Optional[str]:
    """
    Safe helper to get the currently-verified user ID.

    NEVER accept `student_id` / `user_id` from request JSON.
    ALWAYS use this function inside protected endpoints to get the actor identity.
    """
    user = getattr(g, "current_user", None)
    if not user:
        return None
    return user.get("id")
