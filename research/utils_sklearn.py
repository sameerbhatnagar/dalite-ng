import os
import datetime

import pandas as pd
import numpy as np
from scipy import stats


from sklearn.preprocessing import QuantileTransformer, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_selection import SelectKBest, f_regression

from research.utils_load_data import (
    get_convincingness_ratio,
    extract_timestamp_features,
)

from research.utils_spacy import get_features

RANDOM_SEED = 123


def get_features_and_save(path_to_data):
    """
    calculate and save lexical,syntax and readability features
    """
    fpath_data_inventory = os.path.join(
        path_to_data, "data_inventory_research_consent_True_clean.csv",
    )

    with open(fpath_data_inventory, "r") as f:
        DATA_INVENTORY = pd.read_csv(fpath_data_inventory)

    disciplines = (
        DATA_INVENTORY.groupby(["discipline"])["N_answers_PI"]
        .sum()
        .sort_values()
        .index[-3:]
        .to_list()
    )
    DATA_INVENTORY["semester"] = DATA_INVENTORY["season"].str.cat(
        DATA_INVENTORY["year"].map(str)
    )
    semesters = (
        DATA_INVENTORY.groupby(["semester"])["N_answers_PI"]
        .sum()
        .sort_values()
        .index[-4:]
        .to_list()
    )

    df = pd.DataFrame()
    for discipline in disciplines:
        df_discipline = pd.DataFrame()

        for semester in semesters:

            df_semester = pd.DataFrame()

            # need to calculate features for all
            group_names = DATA_INVENTORY.loc[
                (
                    (DATA_INVENTORY["discipline"] == discipline)
                    & (DATA_INVENTORY["semester"] == semester)
                ),
                "name",
            ]

            for group_name in group_names:
                print(group_name)
                print(
                    "{} - calculating features".format(datetime.datetime.now())
                )
                df_group = get_features(
                    group_name=group_name,
                    path_to_data=path_to_data,
                    subject=discipline,
                )

                df_group["group"] = group_name
                df_semester = pd.concat([df_semester, df_group], sort=False)
            df_semester["semester"] = semester
            df_discipline = pd.concat([df_discipline, df_semester], sort=False)

        df_discipline["discipline"] = discipline
        df = pd.concat([df, df_discipline], sort=False)

    df = get_convincingness_ratio(df)

    df = extract_timestamp_features(df)

    fpath_all = os.path.join(path_to_data, "all_groups_with_features.csv")

    df.to_csv(fpath_all)

    return df


def filter_data(df, feature_columns_numeric):
    """
    """
    MIN_TIMES_SHOWN = 3
    df_filtered_times_shown = df[df["times_shown"] > MIN_TIMES_SHOWN]

    df_filtered = df_filtered_times_shown[
        (
            np.abs(
                stats.zscore(df_filtered_times_shown[feature_columns_numeric])
            )
            < 3
        ).all(axis=1)
    ]

    return df_filtered


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
    n_samples, feature_columns_numeric, feature_columns_categorical
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
            (
                "std_scaler",
                QuantileTransformer(
                    n_quantiles=n_samples, output_distribution="normal"
                ),
            ),
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
            (
                "feature_selector",
                SelectKBest(f_regression, k=int(n_samples / 10)),
            ),
        ]
    )

    return full_pipeline
