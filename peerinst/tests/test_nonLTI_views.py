from django.contrib.auth.hashers import make_password
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase, TransactionTestCase

from ..models import Discipline, Question, Assignment, Teacher, Student
from django.contrib.auth.models import User, Permission

def ready_user(pk):
    user = User.objects.get(pk=pk)
    user.text_pwd = user.password
    user.password = make_password(user.text_pwd)
    user.save()
    return user

class LandingPageTest(TransactionTestCase):

    def setUp(self):
        physics = Discipline.objects.create(title='Physics')
        math = Discipline.objects.create(title='Math')
        chemistry = Discipline.objects.create(title='Chemistry')

        Question.objects.create(title='A', text='text', discipline=physics)
        Question.objects.create(title='B', text='text', discipline=physics)
        Question.objects.create(title='C', text='text', discipline=physics)

        Question.objects.create(title='D', text='text', discipline=math)
        Question.objects.create(title='E', text='text', discipline=math)

        Question.objects.create(title='F', text='text', discipline=chemistry)

    def test_discipline_stats(self):
        self.assertEqual(Question.objects.count(), 6)
        self.assertEqual(Discipline.objects.count(), 3)

        response = self.client.get(reverse('landing_page'))

        self.assertEqual(response.context['disciplines'][0]['name'], 'All')
        self.assertEqual(response.context['disciplines'][1]['name'], 'Physics')
        self.assertEqual(response.context['disciplines'][2]['name'], 'Math')
        self.assertEqual(response.context['disciplines'][3]['name'], 'Chemistry')


class SignUpTest(TestCase):

    def test_which_template(self):
        response = self.client.get(reverse('sign_up'))
        self.assertTemplateUsed(response, 'registration/sign_up.html')

    def test_invalid_form_post(self):
        response = self.client.post(reverse('sign_up'), data={})
        self.assertIn('This field is required', response.content.decode())

    def test_valid_form_post(self):
        response = self.client.post(reverse('sign_up'), data={'username':'abc', 'password1':'jdefngath4', 'password2':'jdefngath4', 'email':'abc@def.com', 'url':'http://abc.com'})
        self.assertTemplateUsed(response, 'registration/sign_up_done.html')
        self.assertTemplateUsed(response, 'registration/sign_up_admin_email_html.html')

    def test_password_mismatch(self):
        response = self.client.post(reverse('sign_up'), data={'username':'abc', 'password1':'jdefngath4', 'password2':'jdefngath', 'email':'abc@def.com', 'url':'http://abc.com'})
        self.assertIn('The two password fields didn\'t match', response.content.decode())

    def test_email_error(self):

        with self.settings(EMAIL_BACKEND=''):
            response = self.client.post(reverse('sign_up'), data={'username':'abc', 'password1':'jdefngath4', 'password2':'jdefngath4', 'email':'abc@def.com', 'url':'http://abc.com'}, follow=True)
            self.assertEqual(response.status_code, 500)
            self.assertTemplateUsed(response, '500.html')


