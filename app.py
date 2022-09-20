# Inspired from https://www.pythongasm.com/menubar-app-for-macos-using-python/ article
# Icons from https://www.flaticon.com/free-icons/diabetes

from datetime import datetime
from datetime import timedelta
import threading
import requests
import rumps
import webbrowser

class NightscoutMenuApp(rumps.App):
    def __init__(self):
        super(NightscoutMenuApp, self).__init__(name="NightscoutMenuApp")

        self.nightscoutUrl = "https://d9n-nightscout.herokuapp.com"
        self.icon = "icon.png"
        self.low_warning = 80 # 80 mg/dL == 4.5 mmol/L

    @rumps.clicked("Launch Nightscout")
    def launchNightscout(self, sender):
        # launch nightscout url in browser
        webbrowser.open(self.nightscoutUrl, new=0)

    @rumps.timer(5)
    def updateStockPrice(self, sender):
        thread = threading.Thread(target=self.getBloodGlucose)
        thread.start()

    def getBloodGlucose(self):
        response = requests.get(f"{self.nightscoutUrl}/api/v1/entries.json?count=1")

        if response.status_code!=200:
            self.title = "API Error"
            return

        ns_data = response.json()[0]

        sgv_mgdl = ns_data["sgv"]
        sgv_mmol = float(sgv_mgdl)/18
        direction = ns_data["direction"]
        # 2022-09-19T15:08:00.000Z
        sgv_date = datetime.strptime(ns_data["dateString"], "%Y-%m-%dT%H:%M:%S.%fZ")

        formatted_sgv = "{:.1f}".format(sgv_mmol)

        # if sgv_mgdl <= self.low_warning:
        #     rumps.alert(title="Low Blood Glucose Warning", message=f"Blood glucose is {formatted_sgv} and below the low warning level")

        # TODO highlight out of range readings
        if self.reading_is_stale(sgv_date):
            self.title = ""
        else:
            self.title = f"{formatted_sgv}{self.format_direction(direction)}"

    def format_direction(self, direction) -> str:
        trend="⇼"
        if direction == "DoubleUp":
            trend="⇈"
        elif direction == "SingleUp":
            trend="↑"
        elif direction == "FortyFiveUp":
            trend="↗"
        elif direction == "Flat":
            trend="→"
        elif direction == "FortyFiveDown":
            trend="↘"
        elif direction == "SingleDown":
            trend="↓"
        elif direction == "DoubleDown":
            trend="⇊"
        elif direction == "NONE":
            trend="⇼"
        else:
            trend = "↛"
        
        return trend

    def reading_is_stale(self, dt: datetime) -> bool:
        # reading is stale if it is older than 15 mins
        return dt > datetime.now() - timedelta(minutes=-15)
       
if __name__ == '__main__':
    NightscoutMenuApp().run()