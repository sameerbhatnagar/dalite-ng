from lti import ToolConsumer
from django.conf import settings
from django.shortcuts import render
from peerinst.models import Assignment


def index(request):
    a = Assignment.objects.last()
    q = a.questions.last()
    consumer = ToolConsumer(
        consumer_key=settings.LTI_CLIENT_KEY,
        consumer_secret=settings.LTI_CLIENT_SECRET,
        launch_url=settings.LTI_LAUNCH_URL,
        params={
            "context_id": "test",
            "context_title": "test",
            "custom_assignment_id": a.identifier,
            "custom_question_id": str(q.pk),
            "lis_outcome_service_url": settings.LTI_LAUNCH_URL,
            "lis_result_sourcedid": settings.LTI_LAUNCH_URL,
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "1.0",
            "resource_link_id": settings.LTI_LAUNCH_URL,
            "roles": "Learner",
            "user_id": "test_user123",
        },
    )

    return render(
        request,
        "dalite_lti/index.html",
        {
            "launch_data": consumer.generate_launch_data(),
            "launch_url": consumer.launch_url,
        },
    )
