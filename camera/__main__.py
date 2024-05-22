import asyncio as aio
from aio_pika import connect_robust

from common.topology import create_topology
from common import config

from .producer import produce


async def main():
    conn = await connect_robust(config.RMQ_URI)
    async with conn:
        chan = await conn.channel()
        await create_topology(chan)

        await produce(chan)


if __name__ == "__main__":
    with aio.Runner() as runner:
        runner.run(main())
