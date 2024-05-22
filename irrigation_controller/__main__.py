import asyncio as aio
import json
import functools

from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractExchange

from common import config
from common.topology import (
    create_topology,
    CORE_TOPIC,
    HARDWARE_MANAGER_TOPIC,
    send_data,
    generate_msg_id, IRRIGATION_CONTROLLER_TOPIC,
)


def control_irrigation(data) -> dict:
    # На самом деле здесь сложная логика управления среды выращивания клубники
    print(f"Принимаем решение об изменении среды: {data=}")
    temp = data["temperature"]
    hum = data["humidity"]
    res = dict(temperature=temp * 0.5 + 10.0, irrigation=100 - hum)
    print(f"Воздействие на клубнику: {res=}")
    return res


async def handler(msg: AbstractIncomingMessage, exch: AbstractExchange):
    async with msg.process():
        data = json.loads(msg.body.decode())
        result = control_irrigation(data)
        result["id"] = generate_msg_id()
        result["src"] = IRRIGATION_CONTROLLER_TOPIC
        result["dst"] = CORE_TOPIC
        await send_data(exch, result)
        result["dst"] = HARDWARE_MANAGER_TOPIC
        await send_data(exch, result)


async def main():
    conn = await connect_robust(config.RMQ_URI)
    async with conn:
        chan = await conn.channel()
        topo = await create_topology(chan)

        await topo.irrigation_controller.consume(functools.partial(handler, exch=chan.default_exchange))

        await aio.Future()


if __name__ == "__main__":
    with aio.Runner() as runner:
        runner.run(main())
