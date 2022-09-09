# tekelek-scraper

Scrape Tekelek 608A data to MQTT.

Local settings are still hardcoded.


## Installation

```
sudo apt-get install libxml2-dev libxslt-dev
pip install -r requirements.txt
```

## Invocation

Run via systemd timer or in a crontab:

```
scrapy runspider tekelek.py
```

