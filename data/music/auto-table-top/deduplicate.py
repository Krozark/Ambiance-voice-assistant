#!/bin/env python
import hashlib
import os
from collections import defaultdict


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()



map = defaultdict(list)

for root, subfolder, files in os.walk("."):
    for item in files:
        path = os.path.join(root, item)
        h = md5(path)
        print("%s => %s" % (path, h))
        map[h].append(path)

print("*********************")
print("* duplicated items: *")
print("*********************")
for key, values in map.items():
    if len(values) > 1:
        print(", ".join(values))
        yn = input("delete ?[Yn]")
        if yn == "Y":
            print("Remove %s " % values[1])
            os.remove(values[1])
