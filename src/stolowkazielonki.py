from utils import *
from bs4 import BeautifulSoup
from datetime import timedelta
from icalendar import Calendar, Event
import os
import json

url_przerwy = 'https://szkola-zielonki.pl/stolowka/'
url_menu = 'https://szkola-zielonki.pl/tygodniowe-menu/'

def get_dishes(tr):
    tds = tr.find_all('td')
    return {
        'date': to_datetime(strip(tds[0].text)),
        'soup': strip(tds[3].text),
        'main': strip(tds[4].text),
    }

def get_classes(soup):
    classes = []
    trs = soup.find_all('tr')
    for idx, tr in enumerate(trs):
        if (idx == 0):
            continue
        tds = tr.find_all('td')
        classes += tds[1].text.replace(r' ', '').split(',')
    return sorted(classes)

def get_all_breaks(soup):
    list = []
    trs = soup.find_all('tr')
    for idx, tr in enumerate(trs):
        if (idx == 0):
            continue
        tds = tr.find_all('td')
        list.append({
            'time': strip(tds[0].text).split(' – '),
            'day0': tds[1].text.replace(r' ', '').split(','),
            'day1': tds[2].text.replace(r' ', '').split(','),
            'day2': tds[3].text.replace(r' ', '').split(','),
            'day3': tds[4].text.replace(r' ', '').split(','),
            'day4': tds[5].text.replace(r' ', '').split(',')
        })
    return list

def find_breaks(clazz, all_breaks):
    found = {}
    for day in [ 'day0', 'day1', 'day2', 'day3', 'day4']:
        for breaq in all_breaks:
            if clazz in breaq[day]:
                found[day] = breaq['time']
    return found


def get_breaks_for_classes():
    content = load(url_przerwy)
    soup = BeautifulSoup(content, 'html.parser')

    all_breaks = get_all_breaks(soup)
    classes = get_classes(soup)

    breaks_for_classes = { }
    for clazz in classes:
        breaks_for_classes[clazz] = find_breaks(clazz, all_breaks)

    return breaks_for_classes
        
def get_menu(soup):
    menu = []
    tables = soup.find_all('table')  
    for table in tables:
        trs = table.find_all('tr')
        for tr in trs:
            dishes = get_dishes(tr)
            if dishes['date'] != None:
                menu.append(get_dishes(tr))
    return menu

def to_timedelta(text):
    s = text.split(':')
    return timedelta(hours=int(s[0]), minutes=int(s[1]))

def get_events(breaks_for_class, menus):
    events = []
    for menu in menus:
        weekday = menu['date'].weekday()
        breaq = breaks_for_class['day' + str(weekday)]
        event = Event()
        event.add('summary', 'Obiad')
        event.add('description', menu['soup'] + '\n\n' + menu['main'])
        event.add('dtstart', menu['date'] + to_timedelta(breaq[0]))
        event.add('dtend', menu['date'] + to_timedelta(breaq[1]))
        events.append(event)
    return events

def to_ics(clazz, events, target_dir):
    cal = Calendar()
    cal.add('prodid', '-//Kalendarz Szkolny//example.com//')
    cal.add('version', '2.0')
    for event in events:
        cal.add_component(event)

    filename = clazz + '.ics'
    f = open(target_dir + '/' + filename, "wb")
    f.write(cal.to_ical())
    f.close()
    print('DONE: ' + f.name)

def save_metadata(metadata, target_dir):
    with open(target_dir + '/metadata.json', 'w') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

def tygodniowemenu(target_dir):
    content = load(url_menu)
    soup = BeautifulSoup(content, 'html.parser')

    menu = get_menu(soup)
    breaks_for_classes = get_breaks_for_classes()

    os.makedirs(target_dir, 0o777, True)

    list = []
    for clazz in breaks_for_classes:
        to_ics(clazz, get_events(breaks_for_classes[clazz], menu), target_dir)
        list.append({
            'name': clazz.upper(),
            'ics': target_dir + '/' + clazz + '.ics'
        })
    save_metadata(list, target_dir)
    return list
