# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import codecs
import io
import os
import pickle
import zipfile
from itertools import product

import requests

from .utils import done_print, load_print


def read_data(language, urls, left_to_right):
    path = os.path.join(os.path.dirname(__file__), ".data", language)

    pkl_path = os.path.join(path, "data.pkl")

    if os.path.exists(pkl_path):
        load_print("Reading pickled file for {}...".format(language))
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)
        done_print("Read pickled file for {}.".format(language))

    else:
        data = {
            gram + 1: read_gram_file(language, gram + 1, url, path)
            for gram, url in enumerate(urls)
        }
        data = {
            gram: {
                "".join(g): val.get("".join(g), 1e-16)
                for g in product(*["".join(data[1].keys())] * gram)
            }
            for gram, val in data.items()
        }
        data = {"n_grams": data, "left_to_right": left_to_right}
        load_print("Pickling data for {}...".format(language))
        with open(pkl_path, "wb") as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        done_print("Pickled data for {}.".format(language))

    return data


def read_gram_file(language, gram, url, path):
    path = os.path.join(path, "{}-grams.txt".format(gram))
    if os.path.exists(path):
        load_print("Reading {}-gram file for {}...".format(gram, language))
        with open(path, "r") as f:
            f.readline()
            lines = [line.strip().split() for line in f]
            data = {line[0]: float(line[1]) for line in lines}
        done_print("Read {}-gram file for {}.".format(gram, language))
    else:
        data = download_gram_file(language, gram, url, path)

    return data


def download_gram_file(language, gram, url, path):
    load_print("Downloading {}-gram file for {}...".format(gram, language))

    resp = requests.get(url)
    resp.raise_for_status()

    if url.endswith("zip"):
        with zipfile.ZipFile(io.BytesIO(resp.content)) as f_zip:
            with f_zip.open(os.path.basename(url)[:-4]) as f:
                lines = [line.strip().split() for line in f]
                data = {
                    line[0].decode("utf-8").lower(): float(line[1])
                    for line in lines
                }

    else:
        lines = [
            line.strip().split()
            for line in resp.content.decode("utf-8").split("\n")
            if line
        ]
        data = {line[0].lower(): float(line[1]) for line in lines}

    total = sum(data.values())
    data = {key: val / total for key, val in data.items()}

    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with codecs.open(path, "w", "utf8") as f:
        f.write("n-gram\tfrequency\n")
        for n_gram, frequency in data.items():
            f.write("{}\t{}\n".format(n_gram, frequency))

    done_print("Downloaded {}-gram file for {}.".format(gram, language))
    return data
