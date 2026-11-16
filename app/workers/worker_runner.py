"""EduLingua AI — Telegram Queue Worker CLI Entrypoint.

Starts the background Redis queue consumer with OS signal handling.
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys

from app.bot.setup import create_bot, create_dispatcher
from app.config import get_settings
from app.utils.redis_client import get_redis_client
from app.workers.telegram_worker import TelegramWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("worker_runner")


async def run_worker() -> None:
    """Initialize bot, dispatcher, redis, and run worker loop."""
    settings = get_settings()
    token = settings.telegram_bot_token.get_secret_value()

    bot = create_bot(token)
    redis = get_redis_client()
    if not redis:
        logger.error("Failed to connect to Redis. Exiting.")
        sys.exit(1)

    dp = create_dispatcher(redis=redis)
    worker = TelegramWorker(bot=bot, dp=dp, redis=redis)

    # Setup signals for graceful termination
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, worker.stop)
        except NotImplementedError:
            # On Windows signal handlers might be limited
            pass

    try:
        await worker.start()
    finally:
        await bot.session.close()


def main() -> None:
    """Synchronous entry point."""
    try:
        asyncio.run(run_worker())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Worker process exited.")


if __name__ == "__main__":
    main()
