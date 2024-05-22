from typing import Annotated
import functools
import json
from contextlib import asynccontextmanager
from collections import deque

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from aio_pika import connect_robust
from aio_pika.abc import AbstractIncomingMessage, AbstractExchange

from common import config
from common.topology import create_topology

OPERATOR_TOKEN = "very-secret-operator-token"
WORKER_TOKEN = "very-secret-worker-token"


N_OBSERVATIONS = 5
diseases = deque()
temperature = deque()
irrigation = deque()


def update_diseases(data):
    print(f"Обрабатываем информацию о заболеваниях")
    diseases.append(data["diseases"])
    while len(diseases) > N_OBSERVATIONS:
        diseases.popleft()


def update_climate(data):
    print(f"Обрабатываем информацию об изменении климата и полива")
    temp = data["temperature"]
    irr = data["irrigation"]
    temperature.append(temp)
    while len(temperature) > N_OBSERVATIONS:
        temperature.popleft()
    irrigation.append(irr)
    while len(irrigation) > N_OBSERVATIONS:
        irrigation.popleft()


def get_diseases() -> set[str]:
    res = set()
    for el in diseases:
        res |= set(el)
    return res


def get_temperature() -> float:
    if len(temperature) == 0:
        return -1.0
    return sum(temperature) / len(temperature)


def get_irrigation() -> float:
    if len(irrigation) == 0:
        return -1.0
    return float(sum(irrigation)) / len(irrigation)


async def consumer_handler(msg: AbstractIncomingMessage, exch: AbstractExchange) -> None:
    async with msg.process():
        data = json.loads(msg.body.decode())
        print(f"core получил сообщение: {data=}")
        if "diseases" in data:
            update_diseases(data)
        elif "temperature" in data and "irrigation" in data:
            update_climate(data)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    conn = await connect_robust(config.RMQ_URI)
    async with conn:
        chan = await conn.channel()
        topo = await create_topology(chan)
        await topo.core.consume(functools.partial(consumer_handler, exch=chan.default_exchange))
        yield


app = FastAPI(lifespan=_lifespan)


class Stats(BaseModel):
    diseases: set[str]
    irrigation: float
    temperature: float


@app.get("/get_stats")
async def get_stats(x_token: Annotated[str | None, Header()] = None) -> Stats:
    if x_token != OPERATOR_TOKEN:
        raise HTTPException(403)
    return Stats(diseases=get_diseases(), irrigation=get_irrigation(), temperature=get_temperature())
