import requests
import re
import dateparser

def load(url):
    return requests.get(url).text

def strip(text):
    return re.sub(r'\s+', ' ', text.strip())

def to_datetime(text):
    return dateparser.parse(text, languages=['pl'])
