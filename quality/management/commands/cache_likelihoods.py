# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging

from django.core.management.base import BaseCommand

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

    def handle(self, *args, **options):
        n = Answer.objects.count() * LikelihoodLanguage.objects.count()
        signs = ["⠋", "⠙", "⠴", "⠦"]

        progress = 0
        current = 0
        i = 0
        for answer in Answer.objects.all().iterator():
            for language in LikelihoodLanguage.objects.all().iterator():
                LikelihoodCache.get(answer, language, options["max_gram"])
                progress = progress + 1.0 / n * 100
                print(
                    "{} ({:>6.2f}%)".format(signs[i], progress)
                    + " Computing likelihood for all answers...",
                    end="\r",
                )
                i = (i + 1) % len(signs)
