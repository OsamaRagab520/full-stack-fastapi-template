import logging

import anyio

from app.core.db import AsyncSessionFactory, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init() -> None:
    async with AsyncSessionFactory() as session:
        await init_db(session)


def main() -> None:
    logger.info("Creating initial data")
    anyio.run(init)
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
