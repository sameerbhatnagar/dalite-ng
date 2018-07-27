from __future__ import unicode_literals

import hashlib

from django.contrib.auth.models import User
from django.db import models, transaction


class Role(models.Model):
    role = models.CharField(max_length=32, primary_key=True)

    def __unicode__(self):
        return "role {}".format(self.role)


class Tos(models.Model):
    ROLES = ("student", "teacher")
    version = models.PositiveIntegerField()
    hash = models.CharField(max_length=32, editable=False)
    text = models.TextField()
    created = models.DateTimeField(editable=False, auto_now=True)
    current = models.BooleanField()
    role = models.CharField(
        max_length=2, choices=tuple((role[:2], role) for role in ROLES)
    )

    def __unicode__(self):
        return str(self.role) + "_" + str(self.version)

    class Meta:
        unique_together = (("role", "version"), ("role", "hash"))

    def save(self, *args, **kwargs):
        if not self.pk:
            self.hash = _compute_hash(str(self.text))
        if self.current:
            Tos.objects.filter(role=self.role, current=True).update(
                current=False
            )
        elif not Tos.objects.filter(role=self.role):
            self.current = True
        super(Tos, self).save(*args, **kwargs)

    @staticmethod
    def get(role, version=None):
        assert isinstance(role, basestring) and role in (
            list(Tos.ROLES) + [r[:2] for r in Tos.ROLES]
        ), "Precondition failed for `role`"
        assert version is None or (
            isinstance(version, int) and version >= 0
        ), "Precondition failed for `version`"

        tos = None
        err = None

        role = role[:2]
        role_long = [r for r in Tos.ROLES if r.startswith(role)][0]

        if version is None:
            try:
                tos = Tos.objects.get(role=role, current=True)
            except Tos.DoesNotExist:
                err = 'No terms of service exist yet for role "{}".'.format(
                    role_long
                )
        else:
            try:
                tos = Tos.objects.get(role=role, version=version)
            except Tos.DoesNotExist:
                err = (
                    "There is no terms of service with version "
                    '{} for role "{}"'.format(version, role_long)
                )

        output = (tos, err)
        assert (
            isinstance(output, tuple)
            and len(output) == 2
            and (output[0] is None) != (output[1] is None)
        ), "Postcondition failed"
        return output


class Consent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tos = models.ForeignKey(Tos, on_delete=models.CASCADE)
    accepted = models.BooleanField()
    datetime = models.DateTimeField(editable=False, auto_now=True)

    @staticmethod
    def get(username, role, version=None, latest=False):
        assert isinstance(
            username, basestring
        ), "Precondition failed for `username`"
        assert isinstance(role, basestring) and role in (
            list(Tos.ROLES) + [r[:2] for r in Tos.ROLES]
        ), "Precondition failed for `role`"
        assert version is None or (
            isinstance(version, int) and version >= 0
        ), "Precondition failed for `version`"
        assert isinstance(latest, bool), "Precondition failed for `version`"
        assert (
            version is None or not latest
        ), "If `version` is given, `latest` must be False"

        consent = None

        role = role[:2]

        if version is None:
            try:
                # returns the latest current consent if `latest` is False
                # or the latest of all consents if `latest` is True
                consent = (
                    Consent.objects.filter(
                        user__username=username,
                        tos__role=role,
                        tos__current=not latest,
                    )
                    .order_by("-datetime")[0]
                    .accepted
                )
            except IndexError:
                consent = None
        else:
            try:
                consent = (
                    Consent.objects.filter(
                        user__username=username,
                        tos__role=role,
                        tos__version=version,
                    )
                    .order_by("-datetime")[0]
                    .accepted
                )
            except IndexError:
                consent = None

        output = consent
        assert output is None or isinstance(
            output, bool
        ), "Postcondition failed"
        return output

    def __unicode__(self):
        return (
            "version "
            + str(self.tos.version)
            + " for "
            + str(self.tos.role)
            + " "
            + str(self.user)
        )


class EmailType(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    type = models.CharField(max_length=32)
    title = models.TextField()
    description = models.TextField()
    show_order = models.PositiveIntegerField(blank=True)

    def __unicode__(self):
        return "email type {} for {}".format(self.type, self.role)

    class Meta:
        unique_together = ("role", "type")

    def save(self, *args, **kwargs):
        if not self.show_order:
            self.show_order = (
                len(
                    EmailType.objects.filter(role=self.role).exclude(
                        type="all"
                    )
                )
                + 1
            )

        if self.type == "all":
            self.show_order = len(EmailType.objects.filter(role=self.role)) + 1

        super(EmailType, self).save(*args, **kwargs)


class EmailConsent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email_type = models.ForeignKey(EmailType, on_delete=models.CASCADE)
    accepted = models.BooleanField()
    datetime = models.DateTimeField(editable=False, auto_now=True)

    @staticmethod
    def get(username, role, email_type, default=None, ignore_all=False):
        assert isinstance(
            username, basestring
        ), "Precondition failed for `username`"
        assert isinstance(role, basestring), "Precondition failed for `role`"
        assert isinstance(
            email_type, basestring
        ), "Precondition failed for `email_type`"
        assert EmailType.objects.filter(
            role=role, type=email_type
        ).exists(), "Precondition failed: there is no matching email_type for the given type and role"

        consent = None

        try:
            consent = (
                EmailConsent.objects.filter(
                    user__username=username,
                    email_type__role=role,
                    email_type__type=email_type,
                )
                .order_by("-datetime")[0]
                .accepted
            )
        except IndexError:
            consent = default

        if not ignore_all and email_type != "all":
            try:
                consent_all = (
                    EmailConsent.objects.filter(
                        user__username=username,
                        email_type__role=role,
                        email_type__type=email_type,
                    )
                    .order_by("-datetime")[0]
                    .accepted
                )
                if not consent_all:
                    consent = False
            except IndexError:
                pass

        output = consent
        assert output is None or isinstance(
            output, bool
        ), "Postcondition failed"
        return output

    def __unicode__(self):
        return "{} for {}".format(self.email_type, self.user)


def _compute_hash(text):
    assert isinstance(text, basestring)
    output = hashlib.md5(text.encode()).hexdigest()
    assert isinstance(output, basestring) and len(output) == 32
    return output


def _create_email_type_all(role):
    EmailType.objects.create(
        role=role,
        type="all",
        title="All email",
        description="Turn off all non-administrative email from Dalite.",
        show_order=len(EmailType.objects.filter(role=role)),
    )
