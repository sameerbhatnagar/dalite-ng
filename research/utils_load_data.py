from __future__ import unicode_literals

import pandas as pd
import numpy as np
from django_pandas.io import read_frame
from django.db.models import Max

import os
import re
import datetime
import itertools
from collections import Counter
import pandas as pd
from django.db.models import Count
from peerinst.models import (
    StudentGroup,
    ShownRationale,
    Teacher,
    Answer,
    Assignment,
    Question,
)
from tos.models import Consent

MIN_STUDENTS = 10
MIN_PI_QUESTIONS = 5
MIN_TIMES_SHOWN = 3
MIN_ANSWERS = MIN_STUDENTS * MIN_PI_QUESTIONS

SEMESTERS = [
    (1, "WINTER"),
    (2, "SUMMER"),
    (3, "FALL"),
]

MONTH_SEMESTER_MAP = {
    1: SEMESTERS[0],
    2: SEMESTERS[0],
    3: SEMESTERS[0],
    4: SEMESTERS[0],
    5: SEMESTERS[1],
    6: SEMESTERS[1],
    7: SEMESTERS[1],
    8: SEMESTERS[2],
    9: SEMESTERS[2],
    10: SEMESTERS[2],
    11: SEMESTERS[2],
    12: SEMESTERS[2],
}


def get_group_semester(df):

    df["datetime_second"] = pd.to_datetime(df["datetime_second"])
    df.index = df["datetime_second"]

    try:
        month, year = (
            df.groupby([df.index.month, df.index.year]).size().idxmax()
        )
    except ValueError:
        month, year = None, None

    return (month, year)


def get_group_metadata(group, path_to_data=None, research_consent=True):
    """
    set `research_consent` to False if you want to include all students,
    even  those who have refused consent for their data to be used for
    academic research. This should only be done for generating
    internal operational reports. Default is set to True.
    """
    df_answers = get_answers_df(group.name, path_to_data, research_consent)

    (
        pi_question_list,
        ro_question_list,
        pi_question_list_all_correct,
    ) = get_pi_question_list(group.name)

    all_questions = (
        pi_question_list + ro_question_list + pi_question_list_all_correct
    )

    if group.teacher.last():
        institution = ",".join(
            group.teacher.last()
            .institutions.all()
            .values_list("name", flat=True)
        )
    else:
        institution = "Unknown"

    month, year = get_group_semester(df_answers)
    semester_season = MONTH_SEMESTER_MAP[month][1]

    d = {
        "year": str(year),
        "season": semester_season,
        "institution": institution,
        "teachers": ",".join(
            group.teacher.all().values_list("user__username", flat=True)
        ),
        "discipline": ",".join(
            Counter(
                [q.discipline.title for q in all_questions if q.discipline]
            ).keys()
        ),
        "name": group.name,
        "title": group.title,
        "N_students": len(filter_student_list(group.name, research_consent)),
        "N_questions_PI": len(pi_question_list),
        "N_answers_PI": df_answers.groupby(["question_type"])["question__id"]
        .size()
        .get("PI"),
        "N_questions_PI_AC": len(pi_question_list_all_correct),
        "N_answers_PI_AC": df_answers.groupby(["question_type"])[
            "question__id"
        ]
        .size()
        .get("PI_AC"),
        "N_questions_RO": len(ro_question_list),
        "N_answers_RO": df_answers.groupby(["question_type"])["question__id"]
        .size()
        .get("RO"),
    }

    return d


def filter_student_list(group_name, research_consent=True):

    sg = StudentGroup.objects.get(name=group_name)
    student_list_full = sg.students.values_list("student__username", flat=True)
    # remove students who have not given consent
    usernames_to_exclude = (
        Consent.objects.filter(tos__role="student")
        .values("user__username")
        .annotate(Max("datetime"))
        .filter(accepted=False)
        .values_list("user", flat=True)
    )
    usernames_tos = (
        Consent.objects.filter(tos__role="student")
        .values("user__username")
        .annotate(Max("datetime"))
        .filter(accepted=True)
        .values_list("user", flat=True)
    )

    teacher_user_names = Teacher.objects.all().values_list("user", flat=True)
    student_list = (
        student_list_full.exclude(student__in=usernames_to_exclude)
        .exclude(student__in=teacher_user_names)
        .filter(student__in=usernames_tos)
    )

    if research_consent:
        return student_list
    else:
        return student_list_full


