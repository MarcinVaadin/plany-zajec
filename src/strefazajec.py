from datetime import timedelta
import re
from bs4 import BeautifulSoup
from icalendar import Alarm, Calendar, Event
import os
import json
from utils import *

base_url = 'https://www.strefazajec.pl'

def find_courses(soup, target_dir):
    list = []
    course_list = soup.select_one('div#course_list')
    courses = course_list.select('div.course-record')
    for course in courses:
        href = course.select_one('a').attrs['href']
        title = strip(course.select_one('h3').text)
        id = get_course_id(href)
        list.append({
            'id': id,
            'ics': target_dir + '/' + id + '/' + id + '.ics',
            'url': base_url + href, 
            'title': title.title(),
        })
    return list

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

def parse_to_ics(course, target_dir):
    cal = Calendar()
    cal.add('prodid', '-//Kalendarz Szkolny//example.com//')
    cal.add('version', '2.0')

    content = load(course['url'])
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.select_one("h1[class!=logo]").text

    for lesson in soup.find_all("tr", {"class":"lesson_record"}):
        event = to_event(title, lesson)
        cal.add_component(event)

    target_dir = target_dir + '/' + course['id']
    os.makedirs(target_dir, 0o777, True)

    filename = course['id'] + '.ics'
    f = open(target_dir + '/' + filename, "wb")
    f.write(cal.to_ical())
    f.close()
    print('DONE: ' + f.name)

def save_metadata(metadata, target_dir):
    with open(target_dir + '/metadata.json', 'w') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

def get_id(url):
    m = re.search(r'.*[^\d](\d+)\.html$', url)
    return m.group(1)

def get_course_id(href):
    m = re.search(r'.*\/(\d+)$', href)
    return m.group(1)

def get_pages(soup):
    paginator = soup.select_one("div[class=paginator]")
    return re.findall(r'\d+', paginator.text)

def get_sort_key(c):
    return c['title']

# Otwiera danego organizatora i szuka zajec
def strefazajec(organization, target_dir):
    id = organization['id']
    url = organization['url']

    content = load(url)
    soup = BeautifulSoup(content, 'html.parser')

    name = soup.select_one('div.comapny_info h2').text
    address = soup.select_one('div.comapny_info p').text
    
    target_dir = target_dir + '/' + id
    os.makedirs(target_dir, 0o777, True)

    list = []
    pages = get_pages(soup)
    for page in pages:
        if page == '1':
            list += find_courses(soup, target_dir)
        else:
            content = load(url + '?page=' + page)
            soup = BeautifulSoup(content, 'html.parser')
            list += find_courses(soup, target_dir)

    list.sort(key=get_sort_key)
    metadata = {
        'id': id,
        'url': url,
        'name': name,
        'address': address,
        'courses': list 
    }
    save_metadata(metadata, target_dir)

    for course in list:
         parse_to_ics(course, target_dir)
    
    return metadata
