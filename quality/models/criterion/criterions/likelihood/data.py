# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import os
import pickle
import zipfile
from itertools import product

import requests

from src.utils import done_print, load_print

language_list = {"english", "french"}


def read_data(language):
    path = os.path.join(os.path.dirname(__file__), ".data", language)

    pkl_path = os.path.join(path, "data.pkl")

    if os.path.exists(pkl_path):
        load_print("Reading pickled file for {}...".format(language))
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)
        done_print("Read pickled file for {}.".format(language))

    else:
        data = {
            gram: read_gram_file(language, gram, path) for gram in (1, 2, 3)
        }
        data = {
            gram: {
                "".join(g): val.get("".join(g), 1e-16)
                for g in product(*["".join(data[1].keys())] * gram)
            }
            for gram, val in data.items()
        }
        load_print("Pickling data for {}...".format(language))
        with open(pkl_path, "wb") as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        done_print("Pickled data for {}.".format(language))

    return data


def read_gram_file(language, gram, path):
    path = os.path.join(path, "{}-grams.txt".format(gram))
    if os.path.exists(path):
        load_print("Reading {}-gram file for {}...".format(gram, language))
        with open(path, "r") as f:
            f.readline()
            lines = [line.strip().split() for line in f]
            data = {line[0]: float(line[1]) for line in lines}
        done_print("Read {}-gram file for {}.".format(gram, language))
    else:
        data = download_gram_file(language, gram, path)

    return data


def download_gram_file(language, gram, path):
    load_print("Downloading {}-gram file for {}...".format(gram, language))
    base_url = "http://practicalcryptography.com/media/cryptanalysis/files"
    if language == "english":
        if gram == 1:
            url = "{}/english_monograms.txt".format(base_url)
        elif gram == 2:
            url = "{}/english_bigrams_1.txt".format(base_url)
        elif gram == 3:
            url = "{}/english_trigrams.txt.zip".format(base_url)
        else:
            raise ValueError(
                "There is no file for {}-grams in {language}.".format(gram)
            )
    elif language == "french":
        if gram == 1:
            url = "{}/french_monograms.txt".format(base_url)
        elif gram == 2:
            url = "{}/french_bigrams.txt".format(base_url)
        elif gram == 3:
            url = "{}/french_trigrams.txt.zip".format(base_url)
        else:
            raise ValueError(
                "There is no file for {}-grams in {language}.".format(gram)
            )
    else:
        raise ValueError(
            "There is no file for {}-grams in {}.".format(gram, language)
        )

    resp = requests.get(url)

    if url.endswith("zip"):
        with zipfile.ZipFile(io.BytesIO(resp.content)) as f_zip:
            with f_zip.open(os.path.basename(url)[:-4]) as f:
                lines = [line.strip().split() for line in f]
                data = {
                    line[0].decode().lower(): int(line[1]) for line in lines
                }

    else:
        lines = [
            line.strip().split()
            for line in resp.content.decode().split("\n")
            if line
        ]
        data = {line[0].lower(): int(line[1]) for line in lines}

    total = sum(data.values())
    data = {key: val / total for key, val in data.items()}

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("n-gram\tfrequency\n")
        for n_gram, frequency in data.items():
            f.write("{}\t{}\n".format(n_gram, frequency))

    done_print("Downloaded {}-gram file for {}.".format(gram, language))
    return data