def get_assignment_list(group_name):
    sg = StudentGroup.objects.get(name=group_name)
    student_list_full = sg.students.values_list("student__username", flat=True)
    assignment_list_qs = sg.studentgroupassignment_set.values_list(
        "assignment", flat=True
    )
    if assignment_list_qs.count() == 0:
        assignment_list = (
            Answer.objects.filter(user_token__in=student_list_full)
            .values("assignment")
            .annotate(n=Count("assignment"))
            .filter(n__gt=10)
            .values_list("assignment", flat=True)
        )
        assignment_list_qs = Assignment.objects.filter(
            identifier__in=assignment_list
        )
    return assignment_list_qs


def get_pi_question_list(group_name):

    sg = StudentGroup.objects.get(name=group_name)
    student_list_full = sg.students.values_list("student__username", flat=True)
    assignment_list = sg.studentgroupassignment_set.values_list(
        "assignment", flat=True
    )
    pi_question_list = []
    ro_question_list = []

    if len(assignment_list) > 0:
        sg_assignment_list = sg.studentgroupassignment_set.filter(
            distribution_date__isnull=False
        )

        for _a in sg_assignment_list:
            pi_question_list.extend(_a.assignment.questions.filter(type="PI"))
            ro_question_list.extend(_a.assignment.questions.filter(type="RO"))

    # LTI groups, keep assignments that have at least 10 answers
    if assignment_list.count() == 0:
        assignment_list = (
            Answer.objects.filter(user_token__in=student_list_full)
            .values("assignment")
            .annotate(n=Count("assignment"))
            .filter(n__gt=10)
            .values_list("assignment", flat=True)
        )
        assignment_list_qs = Assignment.objects.filter(
            identifier__in=assignment_list
        )

        for _a in assignment_list_qs:
            pi_question_list.extend(_a.questions.filter(type="PI"))
            ro_question_list.extend(_a.questions.filter(type="RO"))

    # remove those where all answerchoices are marked as correct
    pi_question_list_all_correct = [
        q
        for q in pi_question_list
        if all(q.answerchoice_set.all().values_list("correct", flat=True))
    ]
    pi_question_list = [
        q for q in pi_question_list if q not in pi_question_list_all_correct
    ]
    return pi_question_list, ro_question_list, pi_question_list_all_correct


def filter_groups_on_min_students(group_name, research_consent=True):
    student_list_filtered = filter_student_list(group_name, research_consent)
    sg = StudentGroup.objects.get(name=group_name)
    student_list_full = sg.students.values_list("student__username", flat=True)
    message = "{}/{} students accepted consent".format(
        len(student_list_filtered), student_list_full.count()
    )
    if len(student_list_filtered) < MIN_STUDENTS:
        return (None, message)
    else:
        return (group_name, message)


def filter_groups_on_min_qs(group_name):
    (
        pi_question_list,
        ro_question_list,
        pi_question_list_all_correct,
    ) = get_pi_question_list(group_name)

    message = "{} pi questions;{} ro questions,{} AC questions".format(
        len(pi_question_list),
        len(ro_question_list),
        len(pi_question_list_all_correct),
    )
    if len(pi_question_list + pi_question_list_all_correct) < MIN_PI_QUESTIONS:
        return (None, message)
    else:
        return (group_name, message)


