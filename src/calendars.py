import json
import subprocess
from strefazajec import strefazajec
from stolowkazielonki import tygodniowemenu

raw_base_url = "https://raw.githubusercontent.com/MarcinVaadin/plany-zajec/refs/heads/main/"

def load_services():
    with open("services.json", mode="r", encoding="utf-8") as file:
        return json.load(file)

def link(name, href):
    return "[" + name + "](" + raw_base_url + href + ")\n"

services = load_services()

with open("KALENDARZE.md", 'w') as f:
    # synergia
    f.write("# Plany lekcji SP w Zielonkach-Parceli\n\n")
    p = subprocess.Popen(['npm', '--silent', 'run', 'synergia'], stdout=subprocess.PIPE)
    result = json.loads(p.stdout.read())
    for clazz in result:
        f.write('- ' + link(clazz['id'], clazz['ics']))

    # strefazajec.pl
    f.write("# Strefa Zajęć\n\n")
    for organization in services['strefazajec']:
        metadata = strefazajec(organization, 'calendars/strefazajec')
        f.write("## " + metadata['name'] + "\n\n")
        for course in metadata['courses']:
            f.write('- ' + link(course['title'], course['ics']))

    # tygodniowe menu
    f.write("# Tygodniowe menu szkoły w Zielonkach-Parceli\n\n")
    metadata = tygodniowemenu('calendars/tygodniowemenu')
    for clazz in metadata:
        f.write('- ' + link(clazz['name'], clazz['ics']))
