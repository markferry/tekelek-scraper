import requests
from bs4 import BeautifulSoup
import tekelek

def strain(soup):
    return [
        t.text for t in soup.select("table:nth-of-type(2) td:nth-of-type(5)")
    ]

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