def filter_groups_on_min_a(group_name, research_consent=True):
    _group_name, _message = filter_groups_on_min_students(
        group_name, research_consent
    )
    if _group_name:
        student_list_filtered = filter_student_list(
            group_name, research_consent
        )
        assignment_list = get_assignment_list(group_name)
        (
            pi_question_list,
            ro_question_list,
            pi_question_list_all_correct,
        ) = get_pi_question_list(group_name)
        answers = (
            Answer.objects.filter(
                user_token__in=student_list_filtered,
                assignment_id__in=assignment_list,
                question_id__in=pi_question_list,
            )
            .exclude(user_token="")
            .values(
                "id",
                "user_token",
                "rationale",
                "first_answer_choice",
                "second_answer_choice",
                "question__id",
                "chosen_rationale__id",
            )
        )
        df = read_frame(answers)
        answers_per_student = df.groupby("user_token").size()
        num_engaged_students = len(
            answers_per_student[answers_per_student > MIN_PI_QUESTIONS].index
        )

        message = "{} students completed at least {} questions each".format(
            num_engaged_students, MIN_PI_QUESTIONS
        )
        if num_engaged_students > MIN_STUDENTS:
            return (group_name, message)
        else:
            return (None, message)
    else:
        return (None, _message)


def filter_groups(group_name, research_consent=True):
    _group_name, _message = filter_groups_on_min_students(
        group_name, research_consent
    )
    if _group_name:
        __group_name, __message = filter_groups_on_min_qs(group_name)
        if __group_name:
            ___group_name, ___message = filter_groups_on_min_a(
                group_name, research_consent
            )
            if ___group_name:
                return group_name, None
            else:
                return None, ___message
        else:
            return None, __message
    else:
        return None, _message


# utility function to append firt correct
def append_first_correct_column(df_answers, id_column_name):
    """
    Arguments:
        - a dataframe with serialized answer objects as rows,
        - the name of the column that holds the answer_id
    Return:
        - same dataframe with appended column with 1/0
        if first answer choice was correct
    """
    correct_dict = {}
    correct_dict["answer_id"] = []
    correct_dict["first_correct"] = []
    qs = Answer.objects.filter(id__in=df_answers[id_column_name].to_list())
    for a in qs:
        correct_dict["answer_id"].append(a.id)
        correct_dict["first_correct"].append(a.first_correct)
    df_first_correct = pd.DataFrame.from_dict(correct_dict)

    df = pd.merge(
        df_answers,
        df_first_correct,
        left_on=id_column_name,
        right_on="answer_id",
    )
    return df


# utility print function
# def print_rationales(a_list):
#     for a in Answer.objects.filter(id__in=a_list):
#         print("Question:")
#         print(a.question.text)
#         if a.question.image:
#             print(Image(url="." + a.question.image.url))
#         print("\n")
#         print("Student Rationale")
#         print(a.rationale)
#         print("\n\n\n\n")
#     return


def shown_answer_ids(shown_for_answer_id, justiceX=pd.DataFrame()):
    """
    given Answer id, return dataframe with
    columns shown_answer_id,shown_word count)
    of the answers that were shown to the student
    """
    if not justiceX.empty:
        pattern = re.compile("[ ''\[\]]")  # noqa

        string_list = justiceX.loc[
            justiceX["id"] == shown_for_answer_id, "rationales"
        ].iat[0]
        try:
            return [
                int(i)
                for i in re.sub(pattern, "", string_list).split(",")
                if str(i) != "nan"
            ]
        except TypeError as e:
            #             print(e)
            #             print(string_list)
            return []

    else:
        shown = ShownRationale.objects.filter(
            shown_for_answer=shown_for_answer_id
        ).values_list("shown_answer__id", flat=True)
    return shown


def get_longest_shown_rationale_id(answer_id, justiceX=pd.DataFrame()):

    shown_ids = shown_answer_ids(answer_id, justiceX)

    if not justiceX.empty:
        shown_rationales = justiceX.loc[
            justiceX["id"].isin(shown_ids), "rationale"
        ].tolist()
    else:
        shown_rationales = Answer.objects.filter(id__in=shown_ids).values_list(
            "rationale", flat=True
        )

    #     print(shown_rationales)
    shown_word_counts = [
        len(_a.split()) for _a in shown_rationales
    ]  # if str(_a)!="nan"]

    if len(shown_word_counts) > 0:
        return shown_ids[np.argmax(shown_word_counts)]
    else:
        return None


