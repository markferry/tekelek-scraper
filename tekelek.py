import json
import re
from collections import defaultdict
from math import pi, trunc

from paho.mqtt import publish
import scrapy

MQTTHOST = "localhost"
TOPIC_ROOT = "ha"


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
    def __init__(self, s):
        v = re.findall(r"\w+", s)
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
            self.temperature = raw["data"] / 100
            self.depth = raw["aux"]
            self.battery_level = raw["bat"]
            self.raw = raw
            self.check()
        else:
            self.depth = self.temperature = self.battery_level = None
            self.raw = None

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


class Tekelek(scrapy.Spider):
    name = "tekelek"
    start_urls = ["http://olive-hub/diag.htm"]
    tanks = [
        RectTank("annex", length=150, width=110, height=81),
        VCylinder("main", height=130, radius=(160 / 2)),
    ]

    @staticmethod
    def value(tank, data):
        if data.depth:
            return {
                "volume": tank.volume(data.depth),
                "temperature": data.temperature,
                "battery_level": data.battery_level,
            }

        return {"volume": None}

    def decode(self, sensors):
        json_data = []
        for idx, tank in enumerate(self.tanks):
            tek_data = SensorData(sensors[idx])
            if tek_data.depth:
                json_data.append((tank.name, json.dumps(self.value(tank, tek_data))))
        return json_data

    def parse(self, response):
        sensors = response.xpath("//table[2]//td[5]/text()").getall()
        json_data = self.decode(sensors)
        for tank, data in json_data:
            publish.single(
                "/".join([TOPIC_ROOT, self.name, tank]),
                data,
                hostname=MQTTHOST,
                client_id=self.name,
            )
