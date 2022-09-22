"""Retrieves the latest entry from a Nightscout installation"""
import logging
import json

from datetime import datetime
from datetime import timedelta
import requests


class Nightscout():
    """Simple wrapper around the Nightscout entries api. Retrieves the latest
    blood glucose reading when refresh() is called and exposes the data value
    in mmol/L or mg/dL depending on the display_mmol setting with the value
    property. A string representation of the current value and trend is
    exposed in the title property.

    Attributes:
    -----------
        value: float
            The current blood glucose reading
        title: str
            The current blood glucose reading and trend indicator
        display_mmol: bool
            If True the mmol/L value is used for the current blood glucose
            value, otherwise the mg/dL value is used.
        low_warning_level: int
            The value in mg/dL that indicates a low blood glucose reading
        high_warning_level: int
            The value in mg/dL that indicates a high blood glucose reading
        is_low: bool
            True is the current blood glucose value is below the low_warning_level
        in_range: bool
            True if the current blood glucose value is within the low_ and
            high_ warning levels, else False
        is_stale: bool
            True if the last reading was longer ago than the stale_reading_period
        stale_reading_period: int
            The number of minutes that should elapse before a reading is considered stale
        data_refresh_period: int
            The number of seconds that should elapse before a new api request is made
        last_refreshed: datetime
            The time the data was last retrieved from the api

    Methods:
    --------
    refresh():
        Gets the latest data from the entries api. Only refreshes the data once
        within the data_refresh_period to reduce api call volume.
    """
    # public attributes
    low_warning_level = 80 # 80 mg/dL == 4.5 mmol/L
    high_warning_level = 240 # 240 mg/dL == 13.3 mmol/L
    title = ""
    display_mmol = True
    is_low = False
    in_range = True
    stale_reading_period = -15
    last_refreshed = datetime.min
    data_refresh_period = 60

    def __init__(self, base_url: str):
        logging.info("Initialising Nightscout class")
        self.reading_is_stale = None
        self.url = f"{base_url}/api/v1/entries.json?count=1"
        self.refresh()

    def refresh(self):
        """Retrieves the latest blood glucose reading from the Nightscout
        API, calculates the mmol/L equivalent of the mg/dL reading and
        generates a simple display string with the current value and trend
        """
        # don't bother refreshing if the data was refreshed more
        # recently than the standard sgv reporting frequency
        if not self.data_needs_refresh():
            logging.info("Skipping data refresh")
            return

        logging.info("Getting entries from nightscout api using %s", self.url)
        response = requests.get(self.url)
        if response.status_code!=200:
            logging.debug("Api returned status code %s, exiting", response.status_code)
            self.text = "API Error"
            return

        ns_data = response.json()[0]
        logging.debug("Api returned data %s", json.dumps(ns_data))

        self.mgdl = ns_data["sgv"]

        calculated_mmol = float(self.mgdl)/18
        self.mmol = f"{calculated_mmol:.1f}"
        if self.display_mmol:
            self.value = self.mmol
        else:
            self.value = self.mgdl

        self.reading_in_range(self.mgdl)

        self.direction = self.get_direction_indicator(ns_data["direction"])
        self.date = datetime.strptime(ns_data["dateString"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.is_stale = self.date > datetime.now() - timedelta(minutes=self.stale_reading_period)

        self.text = f"{self.value}{self.direction}"

        # record when data was last refreshed so we can reduce the number of api requests
        self.last_refreshed = datetime.now()

        logging.debug("OBJECT: %s", str(self))

    def reading_in_range(self, value: int):
        """Compares current reading to high and low thresholds"""
        if value >= self.high_warning_level:
            self.in_range = False
            self.is_low = False
        elif value <= self.low_warning_level:
            self.in_range = False
            self.is_low = True
        else:
            self.in_range = True
            self.is_low = False

    def get_direction_indicator(self, direction: str) -> str:
        """Return a more friendly direction indicator based on the api return value"""
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
        return direction_indicator[direction] or "↛"

    def data_needs_refresh(self) -> bool:
        """Determines whether the time since the last api call was long
        enough to warrant a new api call. By default this is 60s as this
        is the minimum gap between readings in most CGM's"""
        seconds_since_last_refresh = (datetime.now() - self.last_refreshed).total_seconds()
        return seconds_since_last_refresh >= self.data_refresh_period

    def __str__(self):
        return f"Latest reading from {self.date}\n\ttext={self.text} \
            \n\tis_stale={self.is_stale}\n\tmmol={self.mmol}\n\tmgdl={self.mgdl}"
    