# Inspired from https://www.pythongasm.com/menubar-app-for-macos-using-python/ article
# Icons from https://www.flaticon.com/free-icons/diabetes
"""Simple macOS menubar application that displays current blood glucose
information from a Nightscout installation
"""
import threading
import logging
import os
import webbrowser

import rumps

from nightscout import Nightscout

class NightscoutMenuApp(rumps.App):
    """Creates a macOS menubar app that displays blood glucose data from Nightscout

    Uses the rumps package to create the macOS UI
    """

    nightscoutUrl = "https://d9n-nightscout.herokuapp.com"

    def __init__(self):
        super(NightscoutMenuApp, self).__init__(name="NightscoutMenuApp")
        logging.info("Initialising NightscoutMenuApp class")
        logging.info("Nightscout base url is %s", self.nightscoutUrl)

        self.icon = "icon.png"
        self.nightscout = Nightscout(self.nightscoutUrl)

    @rumps.clicked("Launch Nightscout")
    def launch_website(self, sender):
        """Launches the Nightscout website in a browser window"""
        logging.info("Launching Nightscout website")
        webbrowser.open(self.nightscoutUrl, new=0)

    @rumps.timer(5)
    def refresh_data(self, sender):
        """Refreshes the Nightscout data every 5 seconds in a separate thread"""
        thread = threading.Thread(target=self.get_bg)
        thread.start()

    def get_bg(self):
        """Refreshes the Nightscout data and displays the data in the menubar"""
        self.nightscout.refresh()
        self.title = self.nightscout.text

def configure_logging():
    """Configures file and console logging, file logging logs to a file
    location defined in the environment variable NS_LOG_FILE and logs
    INFO output or a logging level defined in environment variable NS_LOG_LEVEL.
    The console logger logs DEBUG level messages
    """
    print(os.getenv('NS_LOG_FILE'))
    log_file = os.getenv('NS_LOG_FILE') or \
        "/Users/Dave/nightscout/menubar-app/nightscout_menubar.log"
    log_level = os.getenv('NS_LOG_LEVEL') or logging.INFO

    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create file handler for file based logging
    file = logging.FileHandler(log_file)
    file.setLevel(log_level)
    file.setFormatter(formatter)
    logger.addHandler(file)

    # create console handler for INFO messages
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)

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
