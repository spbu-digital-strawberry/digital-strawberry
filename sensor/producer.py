import asyncio as aio
import random

from aio_pika.abc import AbstractChannel

from common.topology import generate_msg_id, SENSOR_TOPIC, IRRIGATION_CONTROLLER_TOPIC, send_data


async def produce(chan: AbstractChannel) -> None:
    exch = chan.default_exchange

    while True:
        data = dict(
            temperature=random.uniform(5.0, 30.0),
            humidity=random.randint(0, 100),
            id=generate_msg_id(),
            src=SENSOR_TOPIC,
            dst=IRRIGATION_CONTROLLER_TOPIC,
        )
        await send_data(exch, data)
        await aio.sleep(3.0)
