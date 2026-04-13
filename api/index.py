"""Vercel Python function: top-level ASGI ``app`` (required discovery path)."""

import io
import json
import os
import sys
from contextlib import redirect_stdout

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_GAMES = 350

_CORS_HEADERS = (
    (b"access-control-allow-origin", b"*"),
    (b"access-control-allow-methods", b"GET, OPTIONS"),
    (b"access-control-allow-headers", b"content-type"),
)


def _bench():
    from RPS import player
    from RPS_game import abbey, kris, mrugesh, play, quincy

    out = {}
    for name, bot in (
        ("quincy", quincy),
        ("abbey", abbey),
        ("kris", kris),
        ("mrugesh", mrugesh),
    ):
        buf = io.StringIO()
        with redirect_stdout(buf):
            wr = play(player, bot, _GAMES)
        out[name] = round(wr, 2)
    return out


async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    method = scope.get("method", "GET")

    if method == "OPTIONS":
        await send(
            {
                "type": "http.response.start",
                "status": 204,
                "headers": [
                    (b"content-type", b"text/plain; charset=utf-8"),
                    *_CORS_HEADERS,
                ],
            }
        )
        await send({"type": "http.response.body", "body": b""})
        return

    if method != "GET":
        body = json.dumps({"ok": False, "error": "Method not allowed"}).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": 405,
                "headers": [
                    (b"content-type", b"application/json; charset=utf-8"),
                    *_CORS_HEADERS,
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})
        return

    try:
        body = json.dumps(
            {
                "ok": True,
                "games_per_bot": _GAMES,
                "win_rates_percent": _bench(),
                "note": "Challenge target is ≥60% per bot (tests use 1000 games).",
            }
        ).encode("utf-8")
        status = 200
    except Exception as e:
        body = json.dumps({"ok": False, "error": str(e)}).encode("utf-8")
        status = 500

    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"application/json; charset=utf-8"),
                *_CORS_HEADERS,
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})
