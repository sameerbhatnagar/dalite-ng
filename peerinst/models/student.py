# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import smtplib

import pytz
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import IntegrityError, models
from django.template import loader
from django.utils.translation import ugettext_lazy as _

from ..students import create_student_token, get_student_username_and_password
from .answer import Answer
from .assignment import StudentGroupAssignment
from .group import StudentGroup
from .question import Question


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(StudentGroup, blank=True)
    student_groups = models.ManyToManyField(
        StudentGroup,
        blank=True,
        through="StudentGroupMembership",
        related_name="groups_new",
    )

    def __unicode__(self):
        return self.student.username

    class Meta:
        verbose_name = _("student")
        verbose_name_plural = _("students")

    @staticmethod
    def get_or_create(email):
        """
        Adds the student by using hashes of the email for the username and
        password.
        """

        assert isinstance(email, basestring), "Precondition failed for `email`"

        student = None

        username, password = get_student_username_and_password(email)

        try:
            student = Student.objects.get(
                student__username=username, student__email=email
            )
        except Student.DoesNotExist:

            try:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )

                # Set inactive until confirmed by user
                user.is_active = False
                user.save()
                student = Student.objects.create(student=user)
            except IntegrityError:
                student = None

        output = student
        assert output is None or isinstance(
            output, Student
        ), "Postcondition failed"
        return output

    def send_confirmation_email(self, group, host):
        """Sends e-mail with link for confirmation of account."""
        assert isinstance(host, basestring), "Precondition failed for `host`"
        err = None

        if not self.student.email.endswith("localhost"):

            username = self.student.username
            user_email = self.student.email
            token = create_student_token(username, user_email)
            hash_ = group.hash
            link = reverse(
                "confirm-signup-through-link",
                kwargs={"group_hash": hash_, "token": token},
            )

            if host.startswith("localhost") or host.startswith("127.0.0.1"):
                protocol = "http"
            else:
                protocol = "https"

            subject = "Confirm myDALITE account"
            message = (
                "Please confirm myDALITE account by going to: " + host + link
            )
            template = "students/email_confirmation.html"
            context = {"link": link, "host": host, "protocol": protocol}

            try:
                send_mail(
                    subject,
                    message,
                    "noreply@myDALITE.org",
                    [user_email],
                    fail_silently=False,
                    html_message=loader.render_to_string(
                        template, context=context
                    ),
                )
            except smtplib.SMTPException:
                err = "There was an error sending the email."

        output = err
        assert err is None or isinstance(
            output, basestring
        ), "Postcondition failed"

    def send_signin_email(self, host):
        assert isinstance(host, basestring), "Precondition failed for `host`"
        err = None

        if not self.student.email.endswith("localhost"):

            username = self.student.username
            user_email = self.student.email
            token = create_student_token(username, user_email)
            link = reverse("student-page", kwargs={"token": token})

            if host.startswith("localhost") or host.startswith("127.0.0.1"):
                protocol = "http"
            else:
                protocol = "https"

            subject = "Sign in to your myDALITE account"
            message = (
                " Sign in to your myDALITE accout by clicking the link "
                "below:\n"
                "{}://{}{}".format(protocol, host, link)
            )
            template = "students/email_signin.html"
            context = {"host": host, "protocol": protocol, "link": link}

            try:
                send_mail(
                    subject,
                    message,
                    "noreply@myDALITE.org",
                    [user_email],
                    fail_silently=False,
                    html_message=loader.render_to_string(
                        template, context=context
                    ),
                )
            except smtplib.SMTPException:
                err = "There was an error sending the email."

        output = err
        assert err is None or isinstance(
            output, basestring
        ), "Postcondition failed"

    def send_missing_assignments(self, group, host):
        assert isinstance(
            group, StudentGroup
        ), "Precondition failed for `group`"

        if not self.student.email.endswith("localhost"):

            assignments = StudentGroupAssignment.objects.filter(group=group)

            for assignment in assignments:
                # Create missing instances
                if not StudentAssignment.objects.filter(
                    student=self, group_assignment=assignment
                ).exists():
                    assignment_ = StudentAssignment.objects.create(
                        student=self, group_assignment=assignment
                    )
                    if not assignment.is_expired():
                        # Just send active assignments
                        assignment_.send_email(host, "new_assignment")

    def add_group(self, group):
        try:
            membership = StudentGroupMembership.objects.get(
                student=self, group=group
            )
            membership.current_member = True
            membership.save()
        except StudentGroupMembership.DoesNotExist:
            StudentGroupMembership.objects.create(
                student=self, group=group, current_member=True
            )

    def leave_group(self, group):
        try:
            membership = StudentGroupMembership.objects.get(
                student=self, group=group
            )
            membership.current_member = False
            membership.save()
        except StudentGroupMembership.DoesNotExist:
            pass

    @property
    def current_groups(self):
        return [
            g.group
            for g in StudentGroupMembership.objects.filter(
                student=self, current_member=True
            )
        ]

    @property
    def old_groups(self):
        return [
            g.group
            for g in StudentGroupMembership.objects.filter(
                student=self, current_member=False
            )
        ]


