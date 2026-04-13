"""Vercel serverless: JSON benchmark of `player` vs each bot (suppresses game prints)."""

import io
import json
import os
import sys
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from RPS import player
from RPS_game import abbey, kris, mrugesh, play, quincy

_GAMES = 350


def _bench():
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


class handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        try:
            rates = _bench()
            self._send_json(
                200,
                {
                    "ok": True,
                    "games_per_bot": _GAMES,
                    "win_rates_percent": rates,
                    "note": "Challenge target is ≥60% per bot (tests use 1000 games).",
                },
            )
        except Exception as e:
            self._send_json(500, {"ok": False, "error": str(e)})
