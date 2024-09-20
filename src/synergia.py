import requests
import os

from utils import *

page_url = "https://synergia.librus.pl"


def get_calendar(login, password):
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36"
        }
    )

    session.get(
        "https://api.librus.pl/OAuth/Authorization?client_id=46&response_type=code&scope=mydata"
    )
    session.post(
        "https://api.librus.pl/OAuth/Authorization?client_id=46",
        {
            "action": "login",
            "login": login,
            "pass": password,
        },
    )
    session.get("https://api.librus.pl/OAuth/Authorization/2FA?client_id=46")
    response = session.get(
        "https://synergia.librus.pl/eksporty/ical/eksportuj/planUcznia"
    )
    return response.text


def synergia(config, target_dir):
    os.makedirs(target_dir, 0o777, True)
    metadata = []
    for clazz in config:
        user = os.environ[clazz["user_env"]]
        password = os.environ[clazz["pass_env"]]
        ics = target_dir + "/" + clazz["id"] + ".ics"
        calendar = get_calendar(user, password)
        f = open(ics, "w")
        f.write(calendar)
        f.close()
        metadata.append({"name": clazz["id"].upper(), "ics": ics})
        print("DONE: " + f.name)
    save_metadata(metadata, target_dir)

    return metadata