class TeacherTest(TestCase):
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.validated_teacher = ready_user(1)
        self.other_teacher = ready_user(2)
        self.inactive_user = ready_user(3)
        self.guest = ready_user(11)

    def test_login_and_access_to_accounts(self):
        # Login
        response = self.client.post(reverse('login'), {'username' : self.validated_teacher.username, 'password' : self.validated_teacher.text_pwd}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'].pk, 1)
        self.assertTemplateUsed(response, 'peerinst/teacher_detail.html')

        # Test access to other
        response = self.client.get(reverse('teacher', kwargs={ 'pk' : 2 }))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')

        # Test access to non-existent
        response = self.client.get(reverse('teacher', kwargs={ 'pk' : 3 }))
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

        # Logout
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/landing_page.html')

        # Attempt access after logout
        response = self.client.get(reverse('teacher', kwargs={ 'pk' : 1 }), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_refuse_inactive_at_login(self):
        # @login_required decorator and mixin do NOT check if user.is_active
        # but authentication backend should.
        #
        # Check inactive user cannot login
        logged_in = self.client.login(username=self.inactive_user.username, password=self.inactive_user.text_pwd)
        self.assertFalse(logged_in)

    def test_question_list_view(self):
        logged_in = self.client.login(username=self.validated_teacher.username, password=self.validated_teacher.text_pwd)
        self.assertTrue(logged_in)

        # List matches assignment object
        response = self.client.get(reverse('question-list', kwargs={ 'assignment_id' : 'Assignment1' }))
        self.assertEqual(response.status_code, 200)
        self.assertItemsEqual(response.context['object_list'], Assignment.objects.get(pk='Assignment1').questions.all())

        # Assignment pk invalid -> 404
        response = self.client.get(reverse('question-list', kwargs={ 'assignment_id' : 'unknown_id' }))
        self.assertEqual(response.status_code, 404)

    def test_question_create(self):
        logged_in = self.client.login(username=self.validated_teacher.username, password=self.validated_teacher.text_pwd)
        self.assertTrue(logged_in)

        # Step 1, without peerinst.add_question -> 403
        response = self.client.get(reverse('question-create'))
        self.assertEqual(response.status_code, 403)

        response = self.client.post(reverse('question-create'), {
            'text' : 'Text of new question',
            'title' : 'New question',
            'answer_style': 0,
            'image': '',
            'video_url': '',
            'rationale_selection_algorithm' : 'prefer_expert_and_highly_voted',
            'grading_scheme' : 0
            }, follow=True)
        self.assertEqual(response.status_code, 403)

        # Step 1, with peerinst.add_question & peerinst.change_question -> 200
        permission = Permission.objects.get(codename='add_question')
        self.validated_teacher.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_question')
        self.validated_teacher.user_permissions.add(permission)

        self.assertTrue(self.validated_teacher.has_perm('peerinst.add_question'))
        self.assertTrue(self.validated_teacher.has_perm('peerinst.change_question'))

        question_count = Question.objects.count()

        response = self.client.get(reverse('question-create'))
        self.assertContains(response, 'Step 1')

        response = self.client.post(reverse('question-create'), {
            'text' : 'Text of new question',
            'title' : 'New question',
            'answer_style': 0,
            'image': '',
            'video_url': '',
            'rationale_selection_algorithm' : 'prefer_expert_and_highly_voted',
            'grading_scheme' : 0
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'peerinst/answer_choice_form.html')
        self.assertEqual(Question.objects.count(), question_count+1)

    def test_question_update(self):
        logged_in = self.client.login(username=self.validated_teacher.username, password=self.validated_teacher.text_pwd)
        self.assertTrue(logged_in)

        # Step 1 (as edit) without ownership --> 403
        response = self.client.get(reverse('question-update', kwargs={ 'pk' : 28 }))
        self.assertEqual(response.status_code, 403)

        # Step 1 (as edit) with ownership and permission --> 200
        permission = Permission.objects.get(codename='change_question')
        self.validated_teacher.user_permissions.add(permission)
        response = self.client.get(reverse('question-update', kwargs={ 'pk' : 32 }))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('question-update', kwargs={ 'pk' : 32 }), {
            'text' : 'Text of new question',
            'title' : 'New question',
            'answer_style': 0,
            'image': '',
            'video_url': '',
            'rationale_selection_algorithm' : 'prefer_expert_and_highly_voted',
            'grading_scheme' : 0,
            'collaborators' : 2
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Question.objects.get(pk=32).collaborators.first(), 2)

        # Step 1 (as edit) as collaborator with permission --> 200
        response = self.client.get(reverse('question-update', kwargs={ 'pk' : 33 }))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('question-update', kwargs={ 'pk' : 33 }), {
            'text' : 'Text of new question',
            'title' : 'New title for question 5',
            'answer_style': 0,
            'image': '',
            'video_url': '',
            'rationale_selection_algorithm' : 'prefer_expert_and_highly_voted',
            'grading_scheme' : 0,
            'collaborators' : 2
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.other_teacher, Question.objects.get(pk=33).collaborators.all())
        self.assertEqual(Question.objects.get(pk=33).title, 'New title for question 5')

    def test_answer_choice_create(self):
        logged_in = self.client.login(username=self.validated_teacher.username, password=self.validated_teacher.text_pwd)
        self.assertTrue(logged_in)

        # db check
        self.assertEqual(Question.objects.count(), 5)

        # Step 2, without ownership -> 403
        response = self.client.get(reverse('answer-choice-form', kwargs={ 'question_id' : 30 }))
        self.assertEqual(response.status_code, 403)

        # Step 2, with ownership but no permission -> 403
        response = self.client.get(reverse('answer-choice-form', kwargs={ 'question_id' : 32 }))
        self.assertEqual(response.status_code, 403)

        # Step 2, with ownership and permission -> 200
        permission = Permission.objects.get(codename='change_question')
        self.validated_teacher.user_permissions.add(permission)
        response = self.client.get(reverse('answer-choice-form', kwargs={ 'question_id' : 32 }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['question'], Question.objects.get(pk=32))
        self.assertContains(response, '<form id="answer-choice-form" method="post">')

        # ... test post (to do but need to send formset in POST) -> 302 to step 3
        #response = self.client.post(reverse('answer-choice-form', kwargs={ 'question_id' : 32 }), {'question' : 32, 'text' : 'Choice 1'}, follow=True)
        #self.assertEqual(response.status_code, 200)

        # Step 2, access if student answer exists -> Message
        q = Question.objects.get(pk=29)
        q.user = self.validated_teacher
        q.save()
        self.assertEqual(self.validated_teacher, Question.objects.get(pk=29).user)

        response = self.client.get(reverse('answer-choice-form', kwargs={ 'question_id' : 29 }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Answer choices cannot be changed if any students have answered this question')
        self.assertNotContains(response, '<form id="answer-choice-form" method="post">')

    def test_sample_answers(self):
        # Step 3, any non-student can post
        logged_in = self.client.login(username=self.guest.username, password=self.guest.text_pwd)
        self.assertTrue(logged_in)

        response = self.client.get(reverse('sample-answer-form', kwargs={ 'question_id' : 29 }))
        self.assertNotContains(response, 'id="add_question_to_assignment"')

        answer_count = Question.objects.get(pk=29).answer_set.filter(user_token__exact='').count()
        response = self.client.post(reverse('sample-answer-form', kwargs={ 'question_id' : 29 }), {
            'first_answer_choice' : 1,
            'rationale' : 'Test sample rationale',
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(answer_count+1, Question.objects.get(pk=29).answer_set.filter(user_token__exact='').count())

        # Step 3, auto-add to an assignment for teacher
        # NB: Question doesn't have to belong to teacher
        self.client.logout()
        logged_in = self.client.login(username=self.validated_teacher.username, password=self.validated_teacher.text_pwd)
        self.assertTrue(logged_in)

        response = self.client.get(reverse('sample-answer-form', kwargs={ 'question_id' : 31 }))
        self.assertContains(response, 'id="add_question_to_assignment"')

        assignment = Assignment.objects.get(pk='Assignment1')
        self.assertNotIn(Question.objects.get(pk=31), assignment.questions.all())
        response = self.client.post(reverse('sample-answer-form-done', kwargs={ 'question_id' : 31 }), {
            'assignments' : 'Assignment1',
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(Question.objects.get(pk=31), assignment.questions.all())

        # Step 3, auto-add to an assignment for different teacher -> Invalid form -> Teacher account page
        self.assertNotIn(Question.objects.get(pk=32), assignment.questions.all())
        response = self.client.post(reverse('sample-answer-form-done', kwargs={ 'question_id' : 32 }), {
            'assignments' : 'Assignment3',
            }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'peerinst/teacher_detail.html')
        self.assertNotIn(Question.objects.get(pk=32), assignment.questions.all())

        # Step 3, not a teacher as post -> 400
        self.client.logout()
        logged_in = self.client.login(username=self.guest.username, password=self.guest.text_pwd)
        self.assertTrue(logged_in)

        response = self.client.post(reverse('sample-answer-form-done', kwargs={ 'question_id' : 32 }), {
            'assignments' : 'Assignment3',
            }, follow=True)
        self.assertEqual(response.status_code, 400)
        self.assertNotIn(Question.objects.get(pk=32), assignment.questions.all())

        # Step 3, any get -> 400
        response = self.client.get(reverse('sample-answer-form-done', kwargs={ 'question_id' : 32 }), follow=True)
        self.assertEqual(response.status_code, 400)

    def test_question_cloning(self):
        logged_in = self.client.login(username=self.validated_teacher.username, password=self.validated_teacher.text_pwd)
        self.assertTrue(logged_in)
        permission = Permission.objects.get(codename='add_question')
        self.validated_teacher.user_permissions.add(permission)
        permission = Permission.objects.get(codename='change_question')
        self.validated_teacher.user_permissions.add(permission)

        # Clone question 33
        question = Question.objects.get(pk=33)
        response = self.client.get(reverse('question-clone', kwargs={ 'pk' : 33 }))
        self.assertContains(response, 'Step 1')
        self.assertContains(response, 'Cloned from')
        self.assertContains(response, question.title)
        self.assertContains(response, question.user.username)

        response = self.client.post(reverse('question-clone', kwargs={ 'pk' : 33 }), {
            'text' : 'Text of cloned question',
            'title' : 'Title for cloned question',
            'answer_style': 0,
            'image': '',
            'video_url': '',
            'rationale_selection_algorithm' : 'prefer_expert_and_highly_voted',
            'grading_scheme' : 0,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'peerinst/answer_choice_form.html')
        self.assertEqual(question, Question.objects.get(pk=33))
        new_question = Question.objects.get(title='Title for cloned question')
        self.assertNotEqual(question.pk, new_question.pk)
        self.assertEqual(self.validated_teacher, new_question.user)
        self.assertEqual(question, new_question.parent)

        # Inherit parent answer choices for initial
        response = self.client.get(reverse('answer-choice-form', kwargs={ 'question_id' : new_question.pk }))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, question.answerchoice_set.all())

    def test_assignment_update_dispatch(self):
        logged_in = self.client.login(username=self.validated_teacher.username, password=self.validated_teacher.text_pwd)
        self.assertTrue(logged_in)

        # Access as teacher, non-owner -> 403
        response = self.client.get(reverse('assignment-update', kwargs={ 'assignment_id' : 'Assignment2' }))
        self.assertEqual(response.status_code, 403)

        # Access as teacher, owner -> 200
        response = self.client.get(reverse('assignment-update', kwargs={ 'assignment_id' : 'Assignment1' }))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['teacher'], self.validated_teacher.teacher)
        self.assertTemplateUsed(response, 'peerinst/assignment_detail.html')

    def test_assignment_update_post(self):
        logged_in = self.client.login(username=self.validated_teacher.username, password=self.validated_teacher.text_pwd)
        self.assertTrue(logged_in)

        # As teacher, post valid form to add question -> 200
        response = self.client.post(reverse('assignment-update', kwargs={ 'assignment_id' : 'Assignment1' }), { 'q' : 31 }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'peerinst/assignment_detail.html')
        self.assertIn(Question.objects.get(pk=31), Assignment.objects.get(pk='Assignment1').questions.all())

        # As teacher, post valid form to remove question -> 200
        response = self.client.post(reverse('assignment-update', kwargs={ 'assignment_id' : 'Assignment1' }), { 'q' : 31 }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'peerinst/assignment_detail.html')
        self.assertNotIn(Question.objects.get(pk=31), Assignment.objects.get(pk='Assignment1').questions.all())

        # As teacher, post invalid form to add question -> 400
        response = self.client.post(reverse('assignment-update', kwargs={ 'assignment_id' : 'Assignment1' }), { 'q' : 3111231 }, follow=True)
        self.assertEqual(response.status_code, 400)

        # As non-logged in user, post valid form to add question -> Login
        self.client.logout()
        response = self.client.post(reverse('assignment-update', kwargs={ 'assignment_id' : 'Assignment1' }), { 'q' : 31 }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertNotIn(Question.objects.get(pk=31), Assignment.objects.get(pk='Assignment1').questions.all())


class StudentTest(TestCase):
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=10)
        self.user.text_pwd = self.user.password
        self.user.password = make_password(self.user.text_pwd)
        self.user.save()

    def test_login_to_web_app(self):
        # Login -> 403 & forced logout
        response = self.client.post(reverse('login'), {'username' : self.user.username, 'password' : self.user.text_pwd}, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')
        response = self.client.post(reverse('assignment-list'))
        self.assertRedirects(response, reverse('login')+'?next=/assignment-list/')

    def test_login_and_answer_question(self):
        pass
