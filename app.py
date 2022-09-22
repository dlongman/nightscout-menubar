# Inspired from https://www.pythongasm.com/menubar-app-for-macos-using-python/ article
# Icons from https://www.flaticon.com/free-icons/diabetes

import threading
import rumps
import webbrowser
import logging
import os

from nightscout import Nightscout

class NightscoutMenuApp(rumps.App):

    nightscoutUrl = "https://d9n-nightscout.herokuapp.com"

    def __init__(self):
        super(NightscoutMenuApp, self).__init__(name="NightscoutMenuApp")
        logging.info("Initialising NightscoutMenuApp class")
        logging.info(f"Nightscout base url is {self.nightscoutUrl}")

        self.icon = "icon.png"
        self.ns = Nightscout(self.nightscoutUrl)

    @rumps.clicked("Launch Nightscout")
    def launchNightscout(self, sender):
        logging.info("Launching Nightscout website")
        webbrowser.open(self.nightscoutUrl, new=0)

    @rumps.timer(5)
    def refreshData(self, sender):
        thread = threading.Thread(target=self.getBloodGlucose)
        thread.start()

    def getBloodGlucose(self):
        self.ns.refresh()
        self.title = self.ns.text

def configure_logging():
	
    print(os.getenv('NS_LOG_FILE'))
    log_file = os.getenv('NS_LOG_FILE') or "/Users/Dave/nightscout/menubar-app/nightscout_menubar.log"
    log_level = os.getenv('NS_LOG_LEVEL') or logging.INFO

    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create file handler for file based logging
    fh = logging.FileHandler(log_file)
    fh.setLevel(log_level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # create console handler for INFO messages
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

if __name__ == '__main__':
    try:
        configure_logging()
        logging.info("Logging configured, launching application")
        NightscoutMenuApp().run()
        logging.info("Exiting")
    except Exception as e:
        logging.error(e)
    finally:
        logging.info("Exiting application")