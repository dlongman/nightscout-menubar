from datetime import datetime
from datetime import timedelta
import requests

class Nightscout():
    
    #nightscout_url = "https://d9n-nightscout.herokuapp.com"
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
    
    def __init__(self, base_url: str):
        self.reading_is_stale = None
        self.url = f"{base_url}/api/v1/entries.json?count=1"
        self.refresh()

    def refresh(self):
        
        response = requests.get(self.url)
        if response.status_code!=200:
            self.text = "API Error"
            return

        ns_data = response.json()[0]

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

    
    