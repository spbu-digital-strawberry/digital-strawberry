import asyncio as aio
import json
import functools

from aio_pika import connect_robust, Message
from aio_pika.abc import AbstractIncomingMessage, AbstractExchange

from common import config
from common.topology import (
    create_topology,
    CAMERA_TOPIC,
    CLIMATE_TOPIC,
    CORE_TOPIC,
    DISEASE_DETECTOR_TOPIC,
    HARDWARE_MANAGER_TOPIC,
    IRRIGATION_CONTROLLER_TOPIC,
    IRRIGATOR_TOPIC,
    SENSOR_TOPIC,
)


PERMISSION_MAP = {
    CAMERA_TOPIC: {DISEASE_DETECTOR_TOPIC},
    SENSOR_TOPIC: {IRRIGATION_CONTROLLER_TOPIC},
    DISEASE_DETECTOR_TOPIC: {CORE_TOPIC},
    IRRIGATION_CONTROLLER_TOPIC: {CORE_TOPIC, HARDWARE_MANAGER_TOPIC},
    HARDWARE_MANAGER_TOPIC: {CORE_TOPIC, IRRIGATOR_TOPIC, CLIMATE_TOPIC},
    IRRIGATOR_TOPIC: {HARDWARE_MANAGER_TOPIC},
    CLIMATE_TOPIC: {HARDWARE_MANAGER_TOPIC},
}


def check_permission(data: dict):
    src = data.get("src")
    dst = data.get("dst")
    if src is None or dst is None:
        return False

    allowed_dsts = PERMISSION_MAP.get(src)
    if allowed_dsts is None:
        return False

    if dst in allowed_dsts:
        return True
    return False


async def handler(msg: AbstractIncomingMessage, exch: AbstractExchange):
    async with msg.process():
        data = json.loads(msg.body.decode())
        print(f"Обрабатываем сообщение: {data=}")
        if check_permission(data):
            print(f"Сообщение прошло проверку политик")
            await exch.publish(Message(msg.body), data["dst"])
        else:
            print(f"!!! Сообщение не прошло проверку политик !!!")


async def main():
    conn = await connect_robust(config.RMQ_URI)
    async with conn:
        chan = await conn.channel()
        topo = await create_topology(chan)

        await topo.monitor.consume(functools.partial(handler, exch=chan.default_exchange))

        await aio.Future()


if __name__ == "__main__":
    with aio.Runner() as runner:
        runner.run(main())
