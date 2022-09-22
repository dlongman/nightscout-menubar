from datetime import datetime
from datetime import timedelta
import requests
import logging
import json

class Nightscout():
    
    low_warning_level = 80 # 80 mg/dL == 4.5 mmol/L
    stale_reading_period = -15
    direction_indicator = {
        "DoubleUp": "⇈",
        "SingleUp": "↑",
        "FortyFiveUp": "↗",
        "Flat": "→",
        "FortyFiveDown": "↘",
        "SingleDown": "↓",
        "DoubleDown": "⇊",
        "NONE": "⇼"
    }
    title = ""
    display_mmol = True
    last_refreshed = datetime.min
    data_refresh_period = 60
    
    def __init__(self, base_url: str):
        logging.info("Initialising Nighscout class")
        self.reading_is_stale = None
        self.url = f"{base_url}/api/v1/entries.json?count=1"
        self.refresh()

    def refresh(self):
        
        # don't bother refreshing if the data was refreshed more 
        # recently than the standard sgv reporting frequency
        if not self.data_needs_refresh():
            logging.info("Skipping data refresh")
            return

        logging.info(f"Getting entries from nightscout api using {self.url}")
        response = requests.get(self.url)
        if response.status_code!=200:
            logging.debug(f"Api returned status code {response.status_code}, exiting")
            self.text = "API Error"
            return

        ns_data = response.json()[0]
        logging.debug(f"Api returned data {json.dumps(ns_data)}")

        self.mgdl = ns_data["sgv"]
        self.mmol = "{:.1f}".format(float(self.mgdl)/18)
        if self.display_mmol:
            self.value = self.mmol
        else:
            self.value = self.mgdl

        self.direction = self.direction_indicator[ns_data["direction"]] or "↛"
        self.date = datetime.strptime(ns_data["dateString"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.is_stale = self.date > datetime.now() - timedelta(minutes=self.stale_reading_period)

        # TODO highlight out of range readings
        self.text = f"{self.value}{self.direction}"

        # record when data was last refreshed so we can reduce the number of api requests
        self.last_refreshed = datetime.now()

        logging.debug(f"{self}")

    def data_needs_refresh(self) -> bool:
        seconds_since_last_refresh = (datetime.now() - self.last_refreshed).total_seconds()
        return seconds_since_last_refresh >= self.data_refresh_period

    def __str__(self):
        return f"Latest reading from {self.date}\n\ttext={self.text}\n\tis_stale={self.is_stale}\n\tmmol={self.mmol}\n\tmgdl={self.mgdl}"
    