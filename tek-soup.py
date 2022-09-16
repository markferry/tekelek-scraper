import requests
from bs4 import BeautifulSoup
import tekelek


def strain(soup):
    rows = soup.select("table:nth-of-type(2) tr")
    return [[t.text for t in r.select("td")] for r in rows[1:]]


def get(url):
    return requests.get(url)


def run():
    tek = tekelek.Tekelek()
    response = get(tekelek.URL)
    soup = BeautifulSoup(response.content, "html.parser")
    sensors = strain(soup)
    tek.publish(sensors)


if __name__ == "__main__":
    run()
