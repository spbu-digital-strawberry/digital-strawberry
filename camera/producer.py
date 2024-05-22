import asyncio as aio
import json

from aio_pika.abc import AbstractChannel, AbstractExchange
from aio_pika import Message

from common.topology import MONITOR_TOPIC, CAMERA_TOPIC, DISEASE_DETECTOR_TOPIC, generate_msg_id


async def send_data(exch: AbstractExchange, photo_id: int) -> None:
    body = json.dumps(dict(id=generate_msg_id(), photo_id=photo_id, src=CAMERA_TOPIC, dst=DISEASE_DETECTOR_TOPIC)).encode()
    await exch.publish(Message(body), MONITOR_TOPIC)


async def produce(chan: AbstractChannel) -> None:
    exch = chan.default_exchange

    photo_id = 0
    while True:
        photo_id += 1
        print(f"Отправляем фото: {photo_id=}")
        await send_data(exch, photo_id)
        await aio.sleep(3.0)
