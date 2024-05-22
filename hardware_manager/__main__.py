import asyncio as aio
import json
import functools

from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractExchange

from common import config
from common.topology import (
    create_topology,
    CORE_TOPIC,
    DISEASE_DETECTOR_TOPIC,
    send_data,
    generate_msg_id,
)


async def handler(msg: AbstractIncomingMessage, exch: AbstractExchange):
    async with msg.process():
        data = json.loads(msg.body.decode())
        print(f"Hardware manager получил сообщение: {data=}")
        # await send_data(exch, dict(id=generate_msg_id(), src=DISEASE_DETECTOR_TOPIC, dst=CORE_TOPIC, diseases=diseases))


async def main():
    conn = await connect_robust(config.RMQ_URI)
    async with conn:
        chan = await conn.channel()
        topo = await create_topology(chan)

        await topo.hardware_manager.consume(functools.partial(handler, exch=chan.default_exchange))

        await aio.Future()


if __name__ == "__main__":
    with aio.Runner() as runner:
        runner.run(main())
