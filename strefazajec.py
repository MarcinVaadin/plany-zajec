from datetime import timedelta
import re
from bs4 import BeautifulSoup
from icalendar import Alarm, Calendar, Event
import requests
import dateutil.parser as dparser
import dateparser

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
    return dateparser.parse(text, languages=['pl'])

def to_timedelta(text):
    h = re.findall(r'(\d+) godz.', text)
    m = re.findall(r'(\d+) min.', text)
    h = int(h[0]) if len(h) > 0 else 0
    m = int(m[0]) if len(m) > 0 else 0
    return timedelta(hours=h, minutes=m)

def to_event(title_short, title_full, lesson):
    tds = lesson.find_all("td")
    date = strip(tds[0].text)
    duration = strip(tds[1].text)
    # group = strip(tds[2].text)
    # location = strip(tds[3].text)
    dtstart = to_datetime(date)
    dtend = dtstart + to_timedelta(duration)
    event = Event()
    event.add('summary', title_short)
    event.add('description', title_full)
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    alarm = Alarm()
    alarm.add('action', 'audio')
    alarm.add('trigger', dtstart - timedelta(minutes=30))
    event.add_component(alarm)
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

f = open("strefazajec.ics", "wb")
f.write(cal.to_ical())
f.close()