def get_convincingness_ratio(df_answers):

    df_times_chosen = (
        df_answers["chosen_rationale__id"]
        .value_counts()
        .to_frame()
        .reset_index()
        .rename(
            columns={"chosen_rationale__id": "times_chosen", "index": "id"}
        )
    )

    df = pd.merge(df_answers, df_times_chosen, on="id", how="left")
    df["times_chosen"] = df["times_chosen"].fillna(0)

    df_shown = read_frame(
        ShownRationale.objects.filter(
            shown_for_answer__pk__in=df_answers["id"].to_list()
        ).values("shown_for_answer__id", "shown_answer__id")
    )

    df_times_shown = (
        df_shown["shown_answer__id"]
        .value_counts()
        .to_frame()
        .reset_index()
        .rename(columns={"shown_answer__id": "times_shown", "index": "id"})
    )

    df = pd.merge(df, df_times_shown, on="id", how="left")

    df["times_shown"] = df["times_shown"].fillna(0)

    # prior of 1/14 = 1/7 chance of being chosen at random if shown once
    #                               * 1/2 chance students choose their
    # own rationale
    df["chosen_ratio"] = (df["times_chosen"] + 1) / (df["times_shown"] + 14)

    return df


def get_answers_df(group_name, path_to_data=None, research_consent=True):
    """
    given group name, return df_answers
    """

    if group_name == "justiceX":  # not in same db
        pass
        # df_answers = read_from_harvard_db2()
        # id of longest rationale
        # df_answers["l_s_r_id"] = df_answers["id"].apply(
        #     lambda x: get_longest_shown_rationale_id(x, justiceX=df_answers)
        # )

    else:
        assignment_list = get_assignment_list(group_name)

        (
            pi_question_list,
            ro_question_list,
            pi_question_list_all_correct,
        ) = get_pi_question_list(group_name)
        q_type_map = {
            **{q.pk: "PI" for q in pi_question_list},
            **{q.pk: "PI_AC" for q in pi_question_list_all_correct},
            **{q.pk: "RO" for q in ro_question_list},
        }

        filtered_student_list = filter_student_list(
            group_name, research_consent
        )

        # load data
        a_qs = Answer.objects.filter(
            user_token__in=filtered_student_list,
            assignment_id__in=assignment_list,
            question_id__in=pi_question_list
            + pi_question_list_all_correct
            + ro_question_list,
        )

        qs = a_qs.values(
            "id",
            "user_token",
            "rationale",
            "first_answer_choice",
            "second_answer_choice",
            "question__id",
            "chosen_rationale__id",
            "datetime_start",
            "datetime_first",
            "datetime_second",
        )

        df_answers = read_frame(qs)

        df_answers["question_type"] = df_answers["question__id"].map(
            q_type_map
        )

        # responses for students who repeat the same course with same
        # assignments need to be filtered out

        month, year = get_group_semester(df_answers)
        if month:
            semester_int = MONTH_SEMESTER_MAP[month][0]

            semester_months = [
                m
                for m, s in MONTH_SEMESTER_MAP.items()
                if s[0] == semester_int
            ]

            df_answers = df_answers[
                pd.to_datetime(df_answers["datetime_second"]).dt.month.isin(
                    semester_months
                )
            ]

        # append first_correct
        df_answers = append_first_correct_column(
            df_answers=df_answers, id_column_name="id"
        )

        # id of longest rationale
        # df_answers["l_s_r_id"] = df_answers["id"].apply(
        #     lambda x: get_longest_shown_rationale_id(x)
        # )

    # rest of features are same for all groups

    # word counts
    df_answers["rationale_word_count"] = df_answers.rationale.str.count(
        "\w+"
    )  # noqa

    # switch
    df_answers.loc[
        df_answers["first_answer_choice"]
        != df_answers["second_answer_choice"],
        "switch",
    ] = 1

    # switch rationale, same answerchoice
    df_answers.loc[
        (
            (
                df_answers["first_answer_choice"]
                == df_answers["second_answer_choice"]
            )
            & (df_answers["chosen_rationale__id"].isna() == False)  # noqa
        ),
        "switch_rationale",
    ] = 1

    if path_to_data:
        prefix = "df_"
        group_name_fn = re.sub("/", "_", group_name)
        fpath = os.path.join(path_to_data, prefix + group_name_fn + ".csv")
        df_answers.to_csv(fpath)

    return df_answers


