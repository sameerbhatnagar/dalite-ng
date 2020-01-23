from __future__ import unicode_literals
import os
import json
import spacy
import pandas as pd
import numpy as np
from spacy.matcher import PhraseMatcher
from django.conf import settings
from django_pandas.io import read_frame
from django.db.models import Max

import re
import scipy
import pandas as pd
from collections import defaultdict
from django.db.models import Count
from peerinst.models import (
    StudentGroup,
    ShownRationale,
    Question,
    Teacher,
    Answer,
    Assignment,
)
from tos.models import Consent

MIN_STUDENTS = 10
MIN_PI_QUESTIONS = 10

group_names = (
    StudentGroup.objects.annotate(num_students=Count("student"))
    .filter(num_students__gt=MIN_STUDENTS)
    .values_list("name", flat=True)
)


def get_group_metadata(group):
    if group.teacher.first().disciplines.first():
        discipline=group.teacher.first().disciplines.first().title
    else:
        discipline="Unknown"
    d={
        "teacher":group.teacher.first().user.username,
        "discipline":discipline,
        "name":group.name,
        "title":group.title,
        "N_students":len(filter_student_list(group.name)),
        "N_questions":len(get_pi_question_list(group.name)),
        "N_answers":get_answers_df(group.name).shape[0],
    }
    return d



def filter_student_list(group_name):
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

    return student_list


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

    if len(assignment_list) > 0:
        sg_assignment_list = sg.studentgroupassignment_set.all()

        for _a in sg_assignment_list:
            pi_question_list.extend(_a.assignment.questions.filter(type="PI"))

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

    # remove those where all answerchoices are marked as correct
    pi_question_list = [
        q
        for q in pi_question_list
        if not all(q.answerchoice_set.all().values_list("correct", flat=True))
    ]
    return pi_question_list


def filter_groups_on_min_students(group_name):
    student_list_filtered = filter_student_list(group_name)
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
    pi_question_list = get_pi_question_list(group_name)

    message = "{} pi questions".format(len(pi_question_list))
    if len(pi_question_list) < MIN_PI_QUESTIONS:
        return (None, message)
    else:
        return (group_name, message)


def filter_groups_on_min_a(group_name):
    _group_name, _message = filter_groups_on_min_students(group_name)
    if _group_name:
        student_list_filtered = filter_student_list(group_name)
        assignment_list = get_assignment_list(group_name)
        pi_question_list = get_pi_question_list(group_name)
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


def filter_groups(group_name):
    _group_name, _message = filter_groups_on_min_students(group_name)
    if _group_name:
        __group_name, __message = filter_groups_on_min_qs(group_name)
        if __group_name:
            ___group_name, ___message = filter_groups_on_min_a(group_name)
            if ___group_name:
                return group_name, None
            else:
                return None, ___message
        else:
            return None, __message
    else:
        return None, _message


# utility functions

pattern = re.compile("[ ''\[\]]")

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
def print_rationales(a_list):
    for a in Answer.objects.filter(id__in=a_list):
        print("Question:")
        print(a.question.text)
        if a.question.image:
            print(Image(url="." + a.question.image.url))
        print("\n")
        print("Student Rationale")
        print(a.rationale)
        print("\n\n\n\n")
    return


def shown_answer_ids(shown_for_answer_id, justiceX=pd.DataFrame()):
    """
    given Answer id, return dataframe with columns shown_answer_id,shown_word count) of the answers that were shown to the student
    """
    if not justiceX.empty:
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
    #                               * 1/2 chance students choose their own rationale
    df["chosen_ratio"] = (df["times_chosen"] + 1) / (df["times_shown"] + 14)

    return df


def get_answers_df(group_name):
    """
    given group name, return df_answers
    """

    if group_name == "justiceX":  # not in same db

        df_answers = read_from_harvard_db2()
        # id of longest rationale
        df_answers["l_s_r_id"] = df_answers["id"].apply(
            lambda x: get_longest_shown_rationale_id(x, justiceX=df_answers)
        )

    else:
        assignment_list = get_assignment_list(group_name)

        pi_question_list = get_pi_question_list(group_name)

        filtered_student_list = filter_student_list(group_name)

        # load data
        a_qs = Answer.objects.filter(
            user_token__in=filtered_student_list,
            assignment_id__in=assignment_list,
            question_id__in=pi_question_list,
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
    df_answers["rationale_word_count"] = df_answers.rationale.str.count("\w+")

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
            & (df_answers["chosen_rationale__id"].isna() == False)
        ),
        "switch_rationale",
    ] = 1

    return df_answers
