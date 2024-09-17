from datetime import timedelta
import re
from bs4 import BeautifulSoup
from icalendar import Alarm, Calendar, Event
import requests
import dateparser

base_url = 'https://www.strefazajec.pl'
company_url = base_url + '/company/DK-Stare-Babice-id864.html'

def load(url):
    return requests.get(url).text

def strip(text):
    return re.sub(r'\s+', ' ', text.strip())

def find_courses(content):
    list = []
    soup = BeautifulSoup(content, 'html.parser')
    course_list = soup.select_one('div#course_list')
    courses = course_list.select('div.course-record')
    for course in courses:
        href = course.select_one('a').attrs['href']
        list.append(href)
    return list

def to_datetime(text):
    return dateparser.parse(text, languages=['pl'])

def to_timedelta(text):
    h = re.findall(r'(\d+) godz.', text)
    m = re.findall(r'(\d+) min.', text)
    h = int(h[0]) if len(h) > 0 else 0
    m = int(m[0]) if len(m) > 0 else 0
    return timedelta(hours=h, minutes=m)

def to_event(title, lesson):
    tds = lesson.find_all("td")
    date = strip(tds[0].text)
    duration = strip(tds[1].text)
    # group = strip(tds[2].text)
    # location = strip(tds[3].text)
    dtstart = to_datetime(date)
    dtend = dtstart + to_timedelta(duration)
    event = Event()
    event.add('summary', title)
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    alarm = Alarm()
    alarm.add('action', 'audio')
    alarm.add('trigger', dtstart - timedelta(minutes=30))
    event.add_component(alarm)
    return event

def parse_to_ics(url, filename):
    cal = Calendar()
    cal.add('prodid', '-//Kalendarz Szkolny//example.com//')
    cal.add('version', '2.0')

    content = load(url)    
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.select_one("h1[class!=logo]").text

    for lesson in soup.find_all("tr", {"class":"lesson_record"}):
        event = to_event(title, lesson)
        cal.add_component(event)

    f = open(filename, "wb")
    f.write(cal.to_ical())
    f.close()
    print('DONE: ' + title)


content = load(company_url)
soup = BeautifulSoup(content, 'html.parser')
paginator = soup.select_one("div[class=paginator]")

list = []

pages = re.findall(r'\d+', paginator.text)
for page in pages:
    if page == '1':
        list += find_courses(content)
    else:
        list += find_courses(load(company_url + '?page=' + page))

for href in list:
    id = re.findall(r'\d+', href)
    parse_to_ics(base_url + href, 'strefazajec/' + id[0] + '.ics')
