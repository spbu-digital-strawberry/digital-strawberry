import dataclasses as dc

import aio_pika

CAMERA_TOPIC = "camera"
CLIMATE_TOPIC = "climate"
CORE_TOPIC = "core"
DISEASE_DETECTOR_TOPIC = "disease_detector"
HARDWARE_MANAGER_TOPIC = "hardware_manager"
IRRIGATION_CONTROLLER_TOPIC = "irrigation_controller"
IRRIGATOR_TOPIC = "irrigator"
MONITOR_TOPIC = "monitor"
SENSOR_TOPIC = "sensor"


@dc.dataclass(slots=True, frozen=True)
class Topology:
    camera: aio_pika.abc.AbstractQueue
    climate: aio_pika.abc.AbstractQueue
    core: aio_pika.abc.AbstractQueue
    disease_detector: aio_pika.abc.AbstractQueue
    hardware_manager: aio_pika.abc.AbstractQueue
    irrigation_controller: aio_pika.abc.AbstractQueue
    irrigator: aio_pika.abc.AbstractQueue
    monitor: aio_pika.abc.AbstractQueue
    sensor: aio_pika.abc.AbstractQueue

    exchange: aio_pika.abc.AbstractExchange


async def create_topology(chan: aio_pika.abc.AbstractRobustChannel) -> Topology:
    camera_q = await chan.declare_queue(CAMERA_TOPIC, durable=True)
    climate_q = await chan.declare_queue(CLIMATE_TOPIC, durable=True)
    core_q = await chan.declare_queue(CORE_TOPIC, durable=True)
    disease_detector_q = await chan.declare_queue(DISEASE_DETECTOR_TOPIC, durable=True)
    hardware_manager_q = await chan.declare_queue(HARDWARE_MANAGER_TOPIC, durable=True)
    irrigation_controller_q = await chan.declare_queue(IRRIGATION_CONTROLLER_TOPIC, durable=True)
    irrigator_q = await chan.declare_queue(IRRIGATOR_TOPIC, durable=True)
    monitor_q = await chan.declare_queue(MONITOR_TOPIC, durable=True)
    sensor_q = await chan.declare_queue(SENSOR_TOPIC, durable=True)

    return Topology(
        camera=camera_q,
        climate=climate_q,
        core=core_q,
        disease_detector=disease_detector_q,
        hardware_manager=hardware_manager_q,
        irrigation_controller=irrigation_controller_q,
        irrigator=irrigator_q,
        monitor=monitor_q,
        sensor=sensor_q,
        exchange=chan.default_exchange,
    )