def extract_timestamp_features(df):
    """
    given a dataframe with columns
        - with timestamps for when:
            - student started question
            - student submitted first_answer_choice + rationale
            - student submits second_answer_choice,
        - the question id,

    Return same dataframe with extra columns:
        - a numerical rank for when the student completed their rationale
        with respect to other students
        - time spent writing rationale and first answer first_answer_choice
        - time spent reading and selecting second answer choice
    """

    for c in ["datetime_start", "datetime_first", "datetime_second"]:
        df[c] = pd.to_datetime(df[c], utc=True)

    # earliest students have lowest rank
    df["a_rank_by_time"] = df.groupby("question__id")["datetime_second"].rank(
        pct=True
    )

    df["time_writing"] = (
        df["datetime_first"] - df["datetime_start"]
    ).dt.seconds

    df["time_reading"] = (
        df["datetime_second"] - df["datetime_first"]
    ).dt.seconds

    return df


def build_data_inventory(path_to_data, research_consent=True):
    """
    """

    rejected_groups = []
    data_inventory = []

    all_groups = StudentGroup.objects.all()

    for i, group in enumerate(all_groups):

        print("{}- {}".format(i, group.name))

        _group_name, _message = filter_groups(
            group_name=group.name, research_consent=research_consent
        )

        if _group_name:
            data_inventory.append(get_group_metadata(group, path_to_data))
        else:
            rejected_groups.append(
                {
                    "group": group.name,
                    "title": group.title,
                    "teacher": group.teacher.last().user.username
                    if group.teacher.last()
                    else "Unknown",
                    "message": _message,
                }
            )
            print("\t {} - {}".format(_group_name, _message))

    fpath = os.path.join(
        path_to_data,
        "data_inventory_research_consent_" + str(research_consent) + ".csv",
    )

    with open(fpath, "w") as f:
        pd.DataFrame(data_inventory).to_csv(f)

    fpath = os.path.join(
        path_to_data,
        "rejected_groups_research_consent_" + str(research_consent) + ".csv",
    )

    with open(fpath, "w") as f:
        pd.DataFrame(rejected_groups).to_csv(f)

    return rejected_groups, data_inventory


def get_questions_df(path_to_data):
    """
    make dataframe with contextual data on each question
    """
    all_q = pd.DataFrame(
        [
            {
                "text": q.text,
                "image": q.image.url if q.image else None,
                "image_alt_text": q.image_alt_text if q.image else None,
                "video": q.video_url,
                "rationale_selection_algorithm": q.rationale_selection_algorithm,  # noqa
                "categories": ";".join(
                    q.category.all().values_list("title", flat=True)
                ),
                "expert_rationale": ";".join(
                    q.answer_set.filter(expert=True).values_list(
                        "rationale", flat=True
                    )
                ),
                "correct_answerchoice": list(
                    itertools.compress(
                        (itertools.count(1)),
                        (
                            q.answerchoice_set.all().values_list(
                                "correct", flat=True
                            )
                        ),
                    )
                ),
                "correct_answerchoice_text": ";".join(
                    itertools.compress(
                        (
                            q.answerchoice_set.all().values_list(
                                "text", flat=True
                            )
                        ),
                        (
                            q.answerchoice_set.all().values_list(
                                "correct", flat=True
                            )
                        ),
                    )
                ),
            }
            for q in Question.objects.all()
        ]
    )
    fpath = os.path.join(
        path_to_data,
        datetime.datetime.today().strftime("%Y_%m_%d") + "__all_questions.csv",
    )

    with open(fpath, "w") as f:
        all_q.to_csv(f)

    return all_q
