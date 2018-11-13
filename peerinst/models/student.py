# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import smtplib

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

logger = logging.getLogger("peerinst-models")


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(StudentGroup, blank=True)
    student_groups = models.ManyToManyField(
        StudentGroup,
        blank=True,
        through="StudentGroupMembership",
        related_name="groups_new",
    )
    send_reminder_email_every_day = models.BooleanField(default=False)
    send_reminder_email_day_before = models.BooleanField(default=True)

    def __unicode__(self):
        return self.student.username

    class Meta:
        verbose_name = _("student")
        verbose_name_plural = _("students")

    @staticmethod
    def get_or_create(email):
        """
        Gets the student with the given `email`, creating them if need be.

        Parameters
        ----------
        email : str
            Student email

        Returns
        -------
        student : Optional[Student]
            Student instance if no error getting or creating them
        created : bool
            If the student was created or not
        """
        assert isinstance(email, basestring), "Precondition failed for `email`"

        student = None

        username, password = get_student_username_and_password(email)

        try:
            student = Student.objects.get(
                student__username=username, student__email=email
            )
            created = False
        except Student.DoesNotExist:

            try:
                user = User.objects.create_user(
                    username=username, email=email, password=password
                )

                # Set inactive until confirmed by user
                user.is_active = False
                user.save()
                student = Student.objects.create(student=user)
                created = True
            except IntegrityError:
                student = None
                created = False
                logger.error(
                    "There was an error creating student with "
                    "email {}.".format(email)
                )

        return student, created

    def send_email(self, mail_type, group=None):
        """
        Sends an email to announce a new assignment or an assignment update.

        Parameters
        ----------
        mail_type : str
            Type of mail to send. One of:
                "new_assignment"
                "assignment_updated"

        Returns
        -------
        err : Optional[str]
            Error message if there is any
        """
        assert isinstance(
            mail_type, basestring
        ), "Precondition failed for `mail_type`"
        assert (
            isinstance(group, StudentGroup) or group is None
        ), "Precondition failed for `group`"
        assert (
            "group" not in mail_type or group is not None
        ), "Precondition failed for `group`"

        err = None

        if not self.student.email.endswith("localhost"):

            username = self.student.username
            user_email = self.student.email

            if not user_email:
                err = "There is no email associated with user {}.".format(
                    self.student.username
                )
                logger.error(err)

            else:

                host = settings.ALLOWED_HOSTS[0]

                if host == "localhost" or host == "127.0.0.1":
                    protocol = "http"
                else:
                    protocol = "https"

                token = create_student_token(username, user_email)

                signin_link = "{}://{}{}?token={}".format(
                    protocol, host, reverse("student-page"), token
                )

                group = group.title if group is not None else None

                if mail_type == "signin":
                    subject = "Sign in to your myDALITE account"
                    message = (
                        "Sign in to your myDALITE accout by going to "
                        "the link below:\n" + signin_link
                    )
                    template = "peerinst/student/emails/signin.html"
                elif mail_type == "confirmation":
                    subject = "Confirm your myDALITE account"
                    message = (
                        "Please confirm your myDALITE account by going to "
                        "the link below:\n " + signin_link
                    )
                    template = "peerinst/student/emails/confirmation.html"
                elif mail_type == "new_group":
                    subject = (
                        "You've successfully been registered to group " + group
                    )
                    message = (
                        "Sign in to your myDALITE accout by going to "
                        "the link below:\n" + signin_link
                    )
                    template = "peerinst/student/emails/new_group.html"
                else:
                    err = "The `mail_type` wasn't in the allowed types."
                    logger.error(err)

                context = {"signin_link": signin_link, "group": group}

                if err is None:
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
                        logger.error(err)

        assert err is None or isinstance(
            err, basestring
        ), "Postcondition failed"
        return err

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
                    logger.info(
                        "Assignment %d created for student %d.",
                        assignment_.pk,
                        self.pk,
                    )
                    if not assignment.is_expired():
                        # Just send active assignments
                        assignment_.send_email(mail_type="new_assignment")
                        logger.info(
                            "Assignment %d sent to student %d.",
                            assignment_.pk,
                            self.pk,
                        )

    def join_group(self, group):
        try:
            membership = StudentGroupMembership.objects.get(
                student=self, group=group
            )
            membership.current_member = True
            membership.save()
            logger.info(
                "Student %d added back to group %d.", self.pk, group.pk
            )
        except StudentGroupMembership.DoesNotExist:
            StudentGroupMembership.objects.create(
                student=self, group=group, current_member=True
            )
            logger.info(
                "Student %d added to group %d for the first time.",
                self.pk,
                group.pk,
            )
        # TODO to remove eventually when groups are fully integrated in
        # group membership
        self.groups.add(group)

    def leave_group(self, group):
        try:
            membership = StudentGroupMembership.objects.get(
                student=self, group=group
            )
            membership.current_member = False
            membership.save()
        except StudentGroupMembership.DoesNotExist:
            logger.warning(
                "Student {} left group {} of which he wasn't a member.".format(
                    self.pk, group.pk
                )
            )

    def add_assignment(self, group_assignment, host=None):
        assignment, created = StudentAssignment.objects.get_or_create(
            student=self, group_assignment=group_assignment
        )
        if created:
            logger.info(
                "Assignment %d created for student %d.", assignment.pk, self.pk
            )
        else:
            logger.info(
                "Assignment %d retrieved for student %d.",
                assignment.pk,
                self.pk,
            )

        StudentNotification.create(
            type_="new_assignment", student=self, assignment=assignment
        )

        if host:
            assignment.send_email(mail_type="new_assignment")
            logger.info(
                "Assignment %d email sent to student %d.",
                assignment.pk,
                self.pk,
            )

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

    @property
    def notifications(self):
        return self.studentnotification_set.order_by("-created_on").all()


