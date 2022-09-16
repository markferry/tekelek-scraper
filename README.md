# tekelek-scraper

Scrape Tekelek 608A data to MQTT.

Local settings are still hardcoded.

***The decoding of data is totally wrong!***

# Installation

There are two ways to run this.

## Using BeautifulSoup

```
pip install -r requirements.soup.txt
python tek-soup.py
```

## Using Scrapy
Scrapy is heavier-weight but has the advantage of handling `file://` URIs.

```
sudo apt-get install libxml2-dev libxslt-dev

pip install -r requirements.scrapy.txt
scrapy runspider tek-scrapy.py
```

## Service

Run via systemd timer or in a crontab:

