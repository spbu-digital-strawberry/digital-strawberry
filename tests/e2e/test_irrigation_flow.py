import asyncio as aio
import json
from unittest.mock import ANY

import pytest
import aio_pika
from aio_pika import Message

from common.topology import (
    create_topology,
    generate_msg_id,
    SENSOR_TOPIC,
    IRRIGATION_CONTROLLER_TOPIC,
    MONITOR_TOPIC,
    HARDWARE_MANAGER_TOPIC,
    IRRIGATOR_TOPIC,
    CLIMATE_TOPIC,
)

RMQ_URI = "amqp://guest:guest@localhost:5672/guest"


async def read_queue_content(q: aio_pika.abc.AbstractQueue) -> list[dict]:
    msgs = []
    while msg := await q.get(fail=False):
        async with msg.process():
            msg_data = json.loads(msg.body.decode())
            msgs.append(msg_data)
    return msgs


@pytest.mark.parametrize(
    "begin_temp, humidity, end_temp, irrigation",
    [
        (50.0, 40, 30.0, 60),
        (20.0, 40, 20.0, 60),
        (10.0, 40, 17.0, 60),
        (50.0, 20, 30.0, 70),
        (20.0, 60, 20.0, 40),
        (10.0, 80, 17.0, 30),
    ],
)
@pytest.mark.asyncio
async def test_irrigation_flow(begin_temp, humidity, end_temp, irrigation) -> None:
    conn = await aio_pika.connect(RMQ_URI)
    async with conn:
        chan = await conn.channel()
        topology = await create_topology(chan)

        msg_data = dict(
            temperature=begin_temp,
            humidity=humidity,
            id=generate_msg_id(),
            src=SENSOR_TOPIC,
            dst=IRRIGATION_CONTROLLER_TOPIC,
        )
        await topology.exchange.publish(Message(json.dumps(msg_data).encode()), MONITOR_TOPIC)

        await aio.sleep(0.2)  # на всякий случай

        irrigator_msgs = await read_queue_content(topology.irrigator)
        climate_msgs = await read_queue_content(topology.climate)

        assert irrigator_msgs == [dict(id=ANY, src=HARDWARE_MANAGER_TOPIC, dst=IRRIGATOR_TOPIC, irrigation=irrigation)]
        assert climate_msgs == [dict(id=ANY, src=HARDWARE_MANAGER_TOPIC, dst=CLIMATE_TOPIC, temperature=end_temp)]
