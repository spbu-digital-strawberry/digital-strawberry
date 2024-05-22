import asyncio as aio
import json
import functools

from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractExchange

from common import config
from common.topology import (
    create_topology,
    send_data,
    generate_msg_id, IRRIGATOR_TOPIC, HARDWARE_MANAGER_TOPIC, CLIMATE_TOPIC,
)


async def handler(msg: AbstractIncomingMessage, exch: AbstractExchange):
    async with msg.process():
        data = json.loads(msg.body.decode())
        print(f"Hardware manager получил сообщение: {data=}")
        temperature = data["temperature"]
        irrigation = data["irrigation"]

        clamped_irrigation = min(max(30, irrigation), 70)
        if irrigation != clamped_irrigation:
            print(f"!Команда на полив за лимитами, обрезаем: {irrigation=}, {clamped_irrigation=}")

        clamped_temperature = min(max(17.0, temperature), 30.0)
        if temperature != clamped_temperature:
            print(f"!Команда климат контроля за лимитами, обрезаем: {temperature=}, {clamped_temperature=}")

        await send_data(
            exch,
            dict(
                id=generate_msg_id(),
                src=HARDWARE_MANAGER_TOPIC,
                dst=IRRIGATOR_TOPIC,
                irrigation=clamped_irrigation),
        )
        await send_data(
            exch,
            dict(
                id=generate_msg_id(),
                src=HARDWARE_MANAGER_TOPIC,
                dst=CLIMATE_TOPIC,
                temperature=clamped_temperature),
        )


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
