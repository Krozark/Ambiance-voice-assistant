#!/bin/env python
import json
import sys
import requests

filename = sys.argv[1]
data = json.load(open(filename, "r"))

i = 0
for x in data["log"]['entries']:
    for h in x["response"]["headers"]:
        if h["value"] in ("application/ogg", "audio/ogg"):
            url = x["request"]["url"]
            filename = url.rsplit("/", 1)[-1]
            print("Download %s" % url)
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            i += 1
print("Download %s files" % i)
