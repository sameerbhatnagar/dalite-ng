import os
import json
import spacy

from collections import Counter
import pandas as pd


from sklearn.preprocessing import QuantileTransformer, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from research.utils_load_data import (
    get_convincingness_ratio,
    extract_timestamp_features,
    get_answers_df,
)

from research.utils_spacy import (
    extract_lexical_features,
    extract_syntactic_features,
    extract_readability_features,
)

RANDOM_SEED = 123


def append_features_and_save(path_to_data, group_name):

    fpath = os.path.join(path_to_data, "data_inventory.json")
    with open(fpath, "r") as f:
        DATA_INVENTORY = json.load(f)

    prefix = "df_"
    fpath = os.path.join(path_to_data, prefix + group_name + ".csv")

    try:
        df = pd.read_csv(fpath)
    except FileNotFoundError:
        print("get_answers_df for " + group_name)
        df = get_answers_df(group_name)
        df.to_csv(fpath)

    df["rationale"] = df["rationale"].fillna(" ")

    df = get_convincingness_ratio(df)

    nlp = spacy.load("en_core_web_sm")

    possible_disciplines = [
        [c["discipline"] for c in s["courses"] if c["name"] == group_name]
        for s in DATA_INVENTORY
    ]
    subject = [d[0] for d in possible_disciplines if len(d) > 0][0]

    print("computing lexical_features")
    lexical_features = extract_lexical_features(
        rationales=df["rationale"], nlp=nlp, subject=subject
    )
    for key in lexical_features:
        print(key)
        print(Counter(lexical_features[key]))

    print("computing syntax_features")
    syntax_features = extract_syntactic_features(
        rationales=df["rationale"], nlp=nlp,
    )
    for key in syntax_features:
        print(key)
        print(Counter(syntax_features[key]))

    readability_features = extract_readability_features(
        rationales=df["rationale"], nlp=nlp,
    )
    df = (
        df.join(pd.DataFrame(lexical_features))
        .join(pd.DataFrame(syntax_features))
        .join(pd.DataFrame(readability_features))
    )

    df = extract_timestamp_features(df)

    fpath = os.path.join(
        path_to_data,
        "with_features",
        prefix + group_name + "_with_features.csv",
    )
    df.to_csv(fpath)

    return


def split_train_test(data, target, test_fraction=0.2):
    """
    given:
     - DataFrame
     - split_axis: name of feature for stratification in training and test set
     - target variable name
     - test_fraction (optional)
    returns:
        - train_set
        - train labels
        - test set
        - test labels
    """

    strat_split = StratifiedShuffleSplit(
        n_splits=1, test_size=test_fraction, random_state=RANDOM_SEED
    )

    for train_index, test_index in strat_split.split(data, data[target]):
        train_set = data.iloc[train_index].drop(target, axis=1).copy()
        train_labels = data.iloc[train_index][target]
        test_set = data.iloc[test_index]
        test_labels = data.iloc[test_index][target]

    return train_set, train_labels, test_set, test_labels


def get_feature_transformation_pipeline(
    feature_columns_numeric, feature_columns_categorical
):
    """
    given:
        - array indicating which columns are numeric features
        - array indicating which columns are categorical features
    return:
        - numpy array of transformed data, ready for model
    """

    num_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer()),
            ("std_scaler", QuantileTransformer(output_distribution="normal")),
        ]
    )

    tfidf_tranformer_pipe = Pipeline(
        [
            ("count", CountVectorizer(stop_words="english")),
            ("tfidf", TfidfTransformer()),
        ]
    )

    full_pipeline = ColumnTransformer(
        [
            ("num_pipeline", num_pipeline, feature_columns_numeric),
            ("cat_pipeline", OneHotEncoder(), feature_columns_categorical),
            ("tfidf", tfidf_tranformer_pipe, "rationale"),
        ]
    )

    return full_pipeline
