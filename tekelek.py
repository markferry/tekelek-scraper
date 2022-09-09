from math import pi
import json
import scrapy
import paho.mqtt.publish as publish

MQTTHOST = "localhost"
TOPIC_ROOT = "ha"


class OilTank:
    def volume(self, depth):
        """Where depth is the distance between the top of the tank and the surface"""
        return self.area * (self.height - depth * self.depth_factor) / 1000


class VCylinder(OilTank):
    """Vertical cylinder"""

    def __init__(self, name, height, radius, depth_factor=1):
        self.name = name
        self.height = height
        self.area = radius**2 * pi
        self.depth_factor = depth_factor


class RectTank(OilTank):
    def __init__(self, name, length, width, height, depth_factor=1):
        self.name = name
        self.height = height
        self.area = length * width
        self.depth_factor = depth_factor


class SensorData:
    def __init__(self, s):
        modem_values = s.split(" ")
        if modem_values[1] != "Data":
            self.depth = int(modem_values[0])
            self.temperature = int(modem_values[1])
            self.battery_level = int(modem_values[2])
        else:
            self.depth = self.temperature = self.battery_level = None


class Tekelek(scrapy.Spider):
    name = "tekelek"
    start_urls = ["http://olive-hub/diag.htm"]
    # start_urls = ['file://./diag.htm']
    tanks = [
        VCylinder("main", height=146, radius=(160 / 2), depth_factor=1 / 20),
        RectTank("annex", length=194, width=154, height=109),
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

    def parse(self, response):
        sensors = response.xpath("//table[2]//td[5]/text()").getall()
        for idx, tank in enumerate(self.tanks):
            tek_data = SensorData(sensors[idx])
            if tek_data.depth:
                json_data = json.dumps(self.value(tank, tek_data))
                publish.single(
                    "/".join([TOPIC_ROOT, self.name, tank.name]),
                    json_data,
                    hostname=MQTTHOST,
                    client_id=self.name,
                )
