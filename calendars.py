import json

def load_sources():
    with open("sources.json", mode="r", encoding="utf-8") as file:
        return json.load(file)

sources = load_sources()
print(sources)