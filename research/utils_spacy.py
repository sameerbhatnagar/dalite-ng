from __future__ import unicode_literals
import os
import json
import re
import spacy
from django.conf import settings
from spacy.matcher import PhraseMatcher
from spacy_readability import Readability
import pandas as pd


def on_match(matcher, doc, id, matches):
    """
    call back function to be executed everytime a phrase is matched
    inside `get_matcher` function below
    """

    for m in matches:
        print(doc[m[1] - 2 : m[2] + 2])


def get_matcher(subject, nlp, on_match=None):
    """
    given a subject and nlp object,
    return a phrase mather object that has patterns from
    OpenStax textbook of that discipline
    """
    openstax_textbook_disciplines = {
        "Chemistry": ["chemistry-2e"],
        "Biology": ["biology-2e"],
        "Physics": [
            "university-physics-volume-3",
            "university-physics-volume-2",
            "university-physics-volume-1",
        ],
        "Statistics": ["introductory-statistics"],
    }

    books = openstax_textbook_disciplines[subject]
    keywords = {}
    for book in books:
        book_dir = os.path.join(
            settings.BASE_DIR, os.pardir, "textbooks", book
        )
        files = os.listdir(book_dir)
        keyword_files = [f for f in files if "key-terms" in f]
        for fn in keyword_files:
            with open(os.path.join(book_dir, fn), "r") as f:
                keywords.update(json.load(f))
    keywords_sorted = list(keywords.keys())
    keywords_sorted.sort()

    matcher = PhraseMatcher(nlp.vocab, attr="lower")
    patterns = [nlp.make_doc(text) for text in keywords_sorted]

    matcher.add("KEY_TERMS", patterns, on_match=on_match)

    return matcher


def extract_lexical_features(rationales, subject, nlp):
    """
    given array of rationales,
    return dict of arrays holding lexical features for each, including:
        - number of keywords
        - number of equations
    """
    lexical_features = {}
    matcher = get_matcher(subject=subject, nlp=nlp)
    try:
        lexical_features["num_keywords"] = [
            len(
                set(
                    [
                        str(doc[start:end])
                        for match_id, start, end in matcher(doc)
                    ]
                )
            )
            for doc in nlp.pipe(rationales, batch_size=50)
        ]
    except TypeError:
        pass
    eqn_re = re.compile(r"([\w\/^\*\.+-]+\s?=\s?[\w\/^\*\.+-]+)")
    lexical_features["num_equations"] = (
        pd.Series(rationales).str.count(eqn_re).to_list()
    )

    return lexical_features


def extract_syntactic_features(rationales, nlp):
    """
    given array of rationales,
    return dict of arrays holding synctatic features for each, including:
        - num_sents
        - num_verbs
        - num_conj
    """

    syntactic_features = {}

    syntactic_features["num_sents"] = [
        len(list(doc.sents)) for doc in nlp.pipe(rationales, batch_size=50)
    ]

    syntactic_features["num_verbs"] = [
        len([token.text for token in doc if token.pos_ == "VERB"])
        for doc in nlp.pipe(rationales, batch_size=50)
    ]

    syntactic_features["num_conj"] = [
        len(
            [
                token.text
                for token in doc
                if token.pos_ == "CCONJ" or token.pos_ == "SCONJ"
            ]
        )
        for doc in nlp.pipe(rationales, batch_size=50)
    ]

    return syntactic_features


def extract_readability_features(rationales, nlp):
    """
    given array of rationales,
    return dict of arrays holding synctatic features for each, including:
        - flesch_kincaid_grade_level
        - flesch_kincaid_reading_ease
        - dale_chall
        - automated_readability_index
        - coleman_liau_index
    """
    nlp.add_pipe(Readability())
    readability_features_list = [
        ("flesch_kincaid_grade_level"),
        ("flesch_kincaid_reading_ease"),
        ("dale_chall"),
        ("automated_readability_index"),
        ("coleman_liau_index"),
    ]

    readability_features = {}

    for f in readability_features_list:
        readability_features[f] = [
            getattr(doc._, f) for doc in nlp.pipe(rationales, batch_size=50)
        ]

    return readability_features


def get_features(
    group_name,
    path_to_data,
    syntactic=False,
    lexical=False,
    subject=None,
    readability=False,
):
    """
    append lexical, syntactic and readability features for rationales
    assumes csv file is already made for each group
    """
    prefix = "df_"
    nlp = spacy.load("en_core_web_sm")

    fpath = os.path.join(path_to_data, prefix + group_name + ".csv")
    df_answers = pd.read_csv(fpath)

    df_answers["rationale"] = df_answers["rationale"].fillna(" ")

    if syntactic:
        syntax_features = extract_syntactic_features(
            df_answers["rationale"], nlp=nlp
        )
        for f in syntax_features:
            df_answers.loc[:, f] = syntax_features[f]
    else:
        pass

    if readability:
        pass
    else:
        pass

    if lexical:
        lexical_features = extract_lexical_features(
            df_answers["rationale"], nlp=nlp, subject=subject
        )
        for f in lexical_features:
            df_answers.loc[:, f] = lexical_features[f]

    else:
        pass

    return df_answers
