# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re
import urllib

import bs4
import requests
from django.core.files import File
from django.core.management.base import BaseCommand

from peerinst.models import SaltiseMember


class Command(BaseCommand):
    help = (
        "Populate Saltise members from"
        " https://www.saltise.ca/community/saltise-innovators/"
    )

    def handle(self, *args, **kwargs):
        resp = requests.get(
            "https://www.saltise.ca/community/saltise-innovators/"
        )
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        member_elements = [elem.a for elem in soup.find_all(class_="member")]
        members = [
            {
                "name": elem.span.text,
                "picture_link": "https://www.saltise.ca"
                + re.match(
                    r"^background-image: url\((.+)\);$", elem["style"]
                ).group(1),
            }
            for elem in member_elements
        ]
        for member in members:
            if not SaltiseMember.objects.filter(name=member["name"]).exists():
                member_ = SaltiseMember.objects.create(name=member["name"])
                resp = urllib.retrieve(member["picture_link"])
                member_.picture.save(
                    os.path.basename(member["picture_link"]),
                    File(open(resp[0], "r")),
                )
