import gzip
from json import load, dump

def save_to_disk(filename, json_object, compress=True):
    if compress:
        f = gzip.open(filename, 'wt')
    else:
        f = open(filename, 'wt')
    try:
        print("saving ", filename)
        dump(json_object, f, indent=1)
    finally:
        f.close()

def load_from_disk(filename, compress=True):
    if compress:
        f = gzip.open(filename, 'rt')
    else:
        f = open(filename, 'rt')

    try:
        return load(f)
    finally:
        f.close()
