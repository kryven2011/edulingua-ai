"""EduLingua AI — Telegram Webhook Operations CLI.

Production utility to manage and inspect Telegram webhook registrations.

Usage:
    python scripts/manage_webhook.py set      # Register webhook with Telegram
    python scripts/manage_webhook.py check    # Query current webhook status
    python scripts/manage_webhook.py delete   # Remove webhook registration
    python scripts/manage_webhook.py health   # Inspect local server health
"""

from __future__ import annotations

import asyncio
import json
import sys

import httpx

from app.config import get_settings


async def set_webhook(custom_url: str | None = None) -> None:
    """Register public HTTPS webhook endpoint with Telegram."""
    settings = get_settings()
    token = settings.telegram_bot_token.get_secret_value()
    secret = settings.webhook_secret.get_secret_value()

    if custom_url:
        custom_url = custom_url.strip()
        if not custom_url.startswith("http://") and not custom_url.startswith("https://"):
            custom_url = f"https://{custom_url}"
        target_url = f"{custom_url.rstrip('/')}/telegram/webhook"
    else:
        target_url = settings.webhook_url

    if not target_url:
        print("❌ Error: No webhook URL provided and WEBHOOK_BASE_URL is not set.")
        print("Usage: python scripts/manage_webhook.py set [https://your-domain.up.railway.app]")
        return

    print(f"📡 Setting webhook to: {target_url}")
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            json={
                "url": target_url,
                "secret_token": secret,
                "drop_pending_updates": False,
                "allowed_updates": ["message", "callback_query"],
            },
        )
        print(f"HTTP Status: {resp.status_code}")
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


async def check_webhook() -> None:
    """Inspect current Telegram webhook status."""
    settings = get_settings()
    token = settings.telegram_bot_token.get_secret_value()

    print("🔍 Fetching Telegram Webhook Info...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"https://api.telegram.org/bot{token}/getWebhookInfo")
        print(f"HTTP Status: {resp.status_code}")
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


async def delete_webhook() -> None:
    """Deregister webhook from Telegram."""
    settings = get_settings()
    token = settings.telegram_bot_token.get_secret_value()

    print("🗑 Removing Telegram Webhook...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(f"https://api.telegram.org/bot{token}/deleteWebhook")
        print(f"HTTP Status: {resp.status_code}")
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))


async def check_server_health() -> None:
    """Test local or configured server health endpoint."""
    settings = get_settings()
    url = f"http://127.0.0.1:{settings.app_port}/health/detailed"

    print(f"🩺 Probing server health at {url}...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            print(f"HTTP Status: {resp.status_code}")
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Failed to reach health endpoint: {e}")


def main() -> None:
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "check"
    if cmd == "set":
        custom_url = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(set_webhook(custom_url))
    elif cmd == "check":
        asyncio.run(check_webhook())
    elif cmd == "delete":
        asyncio.run(delete_webhook())
    elif cmd == "health":
        asyncio.run(check_server_health())
    else:
        print(f"Unknown command: {cmd}. Available: set, check, delete, health")
        sys.exit(1)


if __name__ == "__main__":
    main()
