# Inspired from https://www.pythongasm.com/menubar-app-for-macos-using-python/ article
# Icons from https://www.flaticon.com/free-icons/diabetes

import threading
import rumps
import webbrowser

from nightscout import Nightscout

class NightscoutMenuApp(rumps.App):

    nightscoutUrl = "https://d9n-nightscout.herokuapp.com"

    def __init__(self):
        super(NightscoutMenuApp, self).__init__(name="NightscoutMenuApp")
        self.icon = "icon.png"
        self.ns = Nightscout(self.nightscoutUrl)

    @rumps.clicked("Launch Nightscout")
    def launchNightscout(self, sender):
        webbrowser.open(self.nightscoutUrl, new=0)

    @rumps.timer(5)
    def refreshData(self, sender):
        thread = threading.Thread(target=self.getBloodGlucose)
        thread.start()

    def getBloodGlucose(self):
        self.ns.refresh()
        self.title = self.ns.text
       
if __name__ == '__main__':
    NightscoutMenuApp().run()