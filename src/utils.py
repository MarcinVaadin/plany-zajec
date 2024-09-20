import json
import requests
import re
import dateparser


def load(url):
    return requests.get(url).text


def strip(text):
    return re.sub(r"\s+", " ", text.strip())


def to_datetime(text):
    return dateparser.parse(text, languages=["pl"])


def save_metadata(metadata, target_dir):
    with open(target_dir + "/metadata.json", "w") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
