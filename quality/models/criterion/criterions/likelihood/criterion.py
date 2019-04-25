# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import json
from functools import reduce
from operator import mul

from django.db import models

from quality.models.criterion.criterion import Criterion, CriterionRules
from quality.models.custom_fields import CommaSepField, ProbabilityField
from quality.models.quality_type import QualityType

from .model import create_model

language_list = {"english", "french"}


class LikelihoodLanguage(models.Model):
    language = models.CharField(max_length=32, primary_key=True)
    left_to_right = models.BooleanField(default=True)
    n_gram_urls = CommaSepField(distinct=True)

    def __str__(self):
        return str(self.pk)

    @classmethod
    def available(cls):
        return [instance.pk for instance in cls.objects.all()]


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
            binary_threshold=False, uses_rules=["languages"]
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

        other_languages = [
            LikelihoodLanguage.objects.get(language=language)
            for language in set(language_list)
            - {language.language for language in rules.languages.all()}
        ]

        hash_ = LikelihoodCache.compute_hash(
            answer, rules.languages.all(), other_languages, rules.max_gram
        )

        try:
            likelihood = LikelihoodCache.objects.get(hash=hash_).likelihood
        except LikelihoodCache.DoesNotExist:
            models = [
                create_model(
                    (
                        language.language,
                        language.n_gram_urls,
                        language.left_to_right,
                    ),
                    other_language=None,
                    max_gram=rules.max_gram,
                )
                for language in rules.languages.all()
            ] + [
                create_model(
                    (
                        language.language,
                        language.n_gram_urls,
                        language.left_to_right,
                    ),
                    other_language=(
                        other_language.language,
                        other_language.n_gram_urls,
                        other_language.left_to_right,
                    ),
                    max_gram=rules.max_gram,
                )
                for other_language in other_languages
                for language in rules.languages.all()
            ]

            likelihoods = [predict(answer) for predict in models]
            likelihood = reduce(mul, likelihoods, 1) ** (
                1.0 / len(likelihoods)
            )

            LikelihoodCache.objects.create(
                criterion=self, rules=rules, hash=hash_, likelihood=likelihood
            )

        evaluation = {"version": self.version, "quality": likelihood}
        evaluation.update(
            {criterion: val["value"] for criterion, val in rules}
        )
        return evaluation


class LikelihoodCriterionRules(CriterionRules):
    languages = models.ManyToManyField(
        LikelihoodLanguage,
        verbose_name="Languages",
        help_text="Accepted languages.",
    )
    max_gram = models.PositiveIntegerField(
        verbose_name="Max gram", help_text="The maximum size of n-gram to use."
    )

    def __str__(self):
        return "Rules {} for criterion likelihood".format(self.pk)

    @staticmethod
    def get_or_create(
        threshold=0.95, languages=["english", "french"], max_gram=3
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

        try:
            languages = [
                language
                if isinstance(language, LikelihoodLanguage)
                else LikelihoodLanguage.objects.get(language=language.lower())
                for language in languages
            ]
        except LikelihoodLanguage.DoesNotExist:
            raise ValueError(
                "The language has to be one of {}".format(
                    LikelihoodLanguage.available()
                )
            )

        criterion = LikelihoodCriterionRules.objects.filter(
            threshold=threshold, max_gram=max_gram
        )
        for language in languages:
            criterion = criterion.filter(languages__pk=language.pk)
            if not criterion:
                criterion = LikelihoodCriterionRules.objects.create(
                    threshold=threshold, max_gram=max_gram
                )
                criterion.languages.set([l.pk for l in languages])
                criterion.save()
                break
        else:
            criterion = criterion.first()

        return criterion


class LikelihoodCache(models.Model):
    criterion = models.ForeignKey(LikelihoodCriterion)
    rules = models.ForeignKey(LikelihoodCriterionRules)
    hash = models.CharField(max_length=32, unique=True, db_index=True)
    likelihood = ProbabilityField()

    @staticmethod
    def compute_hash(text, languages, other_languages, max_gram):
        languages = list(map(str, languages))
        other_languages = list(map(str, other_languages))
        data = json.dumps(
            {
                "text": text,
                "languages": languages,
                "other_languages": other_languages,
                "max_gram": max_gram,
            }
        )
        return hashlib.md5(data.encode()).hexdigest()