class StudentGroupMembership(models.Model):
    student = models.ForeignKey(Student)
    group = models.ForeignKey(StudentGroup)
    current_member = models.BooleanField(default=True)


class StudentAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group_assignment = models.ForeignKey(
        StudentGroupAssignment, on_delete=models.CASCADE
    )
    first_access = models.DateTimeField(editable=False, auto_now=True)
    last_access = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        unique_together = ("student", "group_assignment")

    def __unicode__(self):
        return "{} for {}".format(self.group_assignment, self.student)

    def send_email(
        self, host, mail_type="login", link=None, assignment_hash=None
    ):
        assert (
            isinstance(link, basestring) and "{}" in link or link is None
        ), "Precondition failed for `link`"
        assert isinstance(host, basestring), "Precondition failed for `host`"
        assert isinstance(mail_type, basestring) and mail_type in (
            "login",
            "new_assignment",
        ), "Precondition failed for `mail_type`"

        err = None

        if not self.student.student.email.endswith("localhost"):

            username = self.student.student.username
            user_email = self.student.student.email

            if err is None and user_email:
                token = create_student_token(username, user_email)

                if mail_type == "login":

                    subject = "Login to myDALITE"
                    message = "Click link below to login to your account."

                    template = "students/email_login.html"

                elif mail_type == "new_assignment":

                    link = reverse(
                        "live",
                        kwargs={
                            "assignment_hash": self.group_assignment.hash,
                            "token": token,
                        },
                    )

                    subject = (
                        "New assignment in "
                        + self.group_assignment.group.title
                        + " (due "
                        + self.group_assignment.due_date.astimezone(
                            pytz.timezone(settings.DEFAULT_TIMEZONE)
                        ).strftime("%Y-%m-%d %H:%M %Z")
                        + ")"
                    )
                    message = "Click link below to access your assignment."

                    template = "students/email_new_assignment.html"

                else:
                    raise RuntimeError(
                        "This error should not be possible. Check asserts and "
                        "mail types."
                    )

                if host == "localhost" or host == "127.0.0.1":
                    protocol = "http"
                else:
                    protocol = "https"

                context = {"link": link, "host": host, "protocol": protocol}

                try:
                    send_mail(
                        subject,
                        message,
                        "noreply@myDALITE.org",
                        [user_email],
                        fail_silently=False,
                        html_message=loader.render_to_string(
                            template, context=context
                        ),
                    )
                except smtplib.SMTPException:
                    err = "There was an error sending the email."
            else:
                if err is None:
                    err = "There is no email associated with user {}".format(
                        self.student.user.username
                    )

        output = err
        assert err is None or isinstance(
            output, basestring
        ), "Postcondition failed"

    def get_current_question(self):
        questions = self.group_assignment.questions

        # get the answer or None for each question of the assignment
        answers = [
            Answer.objects.filter(
                user_token=self.student.student.username,
                question=question,
                assignment=self.group_assignment.assignment,
            ).first()
            for question in questions
        ]
        has_first_answer = [
            a.first_answer_choice is not None if a else False for a in answers
        ]
        # if a question has at least one missing answer (no first choice or no
        # answer), returns the first question with no answer or no first answer
        # choice
        if not all(has_first_answer):
            output = questions[has_first_answer.index(False)]
        else:
            has_second_answer = [
                a.second_answer_choice is not None for a in answers
            ]
            # if there is a question missing the second answer, returns it or
            # returns None if all questions have been answered twice
            if not all(has_second_answer):
                output = questions[has_second_answer.index(False)]
            else:
                output = None

        assert output is None or isinstance(
            output, Question
        ), "Postcondition failed"
        return output
