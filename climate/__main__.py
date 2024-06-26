import asyncio as aio
import json
import functools

from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractExchange

from common import config
from common.topology import create_topology


async def handler(msg: AbstractIncomingMessage, exch: AbstractExchange):
    async with msg.process():
        data = json.loads(msg.body.decode())
        print(f"climate получил сообщение: {data=}")
        temperature = data["temperature"]
        print(f"Меняем температуру выращивания: {temperature=}")


async def main():
    conn = await connect_robust(config.RMQ_URI)
    async with conn:
        chan = await conn.channel()
        topo = await create_topology(chan)

        await topo.climate.consume(functools.partial(handler, exch=chan.default_exchange))

        await aio.Future()


if __name__ == "__main__":
    with aio.Runner() as runner:
        runner.run(main())
