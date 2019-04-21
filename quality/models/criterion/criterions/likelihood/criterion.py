# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import reduce
from operator import mul

from django.db import models

from quality.models.criterion.criterion import Criterion, CriterionRules
from quality.models.custom_fields import CommaSepField
from quality.models.quality_type import QualityType

from .data import language_list
from .model import create_model, predict


class LikelihoodCriterion(Criterion):
    name = models.CharField(
        max_length=32, default="likelihood", editable=False
    )

    @staticmethod
    def info():
        return {
            "name": "likelihood",
            "full_name": "Likelihood",
            "description": "Evaluates if sentence is random gibberish or not.",
        }

    @staticmethod
    def create_default():
        criterion = LikelihoodCriterion.objects.create(
            binary_threshold=True, uses_rules=["languages"]
        )
        criterion.for_quality_types.add(
            QualityType.objects.get(type="studentgroupassignment"),
            QualityType.objects.get(type="studentgroup"),
            QualityType.objects.get(type="teacher"),
            QualityType.objects.get(type="global"),
        )

        return criterion

    def evaluate(self, answer, rules_pk):
        if not isinstance(answer, basestring):
            answer = answer.rationale
        rules = LikelihoodCriterionRules.objects.get(pk=rules_pk)

        other_languages = language_list - set(rules.languages)

        models = {
            language: create_model(language, rules.max_gram)
            for language in language_list
        }

        likelihoods = [
            predict(answer, models[language]) for language in rules.languages
        ] + [
            predict(answer, models[language], models[other_language])
            for other_language in other_languages
            for language in rules.language
        ]

        likelihood = reduce(mul, likelihoods, 1) ** (1 / len(likelihoods))

        evaluation = {"version": self.version, "quality": likelihood}
        evaluation.update(
            {criterion: val["value"] for criterion, val in rules}
        )
        return evaluation


class LikelihoodCriterionRules(CriterionRules):
    languages = CommaSepField(
        distinct=True,
        verbose_name="Languages",
        help_text="Accepted languages. Choices are english and french.",
        blank=True,
        null=True,
    )
    max_gram = models.PositiveIntegerField(
        verbose_name="Max gram", help_text="The maximum size of n-gram to use."
    )

    def __str__(self):
        return "Rules {} for criterion likelihood".format(self.pk)

    @staticmethod
    def get_or_create(
        threshold=1, languages=["english", "french"], max_gram=3
    ):
        """
        Creates or get the criterion rules.

        Parameters
        ----------
        threshold : float in [0, 1] (default : 0)
            Minimum value for the criterion to pass
        languages : List[str] (default : ["english", "french"])
            Accepted languages

        Returns
        -------
        LikelihoodCriterionRules
            Instance

        Raises
        ------
        ValueError
            If the arguments have invalid values
        """
        if threshold < 0 or threshold > 1:
            raise ValueError("The threshold must be between 0 and 1")
        if not isinstance(languages, list):
            raise ValueError("The languages must be a list")
        if max_gram < 1:
            raise ValueError("The max gram has to be greater than 0")
        criterion, __ = LikelihoodCriterionRules.objects.get_or_create(
            threshold=threshold, languages=[l.lower() for l in languages]
        )
        return criterion
