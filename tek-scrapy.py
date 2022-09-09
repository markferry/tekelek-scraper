import scrapy
import tekelek

class TekelekScraper(scrapy.Spider):
    name = "tekelek"
    start_urls = [tekelek.URL]

    def parse(self, response):
        tek = tekelek.Tekelek()
        sensors = response.xpath("//table[2]//td[5]/text()").getall()
        tek.publish(sensors)
