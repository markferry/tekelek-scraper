import json
import re
from math import pi, trunc

from paho.mqtt import publish

MQTTHOST = "localhost"
TOPIC_ROOT = "ha"
URL = "http://olive-hub/diag.htm"


class OilTank:
    def volume(self, depth):
        """Where depth is the distance between the top of the tank and the surface"""
        return self.area * (self.height - depth) / 1000


class VCylinder(OilTank):
    """Vertical cylinder"""

    def __init__(self, name, height, radius):
        self.name = name
        self.height = height
        self.area = radius**2 * pi


class RectTank(OilTank):
    def __init__(self, name, length, width, height):
        self.name = name
        self.height = height
        self.area = length * width


class SensorData:
    def __init__(self, row):
        data = row[4]

        v = re.findall(r"\w+", data)

        if len(v) == 6:
            raw = {
                "data": int(v[0]),
                "aux": int(v[1]),
                "bat": int(v[2]),
                "cache": (
                    int(v[3], 16),
                    int(v[4], 16),
                    int(v[5], 16),
                ),
            }
            self.dev_id = int(row[0])
            self.rf_addr = int(row[1])
            self.rx_count = int(row[2])
            self.rx_time = row[3]
            self.temperature = raw["data"] / 100
            self.depth = raw["aux"]
            self.battery_level = raw["bat"]

            if len(row) >= 6:
                self.fl = row[5]
            else:
                self.fl = ""

            self.raw = raw

            self.check()
        else:
            self.dev_id = self.rf_addr = self.rx_count = self.rx_time = None
            self.depth = self.temperature = self.battery_level = None
            self.fl = self.raw = None

        self.volume = None

    def calc_volume(self, tank):
        self.volume = tank.volume(self.depth)

    def check(self):
        """Check that raw values match cache"""
        c = self.raw["cache"]

        # xx yy zz
        #     ^--^ temperature / 100C
        #    ^^ depth / 0.5cm (overlaps temperature)
        # ^^ battery?

        assert (c[2] + ((c[1] & 0xF) << 8)) == self.raw["data"]
        assert trunc(c[1] / 2) == self.raw["aux"]
        assert trunc(c[0] & 0x7F) == self.raw["bat"]  # ??

    def __str__(self):
        # return f"{self.dev_id}\t{self.rf_addr}\t{self.rx_count}\t{self.rx_time}\t{self.raw}"
        return json.dumps(self.__dict__)


class Tekelek:
    name = "tekelek"
    tanks = [
        VCylinder("main", height=130, radius=(160 / 2)),
        RectTank("annex", length=150, width=110, height=81),
    ]

    def decode(self, sensors):
        json_data = []
        for idx, tank in enumerate(self.tanks):
            tek_data = SensorData(sensors[idx])
            if tek_data.depth:
                tek_data.calc_volume(tank)
                json_data.append((tank.name, str(tek_data)))
        return json_data

    def publish(self, sensors):
        json_data = self.decode(sensors)
        for tank, data in json_data:
            publish.single(
                "/".join([TOPIC_ROOT, self.name, tank]),
                data,
                hostname=MQTTHOST,
                client_id=self.name,
            )
