# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import json
from functools import reduce
from math import exp
from operator import mul, sub

from django.db import models

from quality.models.criterion.criterion import Criterion, CriterionRules
from quality.models.custom_fields import CommaSepField, ProbabilityField
from quality.models.quality_type import QualityType

from .model import create_model


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
        rules = LikelihoodCriterionRules.objects.get(pk=rules_pk)

        languages = LikelihoodLanguage.objects.all()
        other_languages = languages.exclude(language__in=rules.languages.all())

        language_likelihoods = {
            language.language: LikelihoodCache.get(
                answer, language, self, rules
            )
            for language in languages
        }

        likelihoods = [
            1 - min(1, exp(-sub(*language_likelihoods[language.language])))
            for language in rules.languages.all()
        ] + [
            1
            - min(
                1,
                exp(
                    language_likelihoods[other_language.language][0]
                    - language_likelihoods[language.language][0]
                ),
            )
            for other_language in other_languages
            for language in rules.languages.all()
        ]

        likelihood = reduce(mul, likelihoods, 1) ** (1.0 / len(likelihoods))

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
    answer = models.PositiveIntegerField()
    language = models.ForeignKey(LikelihoodLanguage)
    hash = models.CharField(max_length=32, db_index=True)
    likelihood = ProbabilityField()
    likelihood_random = ProbabilityField()

    @classmethod
    def get(cls, answer, language, criterion, rules):
        hash_ = hashlib.md5(
            json.dumps(
                {
                    "text": answer.rationale,
                    "language": language.language,
                    "max_gram": rules.max_gram,
                }
            ).encode()
        ).hexdigest()
        try:
            cache = cls.objects.get(hash=hash_)
            likelihood = cache.likelihood
            likelihood_random = cache.likelihood_random
        except cls.DoesNotExist:
            predict = create_model(
                language.language,
                language.n_gram_urls,
                language.left_to_right,
                rules.max_gram,
            )
            likelihood, likelihood_random = predict(answer.rationale)
            cls.objects.create(
                criterion=criterion,
                rules=rules,
                answer=answer.pk,
                language=language,
                hash=hash_,
                likelihood=likelihood,
                likelihood_random=likelihood_random,
            )
        return likelihood, likelihood_random
