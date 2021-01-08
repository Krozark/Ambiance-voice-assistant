#!/usr//bin/env python
import json
import sys
import requests
import os

filename = sys.argv[1]
data = json.load(open(filename, "r"))

title = data["log"]["pages"][0]["title"].rsplit("/", 1)[-1].split(".")[0]

os.makedirs(title, exist_ok=True)

i = 0
for x in data["log"]['entries']:
    for h in x["response"]["headers"]:
        if h["value"] in ("application/ogg", "audio/ogg"):
            url = x["request"]["url"]
            filename = url.rsplit("/", 1)[-1]
            file_path = os.path.join(title, filename)
            print("Download %s" % url)
            with requests.Session() as session:
                with session.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(file_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            f.write(chunk)
            i += 1
print("Download %s files" % i)
