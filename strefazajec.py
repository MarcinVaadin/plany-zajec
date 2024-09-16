from datetime import timedelta
import re
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
import requests
import dateutil.parser as dparser

classes = {
    'Minecraft' : 'https://www.strefazajec.pl/course/view/id/65496',
    'Szachy': 'https://www.strefazajec.pl/course/view/id/65821',
    'Szycie': 'https://www.strefazajec.pl/course/view/id/64967',
    'Pianino': 'https://www.strefazajec.pl/course/view/id/63775'
}

def load(url):
    return requests.get(url).text

def strip(text):
    return re.sub(r'\s+', ' ', text.strip())

def to_datetime(text):
    return dparser.parse(text, fuzzy=True)

def to_timedelta(text):
    m = re.findall(r'\d+', text)
    hours = int(m[0])
    minutes = 0
    if (len(m) == 2):
        minutes = int(m[1])
    return timedelta(hours=hours, minutes=minutes)

def to_event(title_short, title_full, lesson):
    tds = lesson.find_all("td")
    date = strip(tds[0].text)
    duration = strip(tds[1].text)
    # group = strip(tds[2].text)
    # location = strip(tds[3].text)
    dtstart = to_datetime(date)
    dtend = dtstart + to_timedelta(duration)
    event = Event()
    event.add('name', title_short)
    event.add('description', title_full)
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    return event

cal = Calendar()
cal.add('prodid', '-//Kalendarz Szkolny//example.com//')
cal.add('version', '2.0')

for key in classes:
    content = load(classes[key])
    
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.select_one("h1[class!=logo]").text

    for lesson in soup.find_all("tr", {"class":"lesson_record"}):
        event = to_event(key, title, lesson)
        cal.add_component(event)

f = open("strefazajec.ical", "wb")
f.write(cal.to_ical())
f.close()
