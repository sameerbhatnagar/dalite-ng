# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models.functions import Lower

from peerinst.models import Answer
from quality.models import LikelihoodCache, LikelihoodLanguage

logger = logging.getLogger("quality")


class Command(BaseCommand):
    help = (
        "Compute and cache the likelihood for all answer rationales in all "
        "languages."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--max-gram",
            type=int,
            default=3,
            help="Maximum size of n-grams to use.",
        )
        parser.add_argument(
            "-d", "--discipline", type=str, help="Only cache for discipline"
        )

    def handle(self, *args, **options):
        discipline = options.get("discipline")

        if discipline is None:
            answers = Answer.objects.all()
        else:
            answers = Answer.objects.annotate(
                discipline_lower=Lower("question__discipline__title")
            ).filter(discipline_lower=discipline.lower())

        n = answers.count() * LikelihoodLanguage.objects.count()

        progress = 0
        current = 0

        for answer in answers.iterator():
            for language in LikelihoodLanguage.objects.all().iterator():
                LikelihoodCache.get(answer, language, options["max_gram"])
                progress = progress + 1.0 / n * 100
                if discipline is None:
                    print(
                        "{} - ({:>6.2f}%) -".format(datetime.now(), progress)
                        + " Computing likelihood for all answers..."
                    )
                else:
                    print(
                        "{} - ({:>6.2f}%) -".format(datetime.now(), progress)
                        + " Computing likelihood for answers in "
                        + "discipline {}...".format(discipline)
                    )
