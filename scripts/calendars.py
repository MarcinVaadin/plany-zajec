import json
from strefazajec import strefazajec
from stolowkazielonki import tygodniowemenu

def load_services():
    with open("services.json", mode="r", encoding="utf-8") as file:
        return json.load(file)

services = load_services()

# strefazajec.pl
for organization in services['strefazajec']:
    strefazajec(organization, 'calendars/strefazajec')

# tygodniowe menu
tygodniowemenu('calendars/tygodniowemenu')