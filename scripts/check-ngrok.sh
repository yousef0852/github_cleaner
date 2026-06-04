#!/usr/bin/env bash
# Usage: Run this while uvicorn (port 8000) and ngrok (ngrok http 8000) are running.
# It reads the live ngrok URL from the ngrok local API (port 4040) and tests /health.

set -e

echo "1. Checking local API (http://localhost:8000/health)..."
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q 200; then
  echo "   FAIL: API not responding. Start it with:"
  echo "   source .venv/bin/activate && PYTHONPATH=src uvicorn api.main:app --reload"
  exit 1
fi
echo "   OK"

echo "2. Checking ngrok agent (http://127.0.0.1:4040)..."
if ! curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:4040/api/tunnels 2>/dev/null | grep -q 200; then
  echo "   FAIL: ngrok not running. In another terminal run: ngrok http 8000"
  exit 1
fi
echo "   OK"

echo "3. Getting public URL from ngrok..."
# Prefer tunnels API; fallback to endpoints (newer ngrok)
JSON=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null) || JSON=$(curl -s http://127.0.0.1:4040/api/endpoints 2>/dev/null)
PUBLIC_URL=$(echo "$JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    tunnels = d.get('tunnels') or d.get('endpoints', [])
    for t in (tunnels if isinstance(tunnels, list) else []):
        u = t.get('public_url') or t.get('url', '')
        if u.startswith('https://'):
            print(u)
            break
except Exception:
    pass
" 2>/dev/null)
if [ -z "$PUBLIC_URL" ]; then
  echo "   FAIL: Could not read public_url from ngrok API."
  exit 1
fi
echo "   URL: $PUBLIC_URL"

echo "4. Testing public URL /health (with ngrok-skip-browser-warning)..."
RESP=$(curl -s -w "\n%{http_code}" -H "ngrok-skip-browser-warning: true" "$PUBLIC_URL/health")
HTTP_CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')
if [ "$HTTP_CODE" != "200" ]; then
  echo "   FAIL: HTTP $HTTP_CODE"
  echo "$BODY" | head -5
  exit 1
fi
if echo "$BODY" | grep -q "status"; then
  echo "   OK: $BODY"
else
  echo "   Unexpected body (might be ngrok interstitial): $BODY"
fi

echo ""
echo "Done. Use this in Voiceflow as BASE_URL: $PUBLIC_URL"
