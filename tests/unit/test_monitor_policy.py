import pytest

from monitor.__main__ import check_permission
from common.topology import (
    CAMERA_TOPIC,
    CLIMATE_TOPIC,
    CORE_TOPIC,
    DISEASE_DETECTOR_TOPIC,
    HARDWARE_MANAGER_TOPIC,
    IRRIGATION_CONTROLLER_TOPIC,
    IRRIGATOR_TOPIC,
    SENSOR_TOPIC,
)


@pytest.mark.parametrize(
    "data, expected_authorized",
    [
        # Проверка разрешённых соединений
        (dict(src=CAMERA_TOPIC, dst=DISEASE_DETECTOR_TOPIC), True),
        (dict(src=SENSOR_TOPIC, dst=IRRIGATION_CONTROLLER_TOPIC), True),
        (dict(src=DISEASE_DETECTOR_TOPIC, dst=CORE_TOPIC), True),
        (dict(src=IRRIGATION_CONTROLLER_TOPIC, dst=CORE_TOPIC), True),
        (dict(src=IRRIGATION_CONTROLLER_TOPIC, dst=HARDWARE_MANAGER_TOPIC), True),
        (dict(src=HARDWARE_MANAGER_TOPIC, dst=CORE_TOPIC), True),
        (dict(src=HARDWARE_MANAGER_TOPIC, dst=IRRIGATOR_TOPIC), True),
        (dict(src=HARDWARE_MANAGER_TOPIC, dst=CLIMATE_TOPIC), True),
        (dict(src=IRRIGATOR_TOPIC, dst=HARDWARE_MANAGER_TOPIC), True),
        (dict(src=CLIMATE_TOPIC, dst=HARDWARE_MANAGER_TOPIC), True),

        # Проверка неразрешённых соединений
        (dict(src=CAMERA_TOPIC, dst=CLIMATE_TOPIC), False),
        (dict(src=CLIMATE_TOPIC, dst=CAMERA_TOPIC), False),
        (dict(src=SENSOR_TOPIC, dst=CORE_TOPIC), False),
        (dict(src=DISEASE_DETECTOR_TOPIC, dst=IRRIGATION_CONTROLLER_TOPIC), False),
        (dict(src=IRRIGATION_CONTROLLER_TOPIC, dst=CAMERA_TOPIC), False),
        (dict(src=HARDWARE_MANAGER_TOPIC, dst=SENSOR_TOPIC), False),
        (dict(src=IRRIGATOR_TOPIC, dst=CLIMATE_TOPIC), False),
        (dict(src=CLIMATE_TOPIC, dst=IRRIGATION_CONTROLLER_TOPIC), False),

        # Проверка отсутствующих данных
        (dict(src=None, dst=CLIMATE_TOPIC), False),
        (dict(src=CAMERA_TOPIC, dst=None), False),
        (dict(src=None, dst=None), False),
        (dict(src=CAMERA_TOPIC), False),
        (dict(dst=CLIMATE_TOPIC), False),
        ({}, False),
    ]
)
def test_monitor_policy(data, expected_authorized) -> None:
    authorized = check_permission(data)
    assert authorized == expected_authorized
