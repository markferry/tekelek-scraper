import scrapy
import tekelek


class TekelekScraper(scrapy.Spider):
    name = "tekelek"
    start_urls = [tekelek.URL]

    def parse(self, response):
        tek = tekelek.Tekelek()
        sensors = [
            response.xpath(f"//table[2]//tr[{i}]/td/text()").getall()
            for i in range(2, 5)
        ]
        tek.publish(sensors)