class StudentGroupMembership(models.Model):
    student = models.ForeignKey(Student)
    group = models.ForeignKey(StudentGroup)
    current_member = models.BooleanField(default=True)
    send_emails = models.BooleanField(default=True)

    class Meta:
        unique_together = ("student", "group")


class StudentAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group_assignment = models.ForeignKey(
        StudentGroupAssignment, on_delete=models.CASCADE
    )
    first_access = models.DateTimeField(editable=False, auto_now=True)
    last_access = models.DateTimeField(editable=False, auto_now=True)
    reminder_sent = models.BooleanField(editable=False, default=False)

    class Meta:
        unique_together = ("student", "group_assignment")

    def __unicode__(self):
        return "{} for {}".format(self.group_assignment, self.student)

    def send_email(self, mail_type):
        """
        Sends an email to announce a new assignment or an assignment update.

        Parameters
        ----------
        mail_type : str
            Type of mail to send. One of:
                "new_assignment"
                "assignment_updated"

        Returns
        -------
        err : Optional[str]
            Error message if there is any
        """
        assert isinstance(
            mail_type, basestring
        ), "Precondition failed for `mail_type`"

        err = None

        if not self.student.student.email.endswith("localhost"):

            username = self.student.student.username
            user_email = self.student.student.email
            group_membership = StudentGroupMembership.objects.get(
                student=self.student, group=self.group_assignment.group
            )

            if not user_email:
                err = "There is no email associated with user {}.".format(
                    self.student.student.username
                )
                logger.error(err)
            elif group_membership.send_emails:

                host = settings.ALLOWED_HOSTS[0]

                if host == "localhost" or host == "127.0.0.1":
                    protocol = "http"
                else:
                    protocol = "https"

                token = create_student_token(username, user_email)

                signin_link = "{}://{}{}?token={}".format(
                    protocol, host, reverse("student-page"), token
                )
                assignment_link = "{}://{}{}".format(
                    protocol,
                    host,
                    reverse(
                        "live",
                        kwargs={
                            "assignment_hash": self.group_assignment.hash,
                            "token": token,
                        },
                    ),
                )

                days_to_expiry = self.group_assignment.days_to_expiry

                if mail_type == "new_assignment":
                    subject = "New assignment for group {}".format(
                        self.group_assignment.group.title
                    )
                    message = (
                        "Use one of the links below to access your "
                        "assignment or go to your student page."
                        "\nGo to assignment: "
                        + assignment_link
                        + "\nGo to student page: "
                        + signin_link
                    )
                    template = "peerinst/student/emails/new_assignment.html"

                elif mail_type == "assignment_updated":
                    subject = "Assignment {} for group {} updated".format(
                        self.group_assignment.assignment.title,
                        self.group_assignment.group.title,
                    )
                    message = (
                        "Use one of the links below to access your "
                        "assignment or go to your student page."
                        "\nGo to assignment: "
                        + assignment_link
                        + "\nGo to student page: "
                        + signin_link
                    )
                    template = (
                        "peerinst/student/emails/assignment_updated.html"
                    )

                elif mail_type == "assignment_about_to_expire":
                    subject = "Assignment {} for ".format(
                        self.group_assignment.assignment.title
                    ) + "group {} expires in {} days".format(
                        self.group_assignment.group.title, days_to_expiry
                    )
                    message = (
                        "Use one of the links below to access your "
                        "assignment or go to your student page."
                        "\nGo to assignment: "
                        + assignment_link
                        + "\nGo to student page: "
                        + signin_link
                    )
                    template = (
                        "peerinst/student/emails/"
                        "assignment_about_to_expire.html"
                    )

                else:
                    err = "The `mail_type` wasn't in the allowed types."
                    logger.error(err)

                context = {
                    "group": self.group_assignment.group.title,
                    "assignment": self.group_assignment.assignment.title,
                    "assignment_link": assignment_link,
                    "signin_link": signin_link,
                    "days_to_expiry": days_to_expiry,
                }

                if err is None:
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
                        logger.error(err)

        assert err is None or isinstance(
            err, basestring
        ), "Postcondition failed"
        return err

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

    def get_results(self):
        """
        Returns
        -------
        {
            "n" : int
                number of questions
            "n_first_answered" : int
                number of questions answered
            "n_second_answered" : Optional[int]
                number of questions answered with a second answer (or None if
                not applicable)
            "n_first_correct" : int
                number of correct first answers
            "n_second_correct" : Optional[int]
                number of correct second answers (or None if not applicable)

        }
        """
        data = [
            {
                "question": question,
                "answer": (
                    Answer.objects.filter(
                        assignment=self.group_assignment.assignment,
                        user_token=self.student.student.username,
                        question=question,
                    )
                    or [None]
                )[0],
                "correct": [
                    i + 1
                    for i, _ in enumerate(question.get_choices())
                    if question.is_correct(i + 1)
                ],
            }
            for question in self.group_assignment.questions
        ]

        results = {
            "n": len(data),
            "n_first_answered": len(
                [q for q in data if q["answer"] is not None]
            ),
            "n_second_answered": len(
                [
                    q
                    for q in data
                    if q["answer"] is not None
                    and q["answer"].second_answer_choice is not None
                ]
            ),
            "n_first_correct": len(
                [
                    q
                    for q in data
                    if q["answer"] is not None
                    and q["answer"].first_answer_choice in q["correct"]
                ]
            ),
            "n_second_correct": len(
                [
                    q
                    for q in data
                    if q["answer"] is not None
                    and q["answer"].second_answer_choice is not None
                    and q["answer"].second_answer_choice in q["correct"]
                ]
            ),
        }

        return results

    def send_reminder(self, last_day):
        """
        Sends a reminder that the assignment is almost due as a reset of the
        student notification and possibly an email.

        Parameters
        ----------
        last_day : bool
            If there is only one day before the assignment is due
        """
        if not self.completed:
            if not StudentNotification.objects.filter(
                student=self.student,
                notification__type="assignment_about_to_expire",
            ).exists():
                StudentNotification.create(
                    type_="assignment_about_to_expire",
                    student=self.student,
                    assignment=self,
                )

            if StudentGroupMembership.objects.get(
                student=self.student, group=self.group_assignment.group
            ).send_emails:
                if (
                    not self.reminder_sent
                    or self.student.send_reminder_email_every_day
                    or (
                        last_day
                        and self.student.send_reminder_email_day_before
                    )
                ):
                    err = self.send_email("assignment_about_to_expire")
                    if err is None:
                        self.reminder_sent = True
                        self.save()

    @property
    def completed(self):
        """
        Returns
        -------
        bool
            If the assignment was completed
        """
        return not any(
            not Answer.objects.filter(
                assignment=self.group_assignment.assignment,
                user_token=self.student.student.username,
                question=question,
            ).exists()
            or Answer.objects.get(
                assignment=self.group_assignment.assignment,
                user_token=self.student.student.username,
                question=question,
            ).second_answer_choice
            is None
            for question in self.group_assignment.questions
        )


class StudentNotificationType(models.Model):
    type = models.CharField(max_length=32, unique=True)
    icon = models.TextField()


class StudentNotification(models.Model):
    student = models.ForeignKey(Student)
    notification = models.ForeignKey(StudentNotificationType)
    created_on = models.DateTimeField(auto_now=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)
    text = models.TextField()
    hover_text = models.TextField(blank=True, null=True)

    @staticmethod
    def create(type_, student, assignment=None):
        """
        Creates a new notification of the given `type_` for the `student`.

        Parameters
        ----------
        type_ : str
            Type of notification. Must be equal to the field `type` for one of
            the StudentNotificationType
        student : Student
            Student for whom the notification is created
        assignment : Optional[StudentAssignment] (default : None)
            Assignment corresponding to the notification if needed
        """
        assert isinstance(
            student, Student
        ), "Precondition failed for `student`"
        assert (
            isinstance(assignment, StudentAssignment) or assignment is None
        ), "Precondition failed for `assignment`"
        assert isinstance(type_, basestring) and (
            "assignment" not in type_ or assignment is not None
        ), "Precondition failed for `type_`"

        try:
            notification = StudentNotificationType.objects.get(type=type_)
        except StudentNotificationType.DoesNotExist:
            logger.error(
                "A notification wasn't created for "
                + "student {} ".format(student.pk)
                + "because {} wasn't a valid notification type.".format(type_)
            )

        else:
            if assignment is not None:
                link = reverse(
                    "live",
                    kwargs={
                        "assignment_hash": assignment.group_assignment.hash,
                        "token": create_student_token(
                            student.student.username, student.student.email
                        ),
                    },
                )
                hover_text = "Go to assignment"
            else:
                link = ""
                hover_text = ""

            if type_ == "new_assignment":
                text = "A new assignment {} was added for group {}.".format(
                    assignment.group_assignment.assignment.title,
                    assignment.group_assignment.group.title,
                )

            elif type_ == "assignment_due_date_changed":
                text = (
                    "The due date for assignment {} ".format(
                        assignment.group_assignment.assignment.title
                    )
                    + "in group {} was ".format(
                        assignment.group_assignment.group.title
                    )
                    + "changed to {}.".format(
                        assignment.group_assignment.due_date.strftime(
                            "%Y-%m-%d %H:%M"
                        )
                    )
                )

            elif type_ == "assignment_about_to_expire":
                text = "The assignment {} in group {} expires on {}.".format(
                    assignment.group_assignment.assignment.title,
                    assignment.group_assignment.group.title,
                    assignment.group_assignment.due_date.strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                )

            else:
                logger.error(
                    "There's a missing branch for notification "
                    "type {}.".format(type_)
                )
                return

            StudentNotification.objects.create(
                student=student,
                notification=notification,
                link=link,
                text=text,
                hover_text=hover_text,
            )
            logger.info(
                "Notification of type {} was created for student {}.".format(
                    type_, student.pk
                )
            )
